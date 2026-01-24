"""
AJAX Crawler - Discovers pages and assets
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from . import config

class Crawler:
    def __init__(self, base_url, cookies=None, headers=None):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.USER_AGENT})
        if headers:
            self.session.headers.update(headers)
        if cookies:
            self.session.cookies.update(cookies)
            
        self.visited = set()
        self.assets_to_scan = set() # Set of (url, type) tuples
        self.external_assets = [] # List of {'url', 'type', 'source_page'}

    def is_internal(self, url):
        return urlparse(url).netloc == self.domain

    def crawl(self, url=None, depth=0):
        if url is None:
            url = self.base_url
            
        if depth > config.MAX_DEPTH or url in self.visited:
            return
            
        self.visited.add(url)
        print(f"Crawling: {url}")
        
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            if response.status_code != 200:
                print(f"  Failed: {response.status_code}")
                return
                
            content_type = response.headers.get('content-type', '').lower()
            
            # If it's HTML, parse for links and scripts
            if 'text/html' in content_type:
                # Add this page itself as an asset to scan
                self.assets_to_scan.add((url, 'html'))
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 1. Discover Links (for crawling)
                for a in soup.find_all('a', href=True):
                    next_url = urljoin(url, a['href']).split('#')[0]
                    if self.is_internal(next_url) and next_url not in self.visited:
                        # Simple extension filter to avoid crawling binary files
                        if not any(next_url.lower().endswith(ext) for ext in config.SKIP_EXTENSIONS):
                            time.sleep(config.DELAY_BETWEEN_REQUESTS)
                            self.crawl(next_url, depth + 1)
                            
                # 2. Discover Scripts
                for script in soup.find_all('script', src=True):
                    script_url = urljoin(url, script['src'])
                    if self.is_internal(script_url):
                         self.assets_to_scan.add((script_url, 'js'))
                    else:
                         self.external_assets.append({'url': script_url, 'type': 'Script', 'source_page': url})

                # 3. Discover CSS
                for link in soup.find_all('link', rel='stylesheet'):
                    href = link.get('href')
                    if href:
                        css_url = urljoin(url, href)
                        if self.is_internal(css_url):
                            # Optional: Scan CSS for images/fonts? For now just track existence
                            pass 
                        else:
                            self.external_assets.append({'url': css_url, 'type': 'Stylesheet', 'source_page': url})

        except Exception as e:
            print(f"  Error crawling {url}: {e}")

    def get_assets(self):
        """Returns list of unique URLs to scan for AJAX"""
        return list(self.assets_to_scan)
        
    def get_external_assets(self):
        return self.external_assets
