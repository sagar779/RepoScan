import os
import re
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
    """
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            # Construct relative path
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, root_dir)
            
            # Simulate sanitization
            test_sanitized = rel_path.replace(os.sep, "_").replace("/", "_").replace("\\", "_")
            
            if test_sanitized == sanitized_path:
                return rel_path
    return None

def main():
    parser = argparse.ArgumentParser(description="Generate refactored copies of source files.")
    parser.add_argument("--root", required=True, help="Root directory of the original source code")
    parser.add_argument("--extracted", required=True, help="Path to the 'extracted_code' folder")
    parser.add_argument("--output", required=True, help="Directory to save refactored copies")
    
    args = parser.parse_args()

    # 1. Copy Codebase to Output
    print(f"Creating refactored copy at: {args.output}")
    if os.path.exists(args.output):
        try:
            shutil.rmtree(args.output)
        except Exception as e:
            print(f"Error cleaning output/destination {args.output}: {e}")
            return

    try:
        shutil.copytree(args.root, args.output)
    except Exception as e:
        print(f"Failed to copy codebase: {e}")
        return

    # 2. Gather Modifications
    modifications = {} # { rel_file_path: [mods] }
    
    for root, _, files in os.walk(args.extracted):
        for file in files:
            meta = parse_extracted_filename(file)
            if not meta:
                continue
                
            orig_rel_path = find_original_file(args.output, meta['sanitized_path']) # Search in the COPY
            if not orig_rel_path:
                print(f"Warning: Could not find original file for {file}")
                continue
                
            if orig_rel_path not in modifications:
                modifications[orig_rel_path] = []
            modifications[orig_rel_path].append(meta)

    # 3. Process Files (The Copy)
    for rel_path, mods in modifications.items():
        # Sort desc by line number
        mods.sort(key=lambda x: x['start_line'], reverse=True)
        
        full_src_path = os.path.join(args.output, rel_path) # MODIFY THE COPY
        
        try:
            with open(full_src_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Failed to read {full_src_path}: {e}")
            continue
            
        # Apply edits
        for mod in mods:
            start_idx = mod['start_line'] - 1
            end_idx = mod['end_line'] # inclusive in report, so slice should be end_idx
            
            # Check bounds
            if start_idx < 0 or end_idx > len(lines):
                print(f"  Line mismatch in {rel_path}. Skipping.")
                continue

            indent = ""
            if lines[start_idx].strip():
                indent = lines[start_idx].split(lines[start_idx].strip()[0])[0]

            replacement = []
            
            if mod['code_type'] == 'scriptblock':
                src_ref = f"/js/{mod['extracted_file']}"
                replacement.append(f'{indent}<script src="{src_ref}"></script>\n')
                
                # Replace lines
                lines[start_idx:end_idx] = replacement
                
            elif mod['code_type'] == 'styleblock':
                href_ref = f"/css/{mod['extracted_file']}"
                replacement.append(f'{indent}<link rel="stylesheet" href="{href_ref}" />\n')
                lines[start_idx:end_idx] = replacement
                
            elif mod['code_type'] == 'inlinestyle':
                # Can't simple replace lines often line is shared
                # Inserting comment above
                 lines.insert(start_idx, f"{indent}<!-- TODO: Refactor inline style to {mod['extracted_file']} -->\n")
                 
            elif mod['code_type'] in ['onclick', 'onload', 'onmouseover', 'jsuri']:
                 lines.insert(start_idx, f"{indent}<!-- TODO: Refactor {mod['code_type']} to {mod['extracted_file']} -->\n")

        # Write content back to the file (in place, since it's a copy)
        with open(full_src_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        print(f"Modified: {full_src_path}")

    print("Refactoring complete. Full project available at:", args.output)

if __name__ == "__main__":
    main()
