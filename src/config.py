import configparser
import os
import argparse
from typing import List, Set

class ScannerConfig:
    def __init__(self):
        self.root_folder: str = "."
        self.output_folder: str = "."
        self.include_extensions: Set[str] = set()
        self.exclude_folders: Set[str] = set()
        self.exclude_files: Set[str] = set()
        self.max_file_size_mb: int = 10
        self.snippet_max_length: int = 500

    @classmethod
    def load(cls, config_path: str = "config.ini") -> 'ScannerConfig':
        config = cls()
        parser = configparser.ConfigParser()
        
        if os.path.exists(config_path):
            parser.read(config_path)
        else:
            print(f"Warning: Configuration file '{config_path}' not found. Using defaults.")

        # Paths
        if 'Paths' in parser:
            config.root_folder = parser['Paths'].get('root_folder', '.')
            config.output_folder = parser['Paths'].get('output_folder', '.')

        # Filters
        if 'Filters' in parser:
            exts = parser['Filters'].get('include_extensions', '')
            config.include_extensions = {e.strip().lower() for e in exts.split(',') if e.strip()}
            
            folders = parser['Filters'].get('exclude_folders', '')
            config.exclude_folders = {f.strip() for f in folders.split(',') if f.strip()}
            
            files = parser['Filters'].get('exclude_files', '')
            config.exclude_files = {f.strip() for f in files.split(',') if f.strip()}

        # Limits
        if 'Limits' in parser:
            config.max_file_size_mb = int(parser['Limits'].get('max_file_size_mb', 10))
            config.snippet_max_length = int(parser['Limits'].get('snippet_max_length', 500))

        return config

    def validate(self):
        if not os.path.exists(self.root_folder):
            raise ValueError(f"Root folder does not exist: {self.root_folder} (Absolute: {os.path.abspath(self.root_folder)})")
        if not os.path.exists(self.output_folder):
            try:
                os.makedirs(self.output_folder)
            except OSError as e:
                raise ValueError(f"Could not create output folder: {self.output_folder}. Error: {e}")

def parse_arguments() -> ScannerConfig:
    parser = argparse.ArgumentParser(description="Inline Code Detection Utility")
    parser.add_argument("--config", default="config.ini", help="Path to configuration file")
    parser.add_argument("--root", help="Root folder to scan (overrides config)")
    parser.add_argument("--output", help="Output folder (overrides config)")
    
    args = parser.parse_args()
    
    config = ScannerConfig.load(args.config)
    
    if args.root:
        config.root_folder = args.root
    if args.output:
        config.output_folder = args.output
        
    config.validate()
    return config
