import os
import glob
from typing import List, Generator
import logging
from .config import ScannerConfig

class Scanner:
    def __init__(self, config: ScannerConfig):
        self.config = config

    def scan(self) -> Generator[str, None, None]:
        """
        Recursively yields file paths that match the configuration criteria.
        """
        logging.info(f"Scanning directory: {os.path.abspath(self.config.root_folder)}")
        
        for root, dirs, files in os.walk(self.config.root_folder):
            # Modify dirs in-place to skip excluded folders
            dirs[:] = [d for d in dirs if d not in self.config.exclude_folders]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                if self._should_include(file, file_path):
                    yield file_path

    def _should_include(self, filename: str, filepath: str) -> bool:
        # Check extension
        _, ext = os.path.splitext(filename)
        if ext.lower() not in self.config.include_extensions:
            return False

        # Check glob exclusions
        for pattern in self.config.exclude_files:
            if glob.fnmatch.fnmatch(filename, pattern):
                return False

        # Check file size
        try:
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            if size_mb > self.config.max_file_size_mb:
                # Optional: Log warning about skipped large file
                return False
        except OSError:
            # File might be inaccessible
            return False

        return True
