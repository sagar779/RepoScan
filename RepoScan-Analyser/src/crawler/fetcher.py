"""
Asset Fetcher - Downloads content for analysis
"""
import requests
from . import config

class Fetcher:
    def __init__(self, session=None):
        self.session = session or requests.Session()
        
    def fetch_assets(self, assets):
        """
        Fetch content for a list of (url, type) tuples.
        Returns list of dicts: {'url': ..., 'type': ..., 'content': ...}
        """
        results = []
        for url, asset_type in assets:
            print(f"Fetching asset: {url}")
            try:
                response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
                if response.status_code == 200:
                    results.append({
                        'url': url,
                        'type': asset_type,
                        'content': response.text
                    })
            except Exception as e:
                print(f"  Failed to fetch {url}: {e}")
        return results
