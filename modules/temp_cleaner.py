"""
Temporary Files Cleaner Module
Scans and removes temporary files from system locations
"""

import os
import tempfile
import logging
from pathlib import Path


class TempFileCleaner:
    """Handles scanning and cleaning of temporary files"""
    
    def __init__(self):
        self.temp_locations = [
            tempfile.gettempdir(),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp'),
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Temp'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'INetCache'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Temporary Internet Files'),
        ]
        
    def scan(self, progress_callback, status_callback):
        """
        Scan for temporary files
        
        Args:
            progress_callback: Function to call with progress updates (0-100)
            status_callback: Function to call with status messages
            
        Returns:
            List of dictionaries with file information
        """
        results = []
        total_locations = len(self.temp_locations)
        
        status_callback("Scanning temporary file locations...")
        
        for idx, location in enumerate(self.temp_locations):
            if not os.path.exists(location):
                continue
                
            try:
                status_callback(f"Scanning: {location}")
                files = self._scan_directory(location)
                results.extend(files)
                
                progress = int((idx + 1) / total_locations * 100)
                progress_callback(progress)
                
            except Exception as e:
                logging.error(f"Error scanning {location}: {str(e)}")
                
        return results
        
    def _scan_directory(self, directory):
        """Scan a directory for temporary files"""
        files = []
        
        try:
            for root, dirs, filenames in os.walk(directory):
                # Skip if we don't have permissions
                try:
                    os.listdir(root)
                except PermissionError:
                    continue
                    
                for filename in filenames:
                    try:
                        filepath = os.path.join(root, filename)
                        
                        # Skip if file is in use
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
            logging.error(f"Error in _scan_directory: {str(e)}")
            
        return files

