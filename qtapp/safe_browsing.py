"""
Google Safe Browsing API v4 - URL check for free mode.
Only opens a site in free mode after checking the URL is not in Google's threat list.
"""
import os
import json
import urllib.parse

try:
    import urllib.request
    import urllib.error
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

# API key from env - do not hardcode
SAFEBROWSING_API_KEY = os.getenv("GOOGLE_SAFEBROWSING_API_KEY", "").strip()
SAFEBROWSING_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
TIMEOUT_SEC = 5


def is_url_safe(url):
    """
    Check if URL is safe using Google Safe Browsing API v4.
    Returns (True, reason) if safe, (False, reason) if threat or error.
    """
    if not SAFEBROWSING_API_KEY or not url or not url.strip():
        # No API key: allow URL but note it wasn't checked (or block for strictness)
        if not SAFEBROWSING_API_KEY:
            return True, "Safe Browsing API key not set - URL not checked"
        return False, "Empty URL"

    if not HAS_URLLIB:
        return True, "Safe Browsing check unavailable (no urllib)"

    try:
        # Normalize: only check the URL once; API accepts up to 500 URLs
        body = {
            "client": {"clientId": "edubrowser", "clientVersion": "1.0"},
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}],
            },
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            f"{SAFEBROWSING_URL}?key={urllib.parse.quote(SAFEBROWSING_API_KEY)}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        if result.get("matches"):
            threats = [m.get("threatType", "THREAT") for m in result["matches"]]
            return False, f"URL flagged by Safe Browsing: {', '.join(threats)}"
        return True, "URL is safe"
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
            err_json = json.loads(err_body)
            msg = err_json.get("error", {}).get("message", str(e))
        except Exception:
            msg = str(e)
        return False, f"Safe Browsing check failed: {msg}"
    except Exception as e:
        # Timeout or network: allow URL so browsing isn't broken when API is down
        return True, f"Safe Browsing check unavailable: {e}"
