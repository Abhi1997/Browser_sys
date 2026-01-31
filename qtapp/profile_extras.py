# Local profile extras (phone, etc.) - not in DB, per user.
# Simple JSON file so no migration needed.
import os
import json

try:
    from authentication import Authentication
except ImportError:
    from .authentication import Authentication


def _extras_dir():
    base = Authentication.get_cache_base_dir()
    return os.path.dirname(base)


def _extras_path(user_id):
    return os.path.join(_extras_dir(), f"profile_{user_id}.json")


def load_profile_extras(user_id):
    """Load { phone, ... } for user. Returns dict."""
    path = _extras_path(user_id)
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_profile_extras(user_id, data):
    """Save profile extras for user. Returns True on success."""
    path = _extras_path(user_id)
    try:
        dirpath = os.path.dirname(path)
        os.makedirs(dirpath, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False
