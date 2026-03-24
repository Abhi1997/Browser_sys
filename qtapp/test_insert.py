import os
import sys
from dotenv import load_dotenv
load_dotenv()
from authentication import Authentication

auth = Authentication()
try:
    print(f"Connecting to {auth.database}...")
    auth.add_browsing_history(1, "https://example.com", "Example", "device_123")
    print("Add browsing history did not throw an exception")
except Exception as e:
    print(f"Caught exception: {e}")
