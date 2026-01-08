"""
DNS Cache Cleaner Module
Clears the system DNS cache
"""

import subprocess
import logging
import platform


class DNSCleaner:
    """Handles clearing DNS cache"""
    
    def __init__(self):
        self.system = platform.system()
        
    def clear_cache(self):
        """
        Clear DNS cache
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if self.system == "Windows":
                result = subprocess.run(
                    ["ipconfig", "/flushdns"],
                    capture_output=True,
                    text=True,
                    shell=True
                )
                
                if result.returncode == 0:
                    logging.info("DNS cache cleared successfully")
                    return (True, "DNS cache cleared successfully!")
                else:
                    error_msg = result.stderr or "Unknown error"
                    logging.error(f"Failed to clear DNS cache: {error_msg}")
                    return (False, f"Failed to clear DNS cache: {error_msg}")
                    
            elif self.system == "Darwin":  # macOS
                result = subprocess.run(
                    ["dscacheutil", "-flushcache"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Also clear mDNSResponder
                    subprocess.run(["killall", "-HUP", "mDNSResponder"])
                    logging.info("DNS cache cleared successfully")
                    return (True, "DNS cache cleared successfully!")
                else:
                    error_msg = result.stderr or "Unknown error"
                    logging.error(f"Failed to clear DNS cache: {error_msg}")
                    return (False, f"Failed to clear DNS cache: {error_msg}")
                    
            elif self.system == "Linux":
                # Try systemd-resolved first
                result = subprocess.run(
                    ["systemd-resolve", "--flush-caches"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    logging.info("DNS cache cleared successfully")
                    return (True, "DNS cache cleared successfully!")
                else:
                    # Try nscd
                    result = subprocess.run(
                        ["sudo", "service", "nscd", "restart"],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        logging.info("DNS cache cleared successfully")
                        return (True, "DNS cache cleared successfully!")
                    else:
                        return (False, "Unable to clear DNS cache. May require administrator privileges.")
            else:
                return (False, f"DNS cache clearing not supported on {self.system}")
                
        except Exception as e:
            error_msg = f"Error clearing DNS cache: {str(e)}"
            logging.error(error_msg)
            return (False, error_msg)

