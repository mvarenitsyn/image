"""
Configuration file for Google Images Search API

This module reads configuration from environment variables:
- GOOGLE_API_KEY: Your Google API developer key
- GOOGLE_CSE_ID: Your Custom Search Engine ID

If environment variables are not set, fallback to default values.
"""

import os

# Read Google API developer key from environment variables
# Get it from: https://console.developers.google.com/apis/credentials
DEVELOPER_KEY = os.environ.get("GOOGLE_API_KEY", "")

# Read Google Custom Search Engine ID from environment variables
# Get it from: https://cse.google.com/cse/all
CX = os.environ.get("GOOGLE_CSE_ID", "")
