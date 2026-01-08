"""
Duplicate File Finder Module
Finds duplicate files by comparing file content hashes
"""

import os
import hashlib
import logging
from collections import defaultdict


class DuplicateFileFinder:
    """Handles finding duplicate files based on content hash"""
    
    def __init__(self):
        self.chunk_size = 8192
        
    def scan(self, directory, progress_callback, status_callback):
        """
        Scan for duplicate files
        
        Args:
            directory: Directory to scan
            progress_callback: Function to call with progress updates (0-100)
            status_callback: Function to call with status messages
            
        Returns:
            List of dictionaries with duplicate file information
        """
        results = []
        
        status_callback("Building file list...")
        
        # First, collect all files
        all_files = []
        try:
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    try:
                        if os.path.exists(filepath) and os.path.isfile(filepath):
                            size = os.path.getsize(filepath)
                            all_files.append((filepath, size))
                    except (PermissionError, OSError):
                        continue
        except Exception as e:
            logging.error(f"Error collecting files: {str(e)}")
            return results
            
        if not all_files:
            return results
            
        status_callback(f"Found {len(all_files)} files. Comparing...")
        
        # Group files by size first (quick duplicate check)
        size_groups = defaultdict(list)
        for filepath, size in all_files:
            if size > 0:  # Skip empty files
                size_groups[size].append(filepath)
                
        # Filter to only groups with potential duplicates
        potential_duplicates = {size: files for size, files in size_groups.items() if len(files) > 1}
        
        if not potential_duplicates:
            status_callback("No duplicates found")
            return results
            
        # Hash files that have the same size
        hash_groups = defaultdict(list)
        total_files = sum(len(files) for files in potential_duplicates.values())
        processed = 0
        
        for size, files in potential_duplicates.items():
            for filepath in files:
                try:
                    status_callback(f"Hashing: {os.path.basename(filepath)}")
                    file_hash = self._hash_file(filepath)
                    if file_hash:
                        hash_groups[file_hash].append((filepath, size))
                        
                    processed += 1
                    progress = int(processed / total_files * 100)
                    progress_callback(progress)
                    
                except Exception as e:
                    logging.error(f"Error hashing {filepath}: {str(e)}")
                    continue
                    
        # Collect duplicates (keep first occurrence, mark others as duplicates)
        for file_hash, file_list in hash_groups.items():
            if len(file_list) > 1:
                # Keep the first file, mark others as duplicates
                original = file_list[0]
                for filepath, size in file_list[1:]:
                    results.append({
                        'path': filepath,
                        'size': size,
                        'name': os.path.basename(filepath),
                        'duplicate_of': original[0]
                    })
                    
        return results
        
    def _hash_file(self, filepath):
        """
        Calculate MD5 hash of a file
        
        Args:
            filepath: Path to file
            
        Returns:
            MD5 hash string or None if error
        """
        try:
            hasher = hashlib.md5()
            
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    hasher.update(chunk)
                    
            return hasher.hexdigest()
            
        except Exception as e:
            logging.error(f"Error hashing file {filepath}: {str(e)}")
            return None

