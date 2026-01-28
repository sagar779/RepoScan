import os
import re
import shutil
import argparse
import shutil

def parse_extracted_filename(filename):
    """
    Parses metadata from filename:
    format: path_to_file_type_lineStart-End.ext
    example: Views_Home_Index.cshtml_scriptblock_line10-25.js
    """
    try:
        # Regex to find the _lineX-Y part
        match = re.search(r'(.+)_([a-zA-Z0-9]+)_line(\d+)-(\d+)\.(js|css)$', filename)
        if not match:
            return None
            
        sanitized_path, code_type, start_line, end_line, ext = match.groups()
        
        # We need to reconstruction the original relative path.
        # This is tricky because we replaced '/' with '_'.
        # But we know the root structure. This is a best-effort matching.
        # Actually, we can just rely on the user providing the root, and we fuzzy match or 
        # use the fact that the underscores match os.sep.
        
        return {
            'sanitized_path': sanitized_path,
            'code_type': code_type,
            'start_line': int(start_line),
            'end_line': int(end_line),
            'ext': ext,
            'extracted_file': filename
        }
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
        return None

def find_original_file(root_dir, sanitized_path):
    """
    Attempts to find the original file matching the sanitized path.
    Supports exact match and suffix match (to handle Root folder varying depth).
    """
    candidates = []
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            # Construct relative path
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, root_dir)
            
            # Simulate sanitization
            test_sanitized = rel_path.replace(os.sep, "_").replace("/", "_").replace("\\", "_")
            
            if test_sanitized == sanitized_path:
                return rel_path
                
            # Fuzzy: Check if one assumes the other is a subpath
            # e.g. Scan was "Views_File", Refactor sees "Project_Views_File"
            if test_sanitized.endswith(sanitized_path) or sanitized_path.endswith(test_sanitized):
                candidates.append(rel_path)

    # If exactly one fuzzy candidate, return it
    if len(candidates) == 1:
        return candidates[0]
        
    return None

