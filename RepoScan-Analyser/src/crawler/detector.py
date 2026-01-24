"""
AJAX Detector - Wraps RepoScan parser for dynamic content
"""
import sys
import os

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.parser import Parser

class DynamicDetector:
    def __init__(self):
        self.parser = Parser()
        
    def detect(self, assets_content):
        """
        Analyze fetched assets for AJAX patterns.
        assets_content: List of dicts {'url', 'type', 'content'}
        Returns: List of CodeSnippet objects (only AJAX ones)
        """
        all_ajax_findings = []
        
        for asset in assets_content:
            url = asset['url']
            content = asset['content']
            
            # Parse the content using RepoScan's main parser
            # This handles script extraction, HTML parsing, AND calls ajax_detector internally
            findings = self.parser.parse(url, content)
            
            # Filter for AJAX findings only
            ajax_findings = [f for f in findings if f.ajax_detected]
            all_ajax_findings.extend(ajax_findings)
            
        print(f"Detected {len(all_ajax_findings)} AJAX calls in fetched assets.")
        return all_ajax_findings
