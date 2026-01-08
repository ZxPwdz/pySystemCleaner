"""
Registry Cleaner Module
Scans and removes invalid or obsolete Windows registry entries
"""

import os
import logging
import winreg
import datetime


class RegistryCleaner:
    """Handles scanning and cleaning of Windows registry"""
    
    def __init__(self):
        # Registry paths to scan for invalid entries
        self.scan_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs"),
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache"),
        ]
        
    def scan(self, progress_callback, status_callback):
        """
        Scan registry for issues
        
        Args:
            progress_callback: Function to call with progress updates (0-100)
            status_callback: Function to call with status messages
            
        Returns:
            List of dictionaries with registry issue information
        """
        results = []
        
        try:
            import winreg
        except ImportError:
            status_callback("Registry cleaning is only available on Windows")
            return results
            
        status_callback("Scanning Windows Registry...")
        
        total_paths = len(self.scan_paths)
        
        for idx, (hkey, subkey) in enumerate(self.scan_paths):
            try:
                status_callback(f"Scanning: {subkey}")
                issues = self._scan_registry_key(hkey, subkey)
                results.extend(issues)
                
                progress = int((idx + 1) / total_paths * 100)
                progress_callback(progress)
                
            except Exception as e:
                logging.error(f"Error scanning registry key {subkey}: {str(e)}")
                
        return results
        
    def _scan_registry_key(self, hkey, subkey):
        """
        Scan a specific registry key for issues
        
        Args:
            hkey: Root key (e.g., HKEY_CURRENT_USER)
            subkey: Subkey path
            
        Returns:
            List of issues found
        """
        issues = []
        
        try:
            key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ)
            
            # Check for invalid file references
            try:
                i = 0
                while True:
                    try:
                        value_name, value_data, value_type = winreg.EnumValue(key, i)
                        
                        # Check if value points to a non-existent file
                        if isinstance(value_data, str):
                            if value_data.endswith('.exe') or value_data.endswith('.dll'):
                                if not os.path.exists(value_data):
                                    issues.append({
                                        'key': f"{subkey}\\{value_name}",
                                        'value': value_data,
                                        'issue': 'File not found'
                                    })
                                    
                        i += 1
                    except OSError:
                        break
                        
            finally:
                winreg.CloseKey(key)
                
        except WindowsError as e:
            logging.error(f"Error accessing registry key {subkey}: {str(e)}")
            
        return issues
        
    def backup_registry(self):
        """
        Create a registry backup
        
        Returns:
            Path to backup file or None
        """
        try:
            backup_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'PCCleaner_Backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f'registry_backup_{timestamp}.reg')
            
            # Export registry using regedit
            os.system(f'regedit /e "{backup_file}" HKEY_CURRENT_USER\\Software')
            
            logging.info(f"Registry backup created: {backup_file}")
            return backup_file
            
        except Exception as e:
            logging.error(f"Error creating registry backup: {str(e)}")
            return None
            
    def delete_key(self, key_path):
        """
        Delete a registry key value
        
        Args:
            key_path: Full key path including value name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Parse the key path
            parts = key_path.split('\\')
            if len(parts) < 2:
                return False
                
            subkey = '\\'.join(parts[:-1])
            value_name = parts[-1]
            
            # Open and delete
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey, 0, winreg.KEY_WRITE)
            try:
                winreg.DeleteValue(key, value_name)
                logging.info(f"Deleted registry value: {key_path}")
                return True
            finally:
                winreg.CloseKey(key)
                
        except Exception as e:
            logging.error(f"Error deleting registry key {key_path}: {str(e)}")
            return False

