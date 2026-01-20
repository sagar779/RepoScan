import os
import collections

class Scanner:
    def __init__(self, target_dir):
        self.target_dir = os.path.abspath(target_dir)
        self.file_inventory = []
        self.directory_stats = collections.defaultdict(lambda: {'count': 0, 'lines': 0})

    def count_lines(self, filepath):
        """Counts lines in a file efficiently, handling encoding errors."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return 0

    def scan(self):
        """Walks the directory and collects metadata."""
        print(f"Scanning directory: {self.target_dir}")
        for root, dirs, files in os.walk(self.target_dir):
            
            # Directory Metadata
            rel_dir = os.path.relpath(root, self.target_dir)
            if rel_dir == '.':
                rel_dir = '(Root)'
            
            # Calculate depth (0 for root, 1 for subfolder, etc.)
            depth = 0 if rel_dir == '(Root)' else rel_dir.count(os.sep) + 1

            for file in files:
                file_path = os.path.join(root, file)
                size_kb = os.path.getsize(file_path) / 1024
                
                # Get extension
                _, ext = os.path.splitext(file)
                if not ext:
                    ext = "(No Extension)"
                else:
                    ext = ext.lower()
                
                # Count lines (Metadata depth)
                lines = self.count_lines(file_path)
                
                # Update Inventory
                self.file_inventory.append({
                    'Directory': rel_dir,
                    'Filename': file,
                    'Extension': ext,
                    'Size_KB': round(size_kb, 2),
                    'Line_Count': lines,
                    'Full_Path': file_path
                })
                
                # Update Directory Stats
                stats = self.directory_stats[rel_dir]
                stats['count'] += 1
                stats['lines'] += lines
                stats['depth'] = depth
                if 'extensions' not in stats:
                    stats['extensions'] = collections.defaultdict(int)
                stats['extensions'][ext] += 1

        print(f"Scan complete. Found {len(self.file_inventory)} files.")
        return self.file_inventory, self.directory_stats
