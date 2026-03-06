import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import authentication and bookmarks
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from authentication import Authentication
import bookmarks

def test_bookmarks():
    load_dotenv()
    auth = Authentication()
    
    # Test user ID (assuming 1 exists, or we use a high number for testing)
    test_user_id = 1 
    test_url = "https://example.com/test-bookmark"
    test_title = "Test Bookmark Title"
    
    print(f"Testing bookmark addition for user {test_user_id}...")
    success = bookmarks.add_bookmark(test_user_id, test_url, test_title, auth_instance=auth)
    if success:
        print("Success: Bookmark added.")
    else:
        print("Error: Failed to add bookmark.")
        return

    print("Testing bookmark retrieval...")
    items = bookmarks.load_bookmarks(test_user_id, auth_instance=auth)
    found = False
    for item in items:
        if item['url'] == test_url:
            print(f"Success: Found bookmark with title '{item['title']}'")
            found = True
            break
    if not found:
        print("Error: Bookmark not found in retrieval.")
        return

    print("Testing bookmark removal...")
    removed = bookmarks.remove_bookmark(test_user_id, test_url, auth_instance=auth)
    if removed:
        print("Success: Bookmark removed.")
    else:
        print("Error: Failed to remove bookmark.")

if __name__ == "__main__":
    test_bookmarks()
