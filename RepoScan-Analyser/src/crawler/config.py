"""
Configuration settings for AJAX Crawler utility
"""
import os

# Crawler settings
MAX_DEPTH = 5
REQUEST_TIMEOUT = 10
DELAY_BETWEEN_REQUESTS = 0.5  # seconds
USER_AGENT = "RepoScan-AJAX-Crawler/1.0"

# Output settings
TEMP_DIR = "temp_crawl_assets"

# Supported file extensions for analysis (downloading)
INTERESTING_EXTENSIONS = ['.js', '.html', '.htm', '.aspx', '.php', '.jsp']
SKIP_EXTENSIONS = ['.css', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.ttf', '.pdf']