def main():
    parser = argparse.ArgumentParser(description="Generate refactored copies of source files.")
    parser.add_argument("--root", required=True, help="Root directory of the original source code")
    parser.add_argument("--extracted", required=True, help="Path to the 'extracted_code' folder")
    parser.add_argument("--output", required=True, help="Directory to save refactored copies")
    
    args = parser.parse_args()

    # Validate Input
    if not os.path.exists(args.root):
        print(f"Error: The root directory '{args.root}' does not exist. Please check the path.")
        return

    # 1. Copy Codebase to Output
    print(f"Creating refactored copy at: {args.output}")
    if os.path.exists(args.output):
        try:
            # Helper to delete read-only files (like .git objects)
            import stat
            def remove_readonly(func, path, excinfo):
                os.chmod(path, stat.S_IWRITE)
                func(path)
                
            shutil.rmtree(args.output, onerror=remove_readonly)
        except Exception as e:
            print(f"Error cleaning output/destination {args.output}: {e}")
            return

    try:
        shutil.copytree(args.root, args.output)
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        return

    modified = False
    file_rel_path = os.path.basename(file_path) # Simplified matching

    # --- 1. HANDLE INTERNAL SCRIPTS (BLOCKS) ---
    # We iterate over the ACTUAL script tags in the file and try to process them
    scripts = soup.find_all('script')
    for script in scripts:
        if script.get('src'): continue 
        if not script.string: continue
        
        content = script.string
        
        # Check if this block needs refactoring (State B/C)
        has_razor = '@' in content
        if not has_razor: continue # State A (Already handled by extractor, or ignored)

        if re.search(r'(@if|@foreach|@for|@while)', content):
            # State C: Add TODO
            comment = soup.new_string(f" TODO: Manual Refactor Required (State C) ")
            script.insert_before(comment)
            continue
            
        # State B: Apply Bridge
        file_hash = generate_hash(content + file_path)
        clean_js, bridge_config = create_bridge_config(content, file_hash)
        
        if bridge_config:
            # Save External File
            new_filename = f"{file_rel_path}_script_{file_hash}.js"
            js_out_path = os.path.join(output_root, "js", "internal", new_filename)
            os.makedirs(os.path.dirname(js_out_path), exist_ok=True)
            
            with open(js_out_path, 'w', encoding='utf-8') as f:
                f.write(clean_js)
            
            # Update HTML
            # 1. Inject Config
            config_script = soup.new_tag("script")
            config_js = f"window.{BRIDGE_VAR_PREFIX}{file_hash} = {{\n"
            for k, v in bridge_config.items():
                config_js += f"    {k}: '{v}',\n" # Razor stays in quotes in the config
            config_js += "};"
            config_script.string = config_js
            script.insert_before(config_script)
            
            # 2. Replace Block with Src
            # FIX: Create new tag and replace_with
            new_script = soup.new_tag("script", src=f"/js/internal/{new_filename}")
            script.replace_with(new_script)
            modified = True
            print(f"[Fixed] Extracted Script Block in {file_rel_path}")

    # --- 2. HANDLE INLINE HANDLERS (ATTRIBUTES) ---
    # We look for standard event attributes
    events = ['onclick', 'onload', 'onmouseover', 'onsubmit']
    all_tags = soup.find_all(True)
    
    bottom_scripts = []
    
    for tag in all_tags:
        for evt in events:
            if tag.has_attr(evt):
                inline_code = tag[evt]
                # We classify this. If it has Razor, we skip (State C) or process.
                # For v2.1, we treat all inline as candidates for extraction.
                
                # 1. Generate ID
                if tag.has_attr('id'):
                    elem_id = tag['id']
                else:
                    elem_id = f"{ID_PREFIX}{generate_hash(inline_code)}"
                    tag['id'] = elem_id
                
                # 2. Extract Code
                new_filename = f"{file_rel_path}_{evt}_{generate_hash(inline_code)}.js"
                js_out_path = os.path.join(output_root, "js", "inline", new_filename)
                os.makedirs(os.path.dirname(js_out_path), exist_ok=True)
                
                # Wrapper Logic
                wrapper_js = f"""
document.addEventListener('DOMContentLoaded', function() {{
    var el = document.getElementById('{elem_id}');
    if(el) {{
        el.addEventListener('{evt[2:]}', function(event) {{
            {inline_code}
        }});
    }}
}});
"""
                with open(js_out_path, 'w', encoding='utf-8') as f:
                    f.write(wrapper_js)
                
                # 3. Clean HTML
                del tag[evt] # REMOVE the attribute
                bottom_scripts.append(f"/js/inline/{new_filename}")
                modified = True
                print(f"[Fixed] Extracted Inline {evt} in {file_rel_path}")

    # Inject Inline Script References at Body End
    if bottom_scripts:
        target = soup.body if soup.body else soup
        for src in bottom_scripts:
            s_tag = soup.new_tag("script", src=src)
            target.append(s_tag)

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))

def main():
    parser = argparse.ArgumentParser(description="Refactoring Engine v2.1 (Hotfix)")
    parser.add_argument("--root", required=True, help="Root of original code")
    parser.add_argument("--extracted", required=True, help="Extracted code directory")
    parser.add_argument("--output", required=True, help="Destination")
    
    args = parser.parse_args()
    
    if os.path.exists(args.output):
        try:
            shutil.rmtree(args.output)
        except:
            pass # Handle permission errors gracefully
            
    shutil.copytree(args.root, args.output)
    print(f"[Init] Copied codebase to {args.output}")

    for root, dirs, files in os.walk(args.output):
        for file in files:
            if file.lower().endswith(('.cshtml', '.html', '.aspx')):
                full_path = os.path.join(root, file)
                process_file(full_path, args.extracted, args.output)
    
    print("\n[Done] Refactoring Complete.")

if __name__ == "__main__":
    main()
