# Personal bookmarks storage (per user, database backed).
# Students see their own; teachers/admins can monitor via API.
import os
from datetime import datetime
try:
    from authentication import Authentication
except ImportError:
    from .authentication import Authentication


def load_bookmarks(user_id, auth_instance=None):
    """Load list of bookmarks for user from database. Returns list of {url, title, added_at}."""
    if not auth_instance:
        auth_instance = Authentication()
    return auth_instance.get_bookmarks_from_db(user_id)


def save_bookmarks(user_id, bookmarks, auth_instance=None):
    """
    Save list of bookmarks for user. 
    Note: For database-backed storage, we typically use add_bookmark/remove_bookmark.
    This method is kept for structural compatibility but now just returns True.
    """
    return True


def add_bookmark(user_id, url, title=None, auth_instance=None):
    """Add one bookmark to the database. Returns True if added."""
    if not url or not url.strip():
        return False
    if not auth_instance:
        auth_instance = Authentication()
    return auth_instance.add_bookmark_to_db(user_id, url, title)


def remove_bookmark(user_id, url, auth_instance=None):
    """Remove bookmark by URL from database. Returns True if removed."""
    if not auth_instance:
        auth_instance = Authentication()
    return auth_instance.remove_bookmark_from_db(user_id, url)
