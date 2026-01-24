"""
AJAX Detection Module for RepoScan

Detects AJAX patterns in JavaScript code using comprehensive regex patterns matched with RepoScan Depth Analyser.
Classifies findings by Capability, Difficulty, and extracts endpoint URLs.
"""

import re
import os
from typing import Optional

# -------------------------------------------------------------------------
# COMPREHENSIVE REGEX PATTERNS (Synced with RepoDepthAnalyser)
# -------------------------------------------------------------------------

# 1. Main AJAX Call Pattern (The "Giant Regex")
AJAX_CALL_PATTERN = re.compile(
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
)

# Server-side dependency patterns
SERVER_PATTERNS = [
    re.compile(r'@Model\.', re.IGNORECASE),
    re.compile(r'@ViewBag\.', re.IGNORECASE),
    re.compile(r'@ViewData\.', re.IGNORECASE),
    re.compile(r'@Url\.Action', re.IGNORECASE),
    re.compile(r'@Url\.Content', re.IGNORECASE),
    re.compile(r'<%=', re.IGNORECASE),
    re.compile(r'<%:', re.IGNORECASE),
    re.compile(r'<%\s', re.IGNORECASE),
    re.compile(r'\{\{.*?\}\}', re.IGNORECASE),  # Template engines
    re.compile(r'\bResponse\.Write\b', re.IGNORECASE),
    re.compile(r'\bRequest\.Form\b', re.IGNORECASE),
]

# URL extraction patterns
URL_PATTERNS = {
    # url: '/api/users' or url: "/api/users"
    'url_property': re.compile(r'''url\s*:\s*['"]([^'"]+)['"]''', re.IGNORECASE),
    # url: baseUrl + '/users'
    'url_concat': re.compile(r'''url\s*:\s*([a-zA-Z_$][a-zA-Z0-9_$]*\s*\+\s*['"][^'"]+['"])''', re.IGNORECASE),
    # url: `${API_URL}/users`
    'url_template': re.compile(r'''url\s*:\s*`([^`]+)`''', re.IGNORECASE),
    # url: variableName
    'url_variable': re.compile(r'''url\s*:\s*([a-zA-Z_$][a-zA-Z0-9_$]*)(?:\s|,|\))''', re.IGNORECASE),
    # fetch('/api/users') or fetch("/api/users")
    'fetch_literal': re.compile(r'''fetch\s*\(\s*['"]([^'"]+)['"]''', re.IGNORECASE),
    # fetch(`${base}/users`)
    'fetch_template': re.compile(r'''fetch\s*\(\s*`([^`]+)`''', re.IGNORECASE),
    # $.get('/api/users', ...) or $.post('/api/users', ...)
    'jquery_literal': re.compile(r'''\$\.(get|post|getJSON|load)\s*\(\s*['"]([^'"]+)['"]''', re.IGNORECASE),
    # axios.get('/api/users')
    'axios_literal': re.compile(r'''axios\.(get|post|put|delete|patch)\s*\(\s*['"]([^'"]+)['"]''', re.IGNORECASE),
}

# Inline file extensions (view/template files)
INLINE_EXTENSIONS = {'.cshtml', '.aspx', '.ascx', '.master', '.html', '.htm', '.php', '.jsp'}


