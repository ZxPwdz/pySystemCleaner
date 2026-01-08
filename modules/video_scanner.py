"""
Video File Scanner Module
Scans for large video files older than a specified age
"""

import os
import time
import logging
from datetime import datetime, timedelta


class VideoFileScanner:
    """Handles scanning for old video files"""
    
    def __init__(self):
        self.video_extensions = [
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', 
            '.webm', '.m4v', '.mpg', '.mpeg', '.3gp', '.f4v'
        ]
        
    def scan(self, age_days, progress_callback, status_callback):
        """
        Scan for old video files
        
        Args:
            age_days: Minimum age in days
            progress_callback: Function to call with progress updates (0-100)
            status_callback: Function to call with status messages
            
        Returns:
            List of dictionaries with file information
        """
        results = []
        cutoff_date = time.time() - (age_days * 24 * 60 * 60)
        
        status_callback(f"Scanning for video files older than {age_days} days...")
        
        # Common video locations
        video_locations = [
            os.path.join(os.path.expanduser('~'), 'Videos'),
            os.path.join(os.path.expanduser('~'), 'Downloads'),
            os.path.join(os.path.expanduser('~'), 'Desktop'),
            os.path.join(os.path.expanduser('~'), 'Documents'),
        ]
        
        total_locations = len(video_locations)
        
        for idx, location in enumerate(video_locations):
            if not os.path.exists(location):
                continue
                
            try:
                status_callback(f"Scanning: {location}")
                files = self._scan_directory(location, cutoff_date)
                results.extend(files)
                
                progress = int((idx + 1) / total_locations * 100)
                progress_callback(progress)
                
            except Exception as e:
                logging.error(f"Error scanning {location}: {str(e)}")
                
        return results
        
    def _scan_directory(self, directory, cutoff_date, max_depth=3, current_depth=0):
        """
        Scan a directory for old video files
        
        Args:
            directory: Directory to scan
            cutoff_date: Unix timestamp cutoff
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
                    
                    if os.path.isdir(filepath):
                        files.extend(self._scan_directory(
                            filepath, cutoff_date, max_depth, current_depth + 1
                        ))
                    else:
                        # Check if it's a video file
                        ext = os.path.splitext(filepath)[1].lower()
                        if ext in self.video_extensions:
                            # Check file age and size
                            try:
                                stat = os.stat(filepath)
                                if stat.st_mtime < cutoff_date:
                                    files.append({
                                        'path': filepath,
                                        'size': stat.st_size,
                                        'name': item,
                                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
                                    })
                            except OSError:
                                continue
                                
                except (PermissionError, OSError):
                    continue
                    
        except (PermissionError, OSError):
            pass
            
        return files

