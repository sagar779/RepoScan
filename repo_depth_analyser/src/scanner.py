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
                r'(?:<link\b[^>]*rel\s*=\s*["\']stylesheet["\'][^>]*>|@import\s+(?:url\()?["\'][^"\']+["\'])', 
                re.IGNORECASE
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
                r'(?:<script\b[^>]*src\s*=\s*["\'][^"\']+["\'][^>]*>|\bimport\s+(?:[\w\s{},*]+from\s+)?["\'][^"\']+["\']|\brequire\s*\(\s*["\'][^"\']+["\']\s*\)|\bdefine\s*\(\s*\[)', 
                re.IGNORECASE
            ),
            
            # 2a. Modern CSS-in-JS
            'css_in_js': re.compile(
                r'(?:styled\.\w+|css`|styled\s*\()',
                re.IGNORECASE
            ),

            # 3. AJAX / Network Calls
            'ajax_call': re.compile(
                r'(\bfetch\s*\(|'
                r'new\s+XMLHttpRequest\s*\(|'
                r'(?:\$|jQuery|axios|superagent|http)\s*\.\s*(?:ajax|get|post|getJSON|getScript|load|request|ajaxSetup|ajaxPrefilter|ajaxTransport|param|parseJSON)\s*\(|'
                r'\.(?:load|ajaxStart|ajaxSend|ajaxSuccess|ajaxError|ajaxComplete|ajaxStop|serialize|serializeArray)\s*\(|'
                r'\.open\s*\(\s*["\'](?:GET|POST|PUT|DELETE|PATCH)["\']|'
                r'\bonreadystatechange\s*=|'
                r'\.send\s*\(|'
                r'\baxios(?:\.\w+)?\s*\(|'
                r'new\s+WebSocket\s*\(|'
                r'new\s+EventSource\s*\(|'
                r'\bajax\s*:\s*function|'  # Object literal AJAX method definitions
                r'navigator\.sendBeacon\s*\(|'  # Analytics/Tracking
                r'new\s+ActiveXObject\s*\(|'    # Legacy IE
                r'\bio\s*\(|'                   # Socket.io
                r'HubConnectionBuilder|'        # SignalR
                r'\bSys\.Net\.WebRequest\s*\(|' # Microsoft AJAX Library (Legacy)
                r'\bPageMethods\.\w+\s*\(|'     # ASP.NET WebForms RPC
                r'\b__doPostBack\s*\(|'         # ASP.NET Postback
                r'\bSys\.WebForms\.PageRequestManager|' # UpdatePanel Manager
                r'\bdata-ajax(?:-\w+)?\s*=|'    # Unobtrusive AJAX Attributes
                r'\.setRequestHeader\s*\(|'     # XHR Header Config
                r'\.abort\s*\(|'                # Request Cancellation
                r'\.getResponseHeader\s*\(|'    # Header Inspection
                r'\.getAllResponseHeaders\s*\(|'
                r'new\s+Headers\s*\(|'          # Fetch API Headers
                r'new\s+Request\s*\(|'          # Fetch API Request
                r'\bJSON\.parse\s*\(|'          # Native JSON
                r'\bJSON\.stringify\s*\(|'      # Native JSON
                r'<\w+:UpdatePanel|'            # ASP.NET Partial Rendering
                r'<\w+:ScriptManager|'          # ASP.NET AJAX Enabler
                r'\bScriptManager\.RegisterStartupScript\s*\(|' # Server-Side Script Injection
                r'\bScriptManager\.RegisterClientScriptBlock\s*\(|'
                r'\bClientScript\.RegisterStartupScript\s*\(|'
                r'\bClientScript\.RegisterClientScriptBlock\s*\(|'
                r'\bPage\.ClientScript\s*\.|'
                r'\[WebMethod\]|'               # ASP.NET AJAX Endpoint
                r'\[ScriptMethod\]|'            # ASP.NET Script Service
                r'\[WebService\]|'              # Legacy Web Service
                r'\[OperationContract\]|'       # WCF
                r'\[ApiController\]|'           # Web API 2 / Core
                r'\[Route\(\s*["\']api/|'       # API Route
                r'\[HubName\]|'                 # SignalR Hub
                r'\bhubConnection\.start\s*\(|' # SignalR Client
                r'\bClients\.All|'              # SignalR Server
                r'\bClients\.Caller|'
                r'@Ajax\.ActionLink|'           # Razor AJAX Helper
                r'@Ajax\.BeginForm|'
                r'@Url\.Action\s*\(|'           # URL Generation for AJAX
                r'@Url\.Content\s*\(|'
                r'<system\.web\.extensions>|'   # Web.config AJAX
                r'<scriptResourceHandler>|'
                r'<telerik:RadAjaxManager|'     # Telerik
                r'<telerik:RadAjaxPanel|'
                r'\bRadAjaxManager\b|'
                r'\bASPxCallback|'              # DevExpress
                r'\bASPxCallbackPanel|'
                r'\$http\b|'                    # Angular 1.x / Vue Resource
                r'\bthis\.http\.get\s*\(|'      # Angular HttpClient
                r'\bthis\.http\.post\s*\(|'
                r'\buseQuery\s*\(|'             # React/TanStack Query
                r'\buseMutation\s*\(|'
                r'\bnew\s+Ajax\.Request\s*\(|'  # Prototype.js
                r'\bnew\s+Request(?:.JSON)?\s*\(|' # MooTools
                r'\bdataType\s*:\s*["\']jsonp["\']|' # jQuery JSONP
                r'\bResponse\.Write\s*\(\s*["\']<script|' # Server-Side Script Injection (Direct)
                r'\bChannelFactory<|'           # WCF Client
                r'\bHttpClient\s+|'             # Blazor / .NET HttpClient usage
                r'\bIJSRuntime\b|'              # Blazor JS Interop
                r'\[Http(?:Get|Post|Put|Delete|Patch|Options)\]|' # .NET API Attributes
                r'\bbackgroundFetch\b|'         # Background Fetch API
                r'\bIJSRuntime\b|'              # Blazor JS Interop
                r'\[Http(?:Get|Post|Put|Delete|Patch|Options)\]|' # .NET API Attributes
                r'\bbackgroundFetch\b|'         # Background Fetch API
                r'target=["\']_?iframe["\']|'   # Hidden Iframe Target (Naive)
                r'<iframe\b[^>]*style=["\'].*display:\s*none|' # Hidden Iframe (Structure)
                r'<iframe\b[^>]*style=["\'].*display:\s*none|' # Hidden Iframe (Structure)
                r'\bnew\s+FormData\b|'          # Form Data Constructor
                r'\bnew\s+Image\s*\(|'          # Pixel Tracking (Image)
                r'\.src\s*=\s*["\']http)',      # Pixel Tracking (src assignment)
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
                r'\.cssText\s*=|' # Bulk Style Assignment
                r'setProperty\s*\(|'
                r'insertRule\s*\(|'
                r'addRule\s*\(|'
                r'setAttribute\s*\(\s*["\']style["\']|' # Dynamic Style Attribute
                r'\.classList\.(?:add|remove|toggle|replace)\s*\(|' # Indirect CSS
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
            'ajax_calls': 0, 'has_ajax_calls': 'No', 'dynamic_js': 0, 'dynamic_css': 0,
            'ajax_details': []
        }
        
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()
        
        # Relevant Extensions for Client-Side Code
        web_exts = {
            '.html', '.htm', '.aspx', '.ascx', '.cshtml', '.vbhtml', '.master', 
            '.php', '.jsp', '.js', '.ts', '.vue', '.jsx', '.tsx', '.razor',
            '.cs', '.vb', '.ashx', '.asmx', '.config'
        }
        
        try:
            # Skip very large files (> 10MB) to prevent memory issues
            file_size = os.path.getsize(filepath)
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    metrics['lines'] = sum(1 for _ in f)
                return metrics
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                metrics['lines'] = content.count('\n') + 1  # Faster than splitlines()
                
                # Only analyze web-related files for Client-Side patterns
                if ext in web_exts:
                    # Run Regex Analysis
                    metrics['inline_css'] = len(self.patterns['inline_css'].findall(content))
                    metrics['internal_style_blocks'] = len(self.patterns['internal_style_blocks'].findall(content))
                    metrics['external_stylesheet_links'] = len(self.patterns['external_stylesheet_links'].findall(content))
                    metrics['inline_js'] = len(self.patterns['inline_js'].findall(content))
                    metrics['internal_script_blocks'] = len(self.patterns['internal_script_blocks'].findall(content))
                    metrics['external_script_tags'] = len(self.patterns['external_script_tags'].findall(content))
                    
                    # Detailed AJAX Analysis
                    ajax_matches = self.patterns['ajax_call'].finditer(content)
                    for match in ajax_matches:
                        # metrics['ajax_calls'] += 1  <-- REMOVED: Only increment for Logical Requests
                        line_num = content.count('\n', 0, match.start()) + 1
                        match_str = match.group()
                        
                        # Determine Capability & CSP Directive
                        capability = "Data Exchange"
                        csp = "connect-src"
                        difficulty = "Easy"
                        
                        lower_match = match_str.lower()
                        
                        # Determine Category and Capability
                        category = "Request" # Default
                        capability = "Data Exchange" # Default
                        is_logical_request = True
                        difficulty = "Easy"

                        if 'sendbeacon' in lower_match:
                            capability = "Telemetry"
                            category = "Request"
                        elif 'getscript' in lower_match or '.js' in lower_match:
                            capability = "Script Loading (Dynamic)"
                            category = "Request"
                            difficulty = "Hard"
                        elif '.css' in lower_match:
                            capability = "CSS Loading"
                            category = "Request"
                            difficulty = "Medium"
                        elif '.html' in lower_match:
                            capability = "UI Injection"
                            category = "Request"
                            difficulty = "Medium"
                        elif 'load' in lower_match and 'payload' not in lower_match: 
                            capability = "UI Injection (Likely)"
                            category = "Request"
                            difficulty = "Medium"
                        elif any(x in lower_match for x in ['ajaxsetup', 'ajaxprefilter', 'ajaxtransport']):
                            capability = "AJAX Configuration"
                            category = "Config"
                            is_logical_request = False
                            difficulty = "Easy"
                        elif any(x in lower_match for x in ['ajaxstart', 'ajaxsend', 'ajaxsuccess', 'ajaxerror', 'ajaxcomplete', 'ajaxstop', 'onreadystatechange']):
                            capability = "Global Event Handler"
                            category = "Event"
                            is_logical_request = False
                            difficulty = "Hard (Refactoring Risk)"
                        elif any(x in lower_match for x in ['serialize', 'param', 'parsejson']):
                            capability = "Form/Data Utility"
                            category = "Utility"
                            is_logical_request = False
                            difficulty = "Easy"
                        elif 'sys.net.webrequest' in lower_match:
                             capability = "Data Exchange (Legacy)"
                             category = "Request"
                             difficulty = "Hard"
                        elif 'pagemethods' in lower_match:
                             capability = "RPC (Code-Behind)"
                             category = "Request"
                             difficulty = "Hard"
                        elif '__dopostback' in lower_match:
                             capability = "Partial Postback"
                             category = "Request"
                             difficulty = "Medium"
                        elif 'data-ajax' in lower_match:
                             capability = "Declarative AJAX"
                             category = "Request"
                             difficulty = "Easy"
                        elif 'sys.webforms' in lower_match:
                             capability = "UpdatePanel Config"
                             category = "Config"
                             is_logical_request = False
                             difficulty = "Hard"
                        elif any(x in lower_match for x in ['setrequestheader', 'getresponseheader', 'getallresponseheaders']):
                             capability = "Request Header Manipulation"
                             category = "Config"
                             is_logical_request = False
                             difficulty = "Medium"
                        elif 'abort' in lower_match:
                             capability = "Request Control"
                             category = "Utility"
                             is_logical_request = False
                             difficulty = "Easy"
                        elif 'json.parse' in lower_match or 'json.stringify' in lower_match:
                             capability = "JSON Utility"
                             category = "Utility"
                             is_logical_request = False
                             difficulty = "Easy"
                        elif 'new headers' in lower_match or 'new request' in lower_match:
                             capability = "Fetch API Construct"
                             category = "Construct"
                             is_logical_request = False
                             difficulty = "Easy"
                        elif 'updatepanel' in lower_match:
                             capability = "Partial Rendering (UpdatePanel)"
                             category = "Request"
                             difficulty = "Hard"
                        elif 'scriptmanager' in lower_match or 'clientscript' in lower_match:
                             capability = "Server-Side Script Injection"
                             category = "Server"
                             is_logical_request = False
                             difficulty = "Hard"
                        elif 'webmethod' in lower_match or 'scriptmethod' in lower_match or 'webservice' in lower_match:
                             capability = "AJAX Endpoint (Server)"
                             category = "Server"
                             is_logical_request = False
                             difficulty = "Medium"
                        elif 'apicontroller' in lower_match or '[route' in lower_match:
                             capability = "API Endpoint (Server)"
                             category = "Server"
                             is_logical_request = False
                             difficulty = "Medium"
                        elif 'operationcontract' in lower_match:
                             capability = "WCF Endpoint (Server)"
                             category = "Server"
                             is_logical_request = False
                             difficulty = "Hard"
                        elif 'hubname' in lower_match or 'clients.all' in lower_match or 'clients.caller' in lower_match:
                             capability = "SignalR Hub (Server)"
                             category = "Server"
                             is_logical_request = False
                             difficulty = "Hard"
                        elif 'hubconnection' in lower_match:
                             capability = "SignalR Client"
                             category = "Real-time"
                             is_logical_request = True
                             difficulty = "Medium"
                        elif '@ajax' in lower_match:
                             capability = "Razor AJAX Helper"
                             category = "Request"
                             is_logical_request = True
                             difficulty = "Medium"
                        elif '@url' in lower_match:
                             capability = "Dynamic URL Generation"
                             category = "Construct"
                             # Helper itself isn't a request, but often inside one. Let's mark as Construct.
                             is_logical_request = False 
                             difficulty = "Easy"
                        elif '<system.web.extensions>' in lower_match or 'scriptresourcehandler' in lower_match:
                             capability = "AJAX Configuration"
                             category = "Config"
                             is_logical_request = False
                             difficulty = "Medium"
                        elif 'radajax' in lower_match or 'telerik' in lower_match:
                             capability = "Telerik AJAX Control"
                             category = "Third-Party"
                             is_logical_request = True # Often wrappers around UpdatePanel
                             difficulty = "Hard (Vendor Lock-in)"
                        elif 'aspxcallback' in lower_match:
                             capability = "DevExpress AJAX Control"
                             category = "Third-Party"
                             is_logical_request = True
                             difficulty = "Hard (Vendor Lock-in)"

                        elif 'response.write' in lower_match:
                             capability = "Direct Script Injection"
                             category = "Server"
                             is_logical_request = False
                             difficulty = "High (Security Risk)"
                        elif 'channelfactory' in lower_match:
                             capability = "WCF Client Proxy"
                             category = "Server"
                             is_logical_request = True # It initiates a request
                             difficulty = "Hard"
                        elif 'httpclient' in lower_match:
                             capability = ".NET HttpClient"
                             category = "Server/Blazor"
                             is_logical_request = True
                             difficulty = "Easy"
                        elif 'ijsruntime' in lower_match:
                             capability = "Blazor JS Interop"
                             category = "Blazor"
                             is_logical_request = False
                             difficulty = "Medium"
                        elif '[http' in lower_match:
                             capability = "API Endpoint Verb"
                             category = "Server"
                             is_logical_request = False
                             difficulty = "Easy"
                        elif 'backgroundfetch' in lower_match:
                             capability = "Background Sync/Fetch"
                             category = "Service Worker"
                             is_logical_request = True
                             difficulty = "Medium"
                        elif 'iframe' in lower_match:
                             capability = "Hidden Iframe (Pseudo-AJAX)"
                             category = "Legacy Pattern"
                             is_logical_request = True
                             difficulty = "Hard"
                        elif 'formdata' in lower_match:
                             capability = "Form Data Construction"
                             category = "Construct"
                             # It's usually passed TO a fetch or XHR, so it's a Construct, not a request itself.
                             is_logical_request = False
                             difficulty = "Easy"
                        elif 'new image' in lower_match or '.src' in lower_match:
                             capability = "Pixel Tracking (Image)"
                             category = "Request"
                             is_logical_request = True
                             difficulty = "Easy"
                        elif 'usequery' in lower_match or 'usemutation' in lower_match:
                             capability = "Modern Data Fetching (React Query)"
                             category = "Modern Framework"
                             is_logical_request = True
                             difficulty = "Easy"
                        elif 'this.http' in lower_match:
                             capability = "Angular HttpClient"
                             category = "Modern Framework"
                             is_logical_request = True
                             difficulty = "Easy"
                        elif 'ajax.request' in lower_match or 'new request' in lower_match: # carefully distinguishing MooTools/Prototype
                             if 'ajax.request' in lower_match:
                                 capability = "Prototype.js AJAX"
                                 category = "Legacy Lib"
                             else:
                                 capability = "MooTools/Fetch Request" # 'new Request' is also Fetch API!
                                 if 'mootools' in lower_match: category = "Legacy Lib" # unlikely to match just 'mootools' string here
                                 else: category = "Construct" # Assume Fetch API unless context proves otherwise
                             is_logical_request = True
                             difficulty = "Hard"
                        elif 'jsonp' in lower_match:
                             capability = "JSONP (Legacy Cross-Domain)"
                             category = "Legacy Pattern"
                             is_logical_request = True
                             difficulty = "Hard (Security Risk)"
                        elif 'new xmlhttprequest' in lower_match or '.open' in lower_match:
                             capability = "XHR Construct"
                             category = "Construct"
                             is_logical_request = False
                        elif 'new websocket' in lower_match or 'new eventsource' in lower_match:
                             capability = "Real-time Construct"
                             category = "Construct"
                             # For these, the 'new' IS the request initiation effectively (connection open), so maybe keep as Logical?
                             # ChatGPT said "Partial XHR Constructs... new XMLHttpRequest... .open... .send".
                             # For WS, 'new WebSocket' opens the connection. 
                             # But to be consistent with XHR, let's count it. But 'new XHR' is NOT a request.
                             # Let's mark 'new' XHR as False.
                             if 'xmlhttprequest' in lower_match: is_logical_request = False
                             else: is_logical_request = True # WS/EventSource open immediately
                        
                        # Only increment total count if it's a logical request (Network Traffic)
                        if is_logical_request:
                             print(f"DEBUG: Incrementing for {match_str} (Category: {category})")
                             metrics['ajax_calls'] += 1

                        metrics['ajax_details'].append({
                            'Line': line_num,
                            'Code_Snippet': match_str[:100], 
                            'Category': category,
                            'Capability': capability,
                            'Difficulty': difficulty,
                            'Is_Counted': "Yes" if is_logical_request else "No"
                        })

                    metrics['has_ajax_calls'] = "Yes" if metrics['ajax_calls'] > 0 else "No"
                    metrics['dynamic_js'] = len(self.patterns['dynamic_js'].findall(content))
                    metrics['dynamic_css'] = len(self.patterns['dynamic_css'].findall(content))
                    
                    # Add CSS-in-JS to Dynamic CSS count (it's effectively dynamic)
                    metrics['dynamic_css'] += len(self.patterns['css_in_js'].findall(content))
                
        except (UnicodeDecodeError, PermissionError) as e:
            # Silently skip files with encoding or permission issues
            pass
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

    def scan(self, verbose=False):
        """Walks the directory and collects metadata."""
        # Collect all files to scan
        all_files = []
        for root, dirs, files in os.walk(self.target_dir):
            # Filter out excluded directories (modifies dirs in-place)
            dirs[:] = [d for d in dirs if d not in self.excluded_folders]
            
            for file in files:
                all_files.append((root, file))
        
        if verbose:
            print(f"\nFound {len(all_files):,} files in {len(set(r for r, f in all_files)):,} directories")
            print("\nScanning folders:")
            print("-" * 66)
                
        # Use ThreadPoolExecutor for concurrent scanning
        results = []
        processed_dirs = set()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_file = {executor.submit(self.process_file, r, f): (r, f) for r, f in all_files}
            for future in concurrent.futures.as_completed(future_to_file):
                try:
                    data = future.result()
                    results.append(data)
                    
                    # Verbose progress per folder
                    if verbose and data['root'] not in processed_dirs:
                        processed_dirs.add(data['root'])
                        rel_dir = os.path.relpath(data['root'], self.target_dir)
                        if rel_dir == '.':
                            rel_dir = '(Root)'
                        
                        # Count elements in this directory
                        dir_results = [r for r in results if r['root'] == data['root']]
                        total_inline_js = sum(r['metrics']['inline_js'] for r in dir_results)
                        total_inline_css = sum(r['metrics']['inline_css'] for r in dir_results)
                        total_ajax = sum(r['metrics']['ajax_calls'] for r in dir_results)
                        
                        print(f"  {rel_dir}")
                        print(f"    Files: {len(dir_results)} | JS: {total_inline_js} | CSS: {total_inline_css} | AJAX: {total_ajax}")
                        
                except Exception as exc:
                    if verbose:
                        print(f"  Warning: {exc}")

        # Aggregate Results
        all_ajax_details = []
        
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
            
            # Collect AJAX Details
            if item['metrics']['ajax_details']:
                for detail in item['metrics']['ajax_details']:
                    detail['File_Path'] = item['file_path']
                    detail['Filename'] = item['file']
                    all_ajax_details.append(detail)
            
            # Update Directory Stats
            stats = self.directory_stats[rel_dir]
            stats['count'] += 1
            stats['lines'] += item['metrics']['lines']
            stats['depth'] = depth
            if 'extensions' not in stats:
                stats['extensions'] = collections.defaultdict(int)
            stats['extensions'][item['ext']] += 1

        if verbose:
            print("-" * 66)
            print(f"Processed {len(results):,} files\n")
        return self.file_inventory, self.directory_stats, all_ajax_details
