"""
Large File Scanner Module
Scans for files larger than a specified size threshold
"""

import os
import logging
from pathlib import Path


class LargeFileScanner:
    """Handles scanning for large files"""
    
    def __init__(self):
        pass
        
    def scan(self, size_mb, progress_callback, status_callback):
        """
        Scan for large files
        
        Args:
            size_mb: Minimum file size in megabytes
            progress_callback: Function to call with progress updates (0-100)
            status_callback: Function to call with status messages
            
        Returns:
            List of dictionaries with file information
        """
        results = []
        size_bytes = size_mb * 1024 * 1024
        
        status_callback(f"Scanning for files larger than {size_mb} MB...")
        
        # Scan user directory
        user_dir = os.path.expanduser('~')
        
        try:
            files = self._scan_directory(user_dir, size_bytes, progress_callback, status_callback)
            results.extend(files)
            
            progress_callback(100)
            
        except Exception as e:
            logging.error(f"Error scanning for large files: {str(e)}")
            
        return results
        
    def _scan_directory(self, directory, size_threshold, progress_callback, status_callback, max_depth=4, current_depth=0):
        """
        Scan a directory for large files
        
        Args:
            directory: Directory to scan
            size_threshold: Minimum file size in bytes
            progress_callback: Progress callback
            status_callback: Status callback
            max_depth: Maximum recursion depth
            current_depth: Current recursion depth
        """
        files = []
        
        if current_depth >= max_depth:
            return files
            
        try:
            for item in os.listdir(directory):
                try:
                    filepath = os.path.join(directory, item)
                    
                    # Skip system directories
                    if os.path.isdir(filepath):
                        if item.lower() not in ['windows', 'program files', 'program files (x86)',
                                                 'programdata', '$recycle.bin', 'system volume information',
                                                 'appdata']:
                            status_callback(f"Scanning: {filepath[:50]}...")
                            files.extend(self._scan_directory(
                                filepath, size_threshold, progress_callback, 
                                status_callback, max_depth, current_depth + 1
                            ))
                    else:
                        # Check file size
                        try:
                            size = os.path.getsize(filepath)
                            if size >= size_threshold:
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

