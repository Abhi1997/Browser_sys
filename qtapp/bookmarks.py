# Personal bookmarks storage (per user, local JSON).
# Only the current user can see their own bookmarks.
import os
import json
from datetime import datetime
try:
    from authentication import Authentication
except ImportError:
    from .authentication import Authentication


def _bookmarks_dir():
    """Directory for bookmarks file (same parent as cache)."""
    base = Authentication.get_cache_base_dir()
    parent = os.path.dirname(base)
    return parent


def _bookmarks_path(user_id):
    """Path to JSON file for this user's bookmarks."""
    return os.path.join(_bookmarks_dir(), f"bookmarks_{user_id}.json")


def load_bookmarks(user_id):
    """Load list of bookmarks for user. Returns list of {url, title, added_at}."""
    path = _bookmarks_path(user_id)
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_bookmarks(user_id, bookmarks):
    """Save list of bookmarks for user."""
    path = _bookmarks_path(user_id)
    try:
        dirpath = os.path.dirname(path)
        os.makedirs(dirpath, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(bookmarks, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def add_bookmark(user_id, url, title=None):
    """Add one bookmark. Returns True if added."""
    if not url or not url.strip():
        return False
    bookmarks = load_bookmarks(user_id)
    url = url.strip()[:2048]
    title = (title or url)[:512]
    # Avoid duplicate URL
    for b in bookmarks:
        if (b.get("url") or "").strip() == url:
            b["title"] = title
            b["added_at"] = datetime.now().isoformat()
            return save_bookmarks(user_id, bookmarks)
    bookmarks.insert(0, {"url": url, "title": title, "added_at": datetime.now().isoformat()})
    return save_bookmarks(user_id, bookmarks)


def remove_bookmark(user_id, url):
    """Remove bookmark by URL. Returns True if removed."""
    bookmarks = load_bookmarks(user_id)
    url = (url or "").strip()
    new_list = [b for b in bookmarks if (b.get("url") or "").strip() != url]
    if len(new_list) == len(bookmarks):
        return False
    return save_bookmarks(user_id, new_list)
