import os
import collections
import re
import concurrent.futures


class Scanner:
    def __init__(self, target_dir):
        self.target_dir = os.path.abspath(target_dir)
        self.file_inventory = []
        self.directory_stats = collections.defaultdict(lambda: {'count': 0, 'lines': 0})
        
        # Folders to exclude (dependencies, build outputs, version control)
        # Folders to exclude (dependencies, build outputs, version control)
        self.excluded_folders = {
            'node_modules', 'vendor', 'packages', '.git', '.svn', '.hg',
            'bin', 'obj', 'dist', 'build', 'out', 'target',
            '__pycache__', '.pytest_cache', '.venv', 'venv', 'env'
        }
        
        # Compile Regex Patterns - Matching main utility's comprehensive detection
        self.patterns = {
            # 1. CSS Patterns
            'inline_css': re.compile(r'style\s*=\s*["\'][^"\']*["\']', re.IGNORECASE),
            'internal_style_blocks': re.compile(r'<style\b[^>]*>[\s\S]*?</style>', re.IGNORECASE),
            'external_stylesheet_links': re.compile(
                r'<link\b[^>]*rel\s*=\s*["\']stylesheet["\'][^>]*>', re.IGNORECASE
            ),

            # 2. JS Patterns
            'inline_js': re.compile(
                r'(\bon\w+\s*=\s*["\'][^"\']*["\']|href=["\']\s*javascript:)', 
                re.IGNORECASE
            ),
            'internal_script_blocks': re.compile(
                r'<script\b(?![^>]*\bsrc=)[^>]*>[\s\S]*?</script>', re.IGNORECASE
            ),
            'external_script_tags': re.compile(
                r'<script\b[^>]*src\s*=\s*["\'][^"\']+["\'][^>]*>', re.IGNORECASE
            ),

            # 3. AJAX / Network Calls
            'ajax_call': re.compile(
                r'(\bfetch\s*\(|'
                r'new\s+XMLHttpRequest\s*\(|'
                r'(?:\$|jQuery|axios|superagent|http)\s*\.\s*(?:ajax|get|post|getJSON|getScript|load|request)\s*\(|'
                r'\.open\s*\(\s*["\'](?:GET|POST|PUT|DELETE|PATCH)["\']|'
                r'\bonreadystatechange\s*=|'
                r'\.send\s*\(|'
                r'\baxios(?:\.\w+)?\s*\(|'
                r'new\s+WebSocket\s*\(|'
                r'new\s+EventSource\s*\()',
                re.IGNORECASE
            ),

            # 4. JS Loading CSS or JS (Dynamic)
            'dynamic_js': re.compile(
                r'(\.src\s*=\s*["\'][^"\']+\.js["\']|'
                r'document\.createElement\s*\(\s*["\']script["\']\s*\)|'
                r'\.appendChild\s*\(|'
                r'\.insertBefore\s*\(|'
                r'eval\s*\(|'
                r'new\s+Function\s*\(|'
                r'setTimeout\s*\(|'
                r'setInterval\s*\(|'
                r'import\s*\(|'
                r'System\.import\s*\(|'
                r'require\s*\(|'
                r'innerHTML\s*=|'
                r'outerHTML\s*=|'
                r'insertAdjacentHTML\s*\(|'
                r'document\.write\s*\()',
                re.IGNORECASE
            ),
            'dynamic_css': re.compile(
                r'(\.src\s*=\s*["\'][^"\']+\.css["\']|'
                r'document\.createElement\s*\(\s*["\']style["\']\s*\)|'
                r'document\.createElement\s*\(\s*["\']link["\']\s*\)|'
                r'\.rel\s*=\s*["\']stylesheet["\']|'
                r'\.href\s*=\s*["\'][^"\']+\.css["\']|'
                r'\.style\.\w+\s*=|'
                r'\.style\[\s*["\'][^"\']+["\']\s*\]\s*=|'
                r'setProperty\s*\(|'
                r'insertRule\s*\(|'
                r'addRule\s*\(|'
                r'new\s+CSSStyleSheet\s*\(|'
                r'adoptedStyleSheets)',
                re.IGNORECASE
            )
        }

    def count_lines_and_analyze(self, filepath):
        """Counts lines and scans for complexity metrics."""
        metrics = {
            'lines': 0,
            'inline_css': 0, 'internal_style_blocks': 0, 'external_stylesheet_links': 0,
            'inline_js': 0, 'internal_script_blocks': 0, 'external_script_tags': 0,
            'ajax_calls': 0, 'has_ajax_calls': 'No', 'dynamic_js': 0, 'dynamic_css': 0
        }
        
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()
        
        # Relevant Extensions for Client-Side Code
        web_exts = {'.html', '.htm', '.aspx', '.ascx', '.cshtml', '.master', '.php', '.jsp', '.js', '.ts', '.vue', '.jsx', '.tsx'}
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                metrics['lines'] = len(content.splitlines())
                
                # Only analyze web-related files for Client-Side patterns
                if ext in web_exts:
                    # Run Regex Analysis
                    metrics['inline_css'] = len(self.patterns['inline_css'].findall(content))
                    metrics['internal_style_blocks'] = len(self.patterns['internal_style_blocks'].findall(content))
                    metrics['external_stylesheet_links'] = len(self.patterns['external_stylesheet_links'].findall(content))
                    metrics['inline_js'] = len(self.patterns['inline_js'].findall(content))
                    metrics['internal_script_blocks'] = len(self.patterns['internal_script_blocks'].findall(content))
                    metrics['external_script_tags'] = len(self.patterns['external_script_tags'].findall(content))
                    metrics['ajax_calls'] = len(self.patterns['ajax_call'].findall(content))
                    metrics['has_ajax_calls'] = "Yes" if metrics['ajax_calls'] > 0 else "No"
                    metrics['dynamic_js'] = len(self.patterns['dynamic_js'].findall(content))
                    metrics['dynamic_css'] = len(self.patterns['dynamic_css'].findall(content))
                
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            
        return metrics

    def process_file(self, root, file):
        """Worker function to process a single file."""
        file_path = os.path.join(root, file)
        size_kb = os.path.getsize(file_path) / 1024
        
        # Get extension
        _, ext = os.path.splitext(file)
        if not ext:
            ext = "(No Extension)"
        else:
            ext = ext.lower()
            
        # Analyze File
        metrics = self.count_lines_and_analyze(file_path)
        
        return {
            'root': root,
            'file': file,
            'ext': ext,
            'size_kb': size_kb,
            'metrics': metrics,
            'file_path': file_path
        }

    def scan(self):
        """Walks the directory and collects metadata."""
        print(f"Scanning directory: {self.target_dir}")
        # Collect all files to scan
        all_files = []
        for root, dirs, files in os.walk(self.target_dir):
            # Filter out excluded directories (modifies dirs in-place)
            dirs[:] = [d for d in dirs if d not in self.excluded_folders]
            
            for file in files:
                all_files.append((root, file))
                
        # Use ThreadPoolExecutor for concurrent scanning
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_file = {executor.submit(self.process_file, r, f): (r, f) for r, f in all_files}
            for future in concurrent.futures.as_completed(future_to_file):
                try:
                    data = future.result()
                    results.append(data)
                except Exception as exc:
                    print(f"File generated an exception: {exc}")

        # Aggregate Results
        for item in results:
            root = item['root']
            rel_dir = os.path.relpath(root, self.target_dir)
            if rel_dir == '.': rel_dir = '(Root)'
            depth = 0 if rel_dir == '(Root)' else rel_dir.count(os.sep) + 1
            
            # Update Inventory
            self.file_inventory.append({
                'Directory': rel_dir,
                'Filename': item['file'],
                'Extension': item['ext'],
                'Size_KB': round(item['size_kb'], 2),
                'Line_Count': item['metrics']['lines'],
                'Inline_CSS_Count': item['metrics']['inline_css'],
                'Internal_Style_Blocks_Count': item['metrics']['internal_style_blocks'],
                'External_Stylesheet_Links_Count': item['metrics']['external_stylesheet_links'],
                'Inline_JS_Count': item['metrics']['inline_js'],
                'Internal_Script_Blocks_Count': item['metrics']['internal_script_blocks'],
                'External_Script_Tags_Count': item['metrics']['external_script_tags'],
                'AJAX_Calls_Count': item['metrics']['ajax_calls'],
                'Has_Ajax_Calls': item['metrics']['has_ajax_calls'],
                'Dynamic_JS_Gen_Count': item['metrics']['dynamic_js'],
                'Dynamic_CSS_Gen_Count': item['metrics']['dynamic_css'],
                'Full_Path': item['file_path']
            })
            
            # Update Directory Stats
            stats = self.directory_stats[rel_dir]
            stats['count'] += 1
            stats['lines'] += item['metrics']['lines']
            stats['depth'] = depth
            if 'extensions' not in stats:
                stats['extensions'] = collections.defaultdict(int)
            stats['extensions'][item['ext']] += 1

        print(f"Scan complete. Found {len(self.file_inventory)} files.")
        return self.file_inventory, self.directory_stats