def detect_ajax_patterns(snippet) -> bool:
    """
    Main entry point for AJAX detection.
    Enriches the CodeSnippet object in-place with AJAX metadata.
    
    Args:
        snippet: CodeSnippet object to analyze
        
    Returns:
        bool: True if AJAX detected, False otherwise
    """
    # JS snippets only
    if snippet.category != 'JS':
        return False
    
    code = snippet.full_code
    
    # 1. Run the Giant Regex
    matches = list(AJAX_CALL_PATTERN.finditer(code))
    
    if not matches:
        return False

    snippet.ajax_detected = True
    snippet.ajax_count = 0 # Will count logical requests
    snippet.ajax_details = [] # Store detailed findings

    first_classification_done = False

    for match in matches:
        match_str = match.group()
        lower_match = match_str.lower()
        
        # Classification Logic (Synced with RepoDepthAnalyser)
        capability = "Data Exchange"
        category = "Request"
        is_logical_request = True
        difficulty = "Easy"

        if 'sendbeacon' in lower_match:
            capability = "Telemetry"
        elif 'getscript' in lower_match or '.js' in lower_match:
            capability = "Script Loading (Dynamic)"
            difficulty = "Hard"
        elif '.css' in lower_match:
            capability = "CSS Loading"
            difficulty = "Medium"
        elif '.html' in lower_match:
            capability = "UI Injection"
            difficulty = "Medium"
        elif 'load' in lower_match and 'payload' not in lower_match: 
            capability = "UI Injection (Likely)"
            difficulty = "Medium"
        elif any(x in lower_match for x in ['ajaxsetup', 'ajaxprefilter', 'ajaxtransport']):
            capability = "AJAX Configuration"
            category = "Config"
            is_logical_request = False
        elif any(x in lower_match for x in ['ajaxstart', 'ajaxsend', 'ajaxsuccess', 'ajaxerror', 'ajaxcomplete', 'ajaxstop', 'onreadystatechange']):
            capability = "Global Event Handler"
            category = "Event"
            is_logical_request = False
            difficulty = "Hard (Refactoring Risk)"
        elif any(x in lower_match for x in ['serialize', 'param', 'parsejson']):
            capability = "Form/Data Utility"
            category = "Utility"
            is_logical_request = False
        elif 'sys.net.webrequest' in lower_match:
                capability = "Data Exchange (Legacy)"
                difficulty = "Hard"
        elif 'pagemethods' in lower_match:
                capability = "RPC (Code-Behind)"
                difficulty = "Hard"
        elif '__dopostback' in lower_match:
                capability = "Partial Postback"
                difficulty = "Medium"
        elif 'data-ajax' in lower_match:
                capability = "Declarative AJAX"
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
        elif 'json.parse' in lower_match or 'json.stringify' in lower_match:
                capability = "JSON Utility"
                category = "Utility"
                is_logical_request = False
        elif 'new headers' in lower_match or 'new request' in lower_match:
                capability = "Fetch API Construct"
                category = "Construct"
                is_logical_request = False
        elif 'updatepanel' in lower_match:
                capability = "Partial Rendering (UpdatePanel)"
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
        elif '@ajax' in lower_match:
                capability = "Razor AJAX Helper"
        elif '@url' in lower_match:
                capability = "Dynamic URL Generation"
                category = "Construct"
                is_logical_request = False
        elif '<system.web.extensions>' in lower_match or 'scriptresourcehandler' in lower_match:
                capability = "AJAX Configuration"
                category = "Config"
                is_logical_request = False
                difficulty = "Medium"
        elif 'radajax' in lower_match or 'telerik' in lower_match:
                capability = "Telerik AJAX Control"
                category = "Third-Party"
                difficulty = "Hard (Vendor Lock-in)"
        elif 'aspxcallback' in lower_match:
                capability = "DevExpress AJAX Control"
                category = "Third-Party"
                difficulty = "Hard (Vendor Lock-in)"
        elif 'response.write' in lower_match:
                capability = "Direct Script Injection"
                category = "Server"
                is_logical_request = False
                difficulty = "High (Security Risk)"
        elif 'channelfactory' in lower_match:
                capability = "WCF Client Proxy"
                category = "Server"
                difficulty = "Hard"
        elif 'httpclient' in lower_match:
                capability = ".NET HttpClient"
                category = "Server/Blazor"
        elif 'ijsruntime' in lower_match:
                capability = "Blazor JS Interop"
                category = "Blazor"
                is_logical_request = False
                difficulty = "Medium"
        elif '[http' in lower_match:
                capability = "API Endpoint Verb"
                category = "Server"
                is_logical_request = False
        elif 'backgroundfetch' in lower_match:
                capability = "Background Sync/Fetch"
                category = "Service Worker"
                difficulty = "Medium"
        elif 'iframe' in lower_match:
                capability = "Hidden Iframe (Pseudo-AJAX)"
                category = "Legacy Pattern"
                difficulty = "Hard"
        elif 'formdata' in lower_match:
                capability = "Form Data Construction"
                category = "Construct"
                is_logical_request = False
        elif 'new image' in lower_match or '.src' in lower_match:
                capability = "Pixel Tracking (Image)"
        elif 'usequery' in lower_match or 'usemutation' in lower_match:
                capability = "Modern Data Fetching (React Query)"
                category = "Modern Framework"
        elif 'this.http' in lower_match:
                capability = "Angular HttpClient"
                category = "Modern Framework"
        elif 'ajax.request' in lower_match or 'new request' in lower_match:
                if 'ajax.request' in lower_match:
                    capability = "Prototype.js AJAX"
                    category = "Legacy Lib"
                    difficulty = "Hard"
                else:
                    capability = "MooTools/Fetch Request"
                    if 'mootools' in lower_match: 
                        category = "Legacy Lib" 
                    else: 
                        category = "Construct"
                    is_logical_request = True # Keeping as request for now
                    difficulty = "Hard"
        elif 'jsonp' in lower_match:
                capability = "JSONP (Legacy Cross-Domain)"
                category = "Legacy Pattern"
                difficulty = "Hard (Security Risk)"
        elif 'new xmlhttprequest' in lower_match or '.open' in lower_match:
                capability = "XHR Construct"
                category = "Construct"
                is_logical_request = False
                if 'xmlhttprequest' in lower_match: is_logical_request = False
                else: is_logical_request = True # open is start
        
        # Determine Endpoint based on the match type
        endpoint = extract_endpoint_url(code, lower_match)

        # Populate Details (Line Number calculation is rough here since we are working on a snippet)
        # We can try to find the line relative to the snippet start
        # start_offset = match.start()
        # rel_line = code[:start_offset].count('\n') 
        # abs_line = snippet.start_line + rel_line
        
        relative_line_offset = code[:match.start()].count('\\n')
        absolute_line = snippet.start_line + relative_line_offset

        detail = {
            'Line': absolute_line,
            'Code_Snippet': match_str[:100], 
            'Category': category,
            'Capability': capability,
            'Difficulty': difficulty,
            'Is_Counted': "Yes" if is_logical_request else "No",
            'Endpoint': endpoint
        }
        snippet.ajax_details.append(detail)

        if is_logical_request:
            snippet.ajax_count += 1
        
        # Set top-level fields for the FIRST or most significant finding (for backward compat)
        if not first_classification_done:
             snippet.ajax_pattern = category + " (" + capability + ")"
             snippet.capability = capability
             snippet.difficulty = difficulty
             snippet.endpoint_url = endpoint
             first_classification_done = True
             
    snippet.is_inline_ajax = is_inline_ajax(snippet.file_path)
    
    # Check for server dependencies
    snippet.has_server_deps = False
    for dep_pattern in SERVER_PATTERNS:
        if dep_pattern.search(code):
            snippet.has_server_deps = True
            break
            
    return True


