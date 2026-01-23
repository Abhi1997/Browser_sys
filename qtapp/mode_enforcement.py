"""
Browser Mode Enforcement Engine
Enforces Exam, Study, Restricted, and Free modes with URL filtering
"""

import re
from urllib.parse import urlparse
from datetime import datetime
from authentication import Authentication

class ModeEnforcement:
    MODES = {
        "exam": {
            "name": "Exam Mode",
            "color": "#dc2626",  # Red
            "icon": "🔒",
            "description": "Strictest mode - only whitelisted educational sites allowed"
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
        }
    }
    
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
        
        # Free mode allows everything (but still logged)
        if mode == "free":
            return True, "Free mode - all URLs allowed"
        
        # Check blacklist first (most restrictive)
        if self._is_blacklisted(domain, mode):
            if student_id:
                self._log_violation(student_id, url, mode, "url_blocked", 
                                  f"URL blocked: {domain} is in blacklist")
            return False, f"Blocked: {domain} is in blacklist for {mode} mode"
        
        # Check whitelist
        if mode in ("exam", "study", "restricted"):
            if not self._is_whitelisted(domain, mode):
                if student_id:
                    self._log_violation(student_id, url, mode, "url_blocked",
                                      f"URL not whitelisted: {domain} not allowed in {mode} mode")
                return False, f"Not allowed: {domain} is not whitelisted for {mode} mode"
        
        return True, "URL allowed"
    
    def _is_whitelisted(self, domain, mode):
        """Check if domain is whitelisted for the mode"""
        try:
            conn = self.auth._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM WhitelistDomains 
                WHERE domain=%s AND mode=%s AND is_active=1
            """, (domain, mode))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result is not None
        except Exception as e:
            print(f"Error checking whitelist: {e}")
            return False
    
    def _is_blacklisted(self, domain, mode):
        """Check if domain is blacklisted for the mode"""
        try:
            conn = self.auth._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM BlacklistDomains 
                WHERE domain=%s AND mode=%s AND is_active=1
            """, (domain, mode))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result is not None
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
            if mode == "exam":
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
        """Check if violations need escalation"""
        try:
            conn = self.auth._get_conn()
            cursor = conn.cursor()
            
            # Count recent violations (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM Violations
                WHERE student_id=%s AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            """, (student_id,))
            count = cursor.fetchone()[0]
            
            if count >= 5:
                # Escalate to admin
                cursor.execute("""
                    INSERT INTO WarningTriggers (student_id, user_id, warning_type,
                                               violation_count, last_violation_at,
                                               escalated_to, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    violation_count=%s, last_violation_at=%s
                """, (student_id, user_id, "repeated_violation", count, datetime.now(),
                      "admin", datetime.now(), count, datetime.now()))
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

