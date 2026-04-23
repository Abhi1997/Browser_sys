"""
Browser Mode Enforcement Engine
Enforces Cached (offline-only), Study, Restricted, and Free modes with URL filtering
"""

import re
from urllib.parse import urlparse
from datetime import datetime
from authentication import Authentication

class ModeEnforcement:
    MODES = {
        "cached": {
            "name": "Cached Mode",
            "color": "#7c3aed",  # Violet
            "icon": "📁",
            "description": "Offline only - only pre-cached sites can be viewed; no network. Cache managed by teachers/admins."
        },
        "study": {
            "name": "Study Mode",
            "color": "#2563eb",  # Blue
            "icon": "📚",
            "description": "Educational and research sites allowed"
        },
        "restricted": {
            "name": "Restricted Mode",
            "color": "#f59e0b",  # Amber
            "icon": "⚠️",
            "description": "Limited browsing with content filtering"
        },
        "free": {
            "name": "Free Mode",
            "color": "#10b981",  # Green
            "icon": "🌐",
            "description": "Unrestricted browsing (monitored)"
        },
        "exam": {
            "name": "Exam Mode",
            "color": "#ef4444",  # Red
            "icon": "📝",
            "description": "Strict exam environment - only a single site is allowed"
        }
    }
    
    # Common domains used for authentication/login that shouldn't be fully whitelisted
    # but need to be reachable during an OAuth/SAML flow.
    TRUSTED_AUTH_DOMAINS = [
        "instructure.com",      # Canvas
        "canvaslms.com",        # Canvas
        "okta.com",             # SSO
        "onelogin.com",         # SSO
        "microsoftonline.com",  # Microsoft/Outlook SSO
        "accounts.google.com",  # Google SSO
        "shibboleth",           # Common academic SSO
        "duosecurity.com",      # MFA
    ]
    
    def __init__(self, auth: Authentication):
        self.auth = auth
    
    def get_mode_info(self, mode):
        """Get mode information"""
        return self.MODES.get(mode, self.MODES["restricted"])
    
    def is_url_allowed(self, url, mode, student_id=None):
        """
        Check if URL is allowed in the given mode
        
        Args:
            url: URL to check
            mode: Current browser mode
            student_id: Student ID (optional, for logging)
        
        Returns:
            (is_allowed: bool, reason: str)
        """
        if not url or not url.strip():
            return False, "Empty URL"
        
        # Normalize URL
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if not domain:
                return False, "Invalid URL format"
        except Exception:
            return False, "Invalid URL format"
        
        # Time window: if student has active TimeWindows, allow only within allowed times
        if student_id and self._outside_time_window(student_id):
            if student_id:
                self._log_violation(student_id, url, mode, "time_window_violation",
                                    "Access attempted outside allowed time window")
            return False, "Access not allowed outside your scheduled time window"

        # Free mode: allow only after Google Safe Browsing check (if API key set)
        if mode == "free":
            try:
                from safe_browsing import is_url_safe
                safe, reason = is_url_safe(url)
                if not safe and student_id:
                    self._log_violation(student_id, url, mode, "url_blocked", reason)
                return safe, reason if not safe else "Free mode - URL checked and allowed"
            except Exception as e:
                # If safe_browsing module fails, allow URL to avoid breaking browsing
                return True, f"Free mode - Safe Browsing check skipped: {e}"
        
        # Check blacklist first (most restrictive) - filter by student's admin_id
        if self._is_blacklisted(url, domain, mode, student_id):
            if student_id:
                self._log_violation(student_id, url, mode, "url_blocked", 
                                  f"URL blocked: {domain} is in blacklist")
            return False, f"Blocked: {domain} is in blacklist for {mode} mode"
        
        # Cached mode: only URLs that are in CachedSites (offline cache); no network
        if mode == "cached":
            path = self.auth.get_cached_site_path(url)
            if not path:
                if student_id:
                    self._log_violation(student_id, url, mode, "url_blocked",
                                        "URL not in offline cache; only cached sites allowed in cached mode")
                return False, "Only cached offline sites can be viewed in Cached mode. No network."
            return True, "Cached - load from offline"

        # Check whitelist for study/restricted/exam - filter by student's admin_id
        if mode in ("study", "restricted", "exam"):
            if not self._is_whitelisted(url, domain, mode, student_id):
                # Special case for Exam Mode: Allow login redirects if they point back to a whitelisted site
                if mode == "exam" and self._is_auth_redirect(url, domain, mode, student_id):
                    return True, "Allowed: Secure authentication flow redirect"
                    
                if student_id:
                    self._log_violation(student_id, url, mode, "url_blocked",
                                      f"URL not whitelisted: {domain} not allowed in {mode} mode")
                return False, f"Not allowed: {domain} is not whitelisted for {mode} mode"
        
        return True, "URL allowed"
    def _matches_rule(self, url_lower, domain_lower, rule):
        rule = rule.strip()
        if not rule:
            return False
            
        if rule.startswith('http://'):
            rule = rule[7:]
        if rule.startswith('https://'):
            rule = rule[8:]
            
        if '/' in rule:
            rule_parts = rule.split('/', 1)
            rule_domain = rule_parts[0]
            rule_path = '/' + rule_parts[1]
        else:
            rule_domain = rule
            rule_path = ""
            
        domain_match = False
        
        # Handle wildcard rules like *.domain.com
        if '*' in rule_domain:
            # Convert wildcard rule to regex: *.instructure.com -> ^.*\.instructure\.com$
            # and allow for the domain itself: instructure.com
            import re
            pattern = re.escape(rule_domain).replace('\\*', '.*')
            if re.match(f"^{pattern}$", domain_lower):
                domain_match = True
            # Also check if it matches without the wildcard prefix (e.g. google.com matches *.google.com)
            bare_rule = rule_domain.replace('*.', '').replace('*', '')
            if domain_lower == bare_rule:
                domain_match = True
        elif domain_lower == rule_domain or domain_lower.endswith('.' + rule_domain):
            domain_match = True
        elif rule_domain and rule_domain in domain_lower:
            # Fallback for partial matches (keep for backward compatibility)
            domain_match = True
            
        if domain_match:
            if rule_path:
                from urllib.parse import urlparse
                try:
                    parsed_path = urlparse(url_lower).path
                    if parsed_path.startswith(rule_path):
                        return True
                except Exception:
                    pass
            else:
                return True
        return False
                
    def _is_auth_redirect(self, url, domain, mode, student_id):
        """
        Detects if a non-whitelisted URL is part of a secure login flow.
        Identifies auth providers and verifies they are redirecting back to a whitelisted exam site.
        """
        domain_lower = domain.lower()
        
        # 1. Is it a known auth provider?
        is_trusted_provider = any(trusted in domain_lower for trusted in self.TRUSTED_AUTH_DOMAINS)
        
        # 2. Does it look like an auth path? (oauth, login, saml, etc.)
        auth_patterns = ['/auth', '/login', '/saml', '/sso', '/authorize', '/callback']
        url_lower = url.lower()
        has_auth_path = any(pattern in url_lower for pattern in auth_patterns)
        
        if not (is_trusted_provider or has_auth_path):
            return False
            
        # 3. CRITICAL: Does it point back to a whitelisted URL for this student?
        from urllib.parse import parse_qs, urlparse
        try:
            parsed_params = parse_qs(urlparse(url).query)
            # Common redirect parameters
            redirect_keys = ['redirect_uri', 'target_domain', 'state', 'continue', 'return_to']
            
            for key in redirect_keys:
                if key in parsed_params:
                    for val in parsed_params[key]:
                        # Check if the redirect target is whitelisted
                        target_parsed = urlparse(val)
                        target_domain = target_parsed.netloc.lower()
                        if target_domain and self._is_whitelisted(val, target_domain, mode, student_id):
                            return True
        except Exception as e:
            print(f"Error parsing auth redirect: {e}")
            
        return False

    def _is_whitelisted(self, url, domain, mode, student_id=None):
        """Check if domain or URL is whitelisted for the mode (filtered by admin_id if student has one)"""
        try:
            conn = self.auth._get_conn()
            cursor = conn.cursor()
            
            # Get admin_id for student if provided
            admin_id = None
            if student_id:
                cursor.execute("SELECT admin_id FROM Students WHERE student_id=%s", (student_id,))
                row = cursor.fetchone()
                admin_id = row[0] if row else None
            
            # Filter by admin_id if student has one, otherwise global whitelist
            if admin_id:
                cursor.execute("""
                    SELECT domain FROM WhitelistDomains 
                    WHERE mode=%s AND is_active=1 AND (admin_id=%s OR admin_id IS NULL)
                """, (mode, admin_id))
            else:
                cursor.execute("""
                    SELECT domain FROM WhitelistDomains 
                    WHERE mode=%s AND is_active=1
                """, (mode,))
            
            rules = [row[0].lower() for row in cursor.fetchall() if row and row[0]]
            cursor.close()
            conn.close()
            
            domain_lower = domain.lower()
            url_lower = url.lower()
            for rule in rules:
                if self._matches_rule(url_lower, domain_lower, rule):
                    return True
            return False
        except Exception as e:
            print(f"Error checking whitelist: {e}")
            return False
    
    def _outside_time_window(self, student_id):
        """True if student has active time windows and current time is outside all of them."""
        try:
            conn = self.auth._get_conn()
            cursor = conn.cursor()
            from datetime import datetime as dt, timedelta
            now = dt.now()
            weekday = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][now.weekday()]
            now_secs = now.hour * 3600 + now.minute * 60 + now.second

            cursor.execute("""
                SELECT start_time, end_time FROM TimeWindows
                WHERE student_id=%s AND is_active=1
                  AND (day_of_week=%s OR day_of_week='all')
            """, (student_id, weekday))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            if not rows:
                return False  # No windows = always allowed
            for (start_time, end_time) in rows:
                # MySQL may return TIME as timedelta (seconds since midnight) or time
                def to_secs(t):
                    if t is None:
                        return 0
                    if hasattr(t, 'total_seconds'):
                        return int(t.total_seconds()) % (24 * 3600)
                    if hasattr(t, 'hour'):
                        return t.hour * 3600 + t.minute * 60 + t.second
                    return 0
                s, e = to_secs(start_time), to_secs(end_time)
                if s <= now_secs <= e:
                    return False  # Inside a window
            return True  # Outside all windows
        except Exception as e:
            print(f"Error checking time window: {e}")
            return False

    def _is_blacklisted(self, url, domain, mode, student_id=None):
        """Check if domain or URL is blacklisted for the mode (filtered by admin_id if student has one)"""
        try:
            conn = self.auth._get_conn()
            cursor = conn.cursor()
            
            # Get admin_id for student if provided
            admin_id = None
            if student_id:
                cursor.execute("SELECT admin_id FROM Students WHERE student_id=%s", (student_id,))
                row = cursor.fetchone()
                admin_id = row[0] if row else None
            
            # Filter by admin_id if student has one, otherwise global blacklist
            if admin_id:
                cursor.execute("""
                    SELECT domain FROM BlacklistDomains 
                    WHERE mode=%s AND is_active=1 AND (admin_id=%s OR admin_id IS NULL)
                """, (mode, admin_id))
            else:
                cursor.execute("""
                    SELECT domain FROM BlacklistDomains 
                    WHERE mode=%s AND is_active=1
                """, (mode,))
            
            rules = [row[0].lower() for row in cursor.fetchall() if row and row[0]]
            cursor.close()
            conn.close()

            domain_lower = domain.lower()
            url_lower = url.lower()
            for rule in rules:
                if self._matches_rule(url_lower, domain_lower, rule):
                    return True
            return False
        except Exception as e:
            print(f"Error checking blacklist: {e}")
            return False
    
    def _log_violation(self, student_id, url, mode, violation_type, description):
        """Log a violation to the activity database"""
        try:
            # Get user_id from student_id
            conn = self.auth._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM Students WHERE student_id=%s", (student_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not result:
                return
            
            user_id = result[0]
            device_info = self.auth.get_device_info()
            
            # Determine severity
            severity = "medium"
            if mode == "cached":
                severity = "high"
            elif violation_type == "mode_bypass_attempt":
                severity = "critical"
            
            conn = self.auth._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Violations (student_id, user_id, violation_type, description,
                                      attempted_url, current_mode, device_id, ip_address,
                                      mac_address, severity, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (student_id, user_id, violation_type, description, url, mode,
                  device_info["device_id"], device_info["ip_address"],
                  device_info["mac_address"], severity, datetime.now()))
            conn.commit()
            
            # Update violation count
            cursor.execute("""
                UPDATE Students SET violation_count = violation_count + 1
                WHERE student_id=%s
            """, (student_id,))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            # Check for escalation
            self._check_escalation(student_id, user_id)
            
        except Exception as e:
            print(f"Error logging violation: {e}")
    
    def _check_escalation(self, student_id, user_id):
        """Record violations with warning triggers: first_violation, repeated_violation, critical."""
        try:
            conn = self.auth._get_conn()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) FROM Violations
                WHERE student_id=%s AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            """, (student_id,))
            count = cursor.fetchone()[0]

            now = datetime.now()
            # First violation: always record a warning trigger for visibility
            if count == 1:
                cursor.execute("""
                    INSERT INTO WarningTriggers (student_id, user_id, warning_type,
                                               violation_count, last_violation_at,
                                               escalated_to, created_at)
                    VALUES (%s, %s, 'first_violation', 1, %s, 'teacher', %s)
                """, (student_id, user_id, now, now))
                conn.commit()
            elif count >= 5:
                cursor.execute("""
                    INSERT INTO WarningTriggers (student_id, user_id, warning_type,
                                               violation_count, last_violation_at,
                                               escalated_to, created_at)
                    VALUES (%s, %s, 'repeated_violation', %s, %s, 'admin', %s)
                """, (student_id, user_id, count, now, now))
                conn.commit()

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error checking escalation: {e}")
    
    def log_activity(self, student_id, user_id, url, mode, duration=0):
        """Log student browsing activity"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            device_info = self.auth.get_device_info()
            
            conn = self.auth._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ActivityLogs (student_id, user_id, url, domain, mode,
                                        visit_duration, visit_start, visit_end,
                                        device_id, ip_address, mac_address, is_allowed, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (student_id, user_id, url, domain, mode, duration,
                  datetime.now(), datetime.now(), device_info["device_id"],
                  device_info["ip_address"], device_info["mac_address"], 1, datetime.now()))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error logging activity: {e}")