def extract_endpoint_url(code: str, pattern_match: str) -> str:
    """
    Extracts the API endpoint URL from AJAX code.
    Tries to be smart based on the pattern match context.
    """
    # Limit search to first 1000 chars for performance
    search_code = code[:1000]
    
    # Try pattern-specific extraction based on regex names? 
    # Current regex is one giant blob, so we rely on string presence in 'pattern_match'
    
    if 'fetch' in pattern_match:
        match = URL_PATTERNS['fetch_template'].search(search_code)
        if match: return match.group(1)
        match = URL_PATTERNS['fetch_literal'].search(search_code)
        if match: return match.group(1)
        
    elif 'jquery' in pattern_match or '$' in pattern_match:
        match = URL_PATTERNS['jquery_literal'].search(search_code)
        if match: return match.group(2)

    elif 'axios' in pattern_match:
        match = URL_PATTERNS['axios_literal'].search(search_code)
        if match: return match.group(2)

    # Generic Fallbacks
    match = URL_PATTERNS['url_template'].search(search_code)
    if match: return match.group(1)

    match = URL_PATTERNS['url_property'].search(search_code)
    if match: 
        url = match.group(1)
        if '@' in url or '<%' in url: return "Server-Generated"
        return url

    match = URL_PATTERNS['url_concat'].search(search_code)
    if match: return match.group(1)

    match = URL_PATTERNS['url_variable'].search(search_code)
    if match: return "Dynamic/Variable"

    return "Unknown/Dynamic"


def is_inline_ajax(file_path: str) -> bool:
    """
    Determines if AJAX is inline (in view/template) or external (.js file).
    """
    _, ext = os.path.splitext(file_path)
    ext_lower = ext.lower()
    
    # .js files are external
    if ext_lower == '.js':
        return False
    
    # View/template files are inline
    if ext_lower in INLINE_EXTENSIONS:
        return True
    
    # Default to inline for unknown extensions (safer assumption)
    return True
