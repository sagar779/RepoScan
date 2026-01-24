import configparser
import os
import argparse
from typing import List, Set
import logging

class ScannerConfig:
    def __init__(self):
        self.root_folder: str = "."
        self.output_folder: str = "."
        self.include_extensions: Set[str] = set()
        self.max_file_size_mb: int = 10
        self.snippet_max_length: int = 500
        # Phase 2 Args
        self.target_url: str = None
        self.mode: str = "static" # static, dynamic, combined, extract

    @classmethod
    def load(cls, config_path: str = "config.ini") -> 'ScannerConfig':
        config = cls()
        parser = configparser.ConfigParser()
        
        if os.path.exists(config_path):
            parser.read(config_path)
        else:
            logging.warning(f"Configuration file '{config_path}' not found. Using defaults.")

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
    parser = argparse.ArgumentParser(description="RepoScan-Analyser: Static & Dynamic Assessment Utility")
    parser.add_argument("--config", default="config.ini", help="Path to configuration file")
    parser.add_argument("--root", help="Root folder to scan (overrides config)")
    parser.add_argument("--output", help="Output folder (overrides config)")
    parser.add_argument("--url", help="Target URL for Dynamic/Combined scan")
    
    # Action Flags
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--static-analysis", action="store_true", help="Run Static Scan (Default)")
    group.add_argument("--dynamic-analysis", action="store_true", help="Run Dynamic Crawler only")
    group.add_argument("--extract", action="store_true", help="Run Code Extraction based on Tracker")
    group.add_argument("--all", action="store_true", help="Run Static Scan + Extraction")
    
    args = parser.parse_args()
    
    config = ScannerConfig.load(args.config)
    
    # Logic to map flags to mode string
    if args.extract:
        config.mode = "extract"
    elif args.dynamic_analysis:
        config.mode = "dynamic"
    elif args.all:
        config.mode = "all"
    else:
        config.mode = "static" # Default or explicit --static-analysis
    
    if args.root:
        config.root_folder = args.root
    if args.output:
        config.output_folder = args.output
    if args.url:
        config.target_url = args.url
        
    config.validate()
    return config
