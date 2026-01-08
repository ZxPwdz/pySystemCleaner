"""
Junk File Cleaner Module
Scans and removes common junk files (.log, .tmp, .bak, etc.)
"""

import os
import logging
from pathlib import Path


class JunkFileCleaner:
    """Handles scanning and cleaning of junk files"""
    
    def __init__(self):
        self.junk_extensions = [
            '.tmp', '.temp', '.log', '.bak', '.old', '.~',
            '.dmp', '.cache', '.chk', '.gid', '.dir'
        ]
        
        # Common locations to scan
        self.scan_locations = [
            os.path.expanduser('~'),
            'C:\\',
        ]
        
    def scan(self, progress_callback, status_callback):
        """
        Scan for junk files
        
        Args:
            progress_callback: Function to call with progress updates (0-100)
            status_callback: Function to call with status messages
            
        Returns:
            List of dictionaries with file information
        """
        results = []
        
        status_callback("Scanning for junk files...")
        
        # Focus on user directory and common locations
        user_dir = os.path.expanduser('~')
        
        try:
            status_callback(f"Scanning: {user_dir}")
            files = self._scan_directory(user_dir, max_depth=3)
            results.extend(files)
            
            progress_callback(100)
            
        except Exception as e:
            logging.error(f"Error scanning for junk files: {str(e)}")
            
        return results
        
    def _scan_directory(self, directory, current_depth=0, max_depth=3):
        """
        Scan a directory for junk files
        
        Args:
            directory: Directory to scan
            current_depth: Current recursion depth
            max_depth: Maximum recursion depth
        """
        files = []
        
        if current_depth >= max_depth:
            return files
            
        try:
            for item in os.listdir(directory):
                try:
                    filepath = os.path.join(directory, item)
                    
                    # Skip system and hidden directories
                    if os.path.isdir(filepath):
                        if item.lower() not in ['windows', 'program files', 'program files (x86)', 
                                                 'programdata', '$recycle.bin', 'system volume information']:
                            files.extend(self._scan_directory(filepath, current_depth + 1, max_depth))
                    else:
                        # Check if file has junk extension
                        ext = os.path.splitext(filepath)[1].lower()
                        if ext in self.junk_extensions:
                            try:
                                size = os.path.getsize(filepath)
                                files.append({
                                    'path': filepath,
                                    'size': size,
                                    'name': item
                                })
                            except OSError:
                                continue
                                
                except (PermissionError, OSError):
                    continue
                    
        except (PermissionError, OSError):
            pass
            
        return files

