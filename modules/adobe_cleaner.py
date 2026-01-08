"""
Adobe Temporary Files Cleaner Module
Scans and removes temporary files created by Adobe applications
"""

import os
import logging
from pathlib import Path


class AdobeTempCleaner:
    """Handles scanning and cleaning of Adobe temporary files"""
    
    def __init__(self):
        # Adobe temp file locations
        self.adobe_locations = [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Adobe'),
            os.path.join(os.environ.get('APPDATA', ''), 'Adobe'),
            os.path.join(os.environ.get('TEMP', ''), 'Adobe'),
            os.path.join(tempfile.gettempdir(), 'Adobe'),
            os.path.join(os.path.expanduser('~'), 'Documents', 'Adobe'),
        ]
        
        # Adobe temp file patterns
        self.adobe_temp_patterns = [
            'AdobeTemp',
            'Adobe_temp',
            'acrobat_tmp',
            'AcroCEF',
            'Acrobat',
        ]
        
    def scan(self, progress_callback, status_callback):
        """
        Scan for Adobe temporary files
        
        Args:
            progress_callback: Function to call with progress updates (0-100)
            status_callback: Function to call with status messages
            
        Returns:
            List of dictionaries with file information
        """
        results = []
        total_locations = len(self.adobe_locations)
        
        status_callback("Scanning for Adobe temporary files...")
        
        for idx, location in enumerate(self.adobe_locations):
            if not os.path.exists(location):
                continue
                
            try:
                status_callback(f"Scanning: {location}")
                files = self._scan_adobe_directory(location)
                results.extend(files)
                
                progress = int((idx + 1) / total_locations * 100)
                progress_callback(progress)
                
            except Exception as e:
                logging.error(f"Error scanning Adobe location {location}: {str(e)}")
                
        return results
        
    def _scan_adobe_directory(self, directory):
        """Scan an Adobe directory for temporary files"""
        files = []
        
        try:
            for root, dirs, filenames in os.walk(directory):
                # Check if this is a temp directory
                is_temp_dir = any(pattern.lower() in root.lower() 
                                 for pattern in ['temp', 'cache', 'tmp'])
                
                try:
                    os.listdir(root)
                except PermissionError:
                    continue
                    
                for filename in filenames:
                    try:
                        filepath = os.path.join(root, filename)
                        
                        # Include files from temp directories or with temp patterns
                        if is_temp_dir or any(pattern.lower() in filename.lower() 
                                             for pattern in self.adobe_temp_patterns):
                            if os.path.exists(filepath):
                                size = os.path.getsize(filepath)
                                
                                files.append({
                                    'path': filepath,
                                    'size': size,
                                    'name': filename
                                })
                    except (PermissionError, OSError):
                        continue
                        
        except Exception as e:
            logging.error(f"Error in _scan_adobe_directory: {str(e)}")
            
        return files


import tempfile

