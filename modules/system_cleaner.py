"""
System File Cleaner Module
Scans and removes old system files (Windows updates, installers, etc.)
"""

import os
import logging
from pathlib import Path


class SystemFileCleaner:
    """Handles scanning and cleaning of old system files"""
    
    def __init__(self):
        # System file locations
        self.system_locations = [
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'SoftwareDistribution', 'Download'),
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Prefetch'),
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Logs'),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp'),
        ]
        
        # Installer file extensions
        self.installer_extensions = [
            '.msi', '.msp', '.msu', '.exe'
        ]
        
    def scan(self, progress_callback, status_callback):
        """
        Scan for old system files
        
        Args:
            progress_callback: Function to call with progress updates (0-100)
            status_callback: Function to call with status messages
            
        Returns:
            List of dictionaries with file information
        """
        results = []
        
        status_callback("Scanning system directories...")
        
        total_locations = len(self.system_locations)
        
        for idx, location in enumerate(self.system_locations):
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
                
        # Also scan for old installers in user downloads
        downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        if os.path.exists(downloads_dir):
            try:
                status_callback(f"Scanning: {downloads_dir}")
                installer_files = self._scan_for_installers(downloads_dir)
                results.extend(installer_files)
            except Exception as e:
                logging.error(f"Error scanning downloads: {str(e)}")
                
        return results
        
    def _scan_directory(self, directory):
        """Scan a directory for system files"""
        files = []
        
        try:
            for root, dirs, filenames in os.walk(directory):
                try:
                    os.listdir(root)
                except PermissionError:
                    continue
                    
                for filename in filenames:
                    try:
                        filepath = os.path.join(root, filename)
                        
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
        
    def _scan_for_installers(self, directory):
        """Scan for old installer files"""
        files = []
        
        try:
            for item in os.listdir(directory):
                try:
                    filepath = os.path.join(directory, item)
                    
                    if os.path.isfile(filepath):
                        ext = os.path.splitext(filepath)[1].lower()
                        if ext in self.installer_extensions:
                            size = os.path.getsize(filepath)
                            
                            files.append({
                                'path': filepath,
                                'size': size,
                                'name': item
                            })
                except (PermissionError, OSError):
                    continue
                    
        except (PermissionError, OSError):
            pass
            
        return files

