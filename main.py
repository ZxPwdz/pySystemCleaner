"""
PC Cleaner Application
A comprehensive system cleaning tool with multiple features.
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QListWidget,
    QLabel, QProgressBar, QWidget, QHBoxLayout, QFileDialog, QMessageBox,
    QDialog, QSpinBox, QDialogButtonBox, QGridLayout, QCheckBox,
    QScrollArea, QGroupBox, QTextEdit, QTabWidget, QLineEdit
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from datetime import datetime
import logging

# Import cleaning modules
from modules.temp_cleaner import TempFileCleaner
from modules.junk_cleaner import JunkFileCleaner
from modules.adobe_cleaner import AdobeTempCleaner
from modules.large_file_scanner import LargeFileScanner
from modules.duplicate_finder import DuplicateFileFinder
from modules.video_scanner import VideoFileScanner
from modules.registry_cleaner import RegistryCleaner
from modules.dns_cleaner import DNSCleaner
from modules.system_cleaner import SystemFileCleaner

# Setup logging
logging.basicConfig(
    filename='pc_cleaner.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class ScanThread(QThread):
    """Background thread for scanning operations"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(list)
    
    def __init__(self, scan_func, *args):
        super().__init__()
        self.scan_func = scan_func
        self.args = args
        
    def run(self):
        try:
            # Create wrapper functions to emit signals
            def progress_callback(value):
                self.progress.emit(value)
                
            def status_callback(message):
                self.status.emit(message)
            
            results = self.scan_func(*self.args, progress_callback, status_callback)
            self.finished.emit(results)
        except Exception as e:
            logging.error(f"Scan error: {str(e)}")
            self.status.emit(f"Error: {str(e)}")
            self.finished.emit([])


class SettingsDialog(QDialog):
    """Settings dialog for customization"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Large file threshold
        group_large = QGroupBox("Large File Scanner")
        layout_large = QHBoxLayout()
        layout_large.addWidget(QLabel("File size threshold (MB):"))
        self.spin_file_size = QSpinBox()
        self.spin_file_size.setRange(10, 10000)
        self.spin_file_size.setValue(100)
        layout_large.addWidget(self.spin_file_size)
        group_large.setLayout(layout_large)
        layout.addWidget(group_large)
        
        # Video file age
        group_video = QGroupBox("Video File Scanner")
        layout_video = QHBoxLayout()
        layout_video.addWidget(QLabel("File age (days):"))
        self.spin_video_age = QSpinBox()
        self.spin_video_age.setRange(30, 3650)
        self.spin_video_age.setValue(365)
        layout_video.addWidget(self.spin_video_age)
        group_video.setLayout(layout_video)
        layout.addWidget(group_video)
        
        # Registry backup
        group_registry = QGroupBox("Registry Cleaner")
        layout_registry = QVBoxLayout()
        self.check_registry_backup = QCheckBox("Create backup before cleaning")
        self.check_registry_backup.setChecked(True)
        layout_registry.addWidget(self.check_registry_backup)
        group_registry.setLayout(layout_registry)
        layout.addWidget(group_registry)
        
        # Scan depth
        group_scan = QGroupBox("Scan Options")
        layout_scan = QVBoxLayout()
        self.check_deep_scan = QCheckBox("Deep scan (slower but more thorough)")
        self.check_deep_scan.setChecked(False)
        layout_scan.addWidget(self.check_deep_scan)
        group_scan.setLayout(layout_scan)
        layout.addWidget(group_scan)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class PCCleanerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Cleaner - System Optimization Tool")
        self.setMinimumSize(QSize(900, 650))
        
        # Initialize cleaners
        self.temp_cleaner = TempFileCleaner()
        self.junk_cleaner = JunkFileCleaner()
        self.adobe_cleaner = AdobeTempCleaner()
        self.large_scanner = LargeFileScanner()
        self.duplicate_finder = DuplicateFileFinder()
        self.video_scanner = VideoFileScanner()
        self.registry_cleaner = RegistryCleaner()
        self.dns_cleaner = DNSCleaner()
        self.system_cleaner = SystemFileCleaner()
        
        # Settings
        self.settings = {
            'file_size_mb': 100,
            'video_age_days': 365,
            'registry_backup': True,
            'deep_scan': False
        }
        
        self.scan_results = []
        self.current_scan_type = None
        
        self.init_ui()
        logging.info("PC Cleaner application started")
        
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_label = QLabel("🧹 PC Cleaner")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)
        
        version_label = QLabel("Version 1.0 - System Optimization Tool")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(version_label)
        
        # Create tab widget for better organization
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Tab 1: File Cleaners
        tab_files = QWidget()
        layout_files = QVBoxLayout(tab_files)
        
        # File cleaning buttons group
        group_file_cleaners = QGroupBox("File Cleaning Tools")
        grid_files = QGridLayout()
        
        self.btn_scan_temp = QPushButton("🗑️ Scan Temporary Files")
        self.btn_scan_temp.clicked.connect(self.scan_temp_files)
        grid_files.addWidget(self.btn_scan_temp, 0, 0)
        
        self.btn_scan_junk = QPushButton("🗑️ Scan Junk Files")
        self.btn_scan_junk.clicked.connect(self.scan_junk_files)
        grid_files.addWidget(self.btn_scan_junk, 0, 1)
        
        self.btn_scan_adobe = QPushButton("📄 Scan Adobe Temp Files")
        self.btn_scan_adobe.clicked.connect(self.scan_adobe_temp)
        grid_files.addWidget(self.btn_scan_adobe, 1, 0)
        
        self.btn_scan_system = QPushButton("⚙️ Scan Old System Files")
        self.btn_scan_system.clicked.connect(self.scan_system_files)
        grid_files.addWidget(self.btn_scan_system, 1, 1)
        
        group_file_cleaners.setLayout(grid_files)
        layout_files.addWidget(group_file_cleaners)
        
        # File scanners group
        group_scanners = QGroupBox("File Analysis Tools")
        grid_scanners = QGridLayout()
        
        self.btn_scan_large = QPushButton("📊 Scan Large Files")
        self.btn_scan_large.clicked.connect(self.scan_large_files)
        grid_scanners.addWidget(self.btn_scan_large, 0, 0)
        
        self.btn_scan_videos = QPushButton("🎬 Scan Old Video Files")
        self.btn_scan_videos.clicked.connect(self.scan_video_files)
        grid_scanners.addWidget(self.btn_scan_videos, 0, 1)
        
        self.btn_scan_duplicates = QPushButton("🔍 Find Duplicate Files")
        self.btn_scan_duplicates.clicked.connect(self.scan_duplicates)
        grid_scanners.addWidget(self.btn_scan_duplicates, 1, 0)
        
        group_scanners.setLayout(grid_scanners)
        layout_files.addWidget(group_scanners)
        
        tabs.addTab(tab_files, "File Tools")
        
        # Tab 2: System Tools
        tab_system = QWidget()
        layout_system = QVBoxLayout(tab_system)
        
        group_system = QGroupBox("System Optimization Tools")
        grid_system = QGridLayout()
        
        self.btn_clear_dns = QPushButton("🌐 Clear DNS Cache")
        self.btn_clear_dns.clicked.connect(self.clear_dns_cache)
        grid_system.addWidget(self.btn_clear_dns, 0, 0)
        
        self.btn_scan_registry = QPushButton("📝 Clean Registry")
        self.btn_scan_registry.clicked.connect(self.scan_registry)
        grid_system.addWidget(self.btn_scan_registry, 0, 1)
        
        group_system.setLayout(grid_system)
        layout_system.addWidget(group_system)
        layout_system.addStretch()
        
        tabs.addTab(tab_system, "System Tools")
        
        # Results panel
        group_results = QGroupBox("Scan Results")
        results_layout = QVBoxLayout()
        
        self.list_results = QListWidget()
        self.list_results.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        results_layout.addWidget(self.list_results)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.btn_select_all = QPushButton("Select All")
        self.btn_select_all.clicked.connect(self.select_all_items)
        action_layout.addWidget(self.btn_select_all)
        
        self.btn_deselect_all = QPushButton("Deselect All")
        self.btn_deselect_all.clicked.connect(self.deselect_all_items)
        action_layout.addWidget(self.btn_deselect_all)
        
        self.btn_delete_selected = QPushButton("🗑️ Delete Selected")
        self.btn_delete_selected.clicked.connect(self.delete_selected_items)
        self.btn_delete_selected.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        action_layout.addWidget(self.btn_delete_selected)
        
        results_layout.addLayout(action_layout)
        group_results.setLayout(results_layout)
        main_layout.addWidget(group_results)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Status bar
        self.status_bar = QLabel("Ready - Select a scan option to begin")
        self.status_bar.setStyleSheet("padding: 5px; background-color: #ecf0f1;")
        main_layout.addWidget(self.status_bar)
        
        # Bottom toolbar
        toolbar_layout = QHBoxLayout()
        
        self.btn_settings = QPushButton("⚙️ Settings")
        self.btn_settings.clicked.connect(self.open_settings)
        toolbar_layout.addWidget(self.btn_settings)
        
        toolbar_layout.addStretch()
        
        self.label_total_size = QLabel("Total Size: 0 MB")
        self.label_total_size.setStyleSheet("font-weight: bold;")
        toolbar_layout.addWidget(self.label_total_size)
        
        main_layout.addLayout(toolbar_layout)
        
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self)
        dialog.spin_file_size.setValue(self.settings['file_size_mb'])
        dialog.spin_video_age.setValue(self.settings['video_age_days'])
        dialog.check_registry_backup.setChecked(self.settings['registry_backup'])
        dialog.check_deep_scan.setChecked(self.settings['deep_scan'])
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings['file_size_mb'] = dialog.spin_file_size.value()
            self.settings['video_age_days'] = dialog.spin_video_age.value()
            self.settings['registry_backup'] = dialog.check_registry_backup.isChecked()
            self.settings['deep_scan'] = dialog.check_deep_scan.isChecked()
            logging.info(f"Settings updated: {self.settings}")
            
    def start_scan(self, scan_func, scan_type, *args):
        """Start a background scan operation"""
        self.current_scan_type = scan_type
        self.scan_results = []
        self.list_results.clear()
        self.progress_bar.setValue(0)
        
        # Disable all scan buttons
        self.set_buttons_enabled(False)
        
        # Create and start scan thread
        self.scan_thread = ScanThread(scan_func, *args)
        self.scan_thread.progress.connect(self.update_progress)
        self.scan_thread.status.connect(self.update_status)
        self.scan_thread.finished.connect(self.scan_finished)
        self.scan_thread.start()
        
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        
    def update_status(self, message):
        """Update status label"""
        self.status_bar.setText(message)
        
    def scan_finished(self, results):
        """Handle scan completion"""
        self.scan_results = results
        self.populate_results(results)
        self.set_buttons_enabled(True)
        self.progress_bar.setValue(100)
        
        if results:
            total_size = sum(item.get('size', 0) for item in results)
            size_mb = total_size / (1024 * 1024)
            self.label_total_size.setText(f"Total Size: {size_mb:.2f} MB")
            self.status_bar.setText(f"Scan complete - Found {len(results)} items ({size_mb:.2f} MB)")
            logging.info(f"{self.current_scan_type} scan completed: {len(results)} items, {size_mb:.2f} MB")
        else:
            self.label_total_size.setText("Total Size: 0 MB")
            self.status_bar.setText("Scan complete - No items found")
            
    def populate_results(self, results):
        """Populate the results list"""
        self.list_results.clear()
        for item in results:
            display_text = self.format_result_item(item)
            self.list_results.addItem(display_text)
            
    def format_result_item(self, item):
        """Format a result item for display"""
        path = item.get('path', 'Unknown')
        size = item.get('size', 0)
        size_mb = size / (1024 * 1024)
        
        if 'duplicate_of' in item:
            return f"[DUPLICATE] {path} ({size_mb:.2f} MB)"
        elif 'key' in item:
            return f"[REGISTRY] {item['key']}"
        else:
            return f"{path} ({size_mb:.2f} MB)"
            
    def set_buttons_enabled(self, enabled):
        """Enable or disable all scan buttons"""
        self.btn_scan_temp.setEnabled(enabled)
        self.btn_scan_junk.setEnabled(enabled)
        self.btn_scan_adobe.setEnabled(enabled)
        self.btn_scan_system.setEnabled(enabled)
        self.btn_scan_large.setEnabled(enabled)
        self.btn_scan_videos.setEnabled(enabled)
        self.btn_scan_duplicates.setEnabled(enabled)
        self.btn_clear_dns.setEnabled(enabled)
        self.btn_scan_registry.setEnabled(enabled)
        
    def select_all_items(self):
        """Select all items in the list"""
        self.list_results.selectAll()
        
    def deselect_all_items(self):
        """Deselect all items in the list"""
        self.list_results.clearSelection()
        
    def delete_selected_items(self):
        """Delete selected items"""
        selected_indices = [index.row() for index in self.list_results.selectedIndexes()]
        
        if not selected_indices:
            QMessageBox.warning(self, "No Selection", "Please select items to delete.")
            return
            
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {len(selected_indices)} selected items?\n\n"
            "This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.perform_deletion(selected_indices)
            
    def perform_deletion(self, indices):
        """Perform the actual deletion"""
        deleted_count = 0
        failed_count = 0
        total_size = 0
        
        self.progress_bar.setValue(0)
        
        for i, idx in enumerate(sorted(indices, reverse=True)):
            if 0 <= idx < len(self.scan_results):
                item = self.scan_results[idx]
                
                try:
                    if self.current_scan_type == "registry":
                        # Handle registry deletion
                        if self.registry_cleaner.delete_key(item['key']):
                            deleted_count += 1
                            logging.info(f"Deleted registry key: {item['key']}")
                    else:
                        # Handle file deletion
                        path = item.get('path')
                        if path and os.path.exists(path):
                            size = os.path.getsize(path)
                            os.remove(path)
                            deleted_count += 1
                            total_size += size
                            logging.info(f"Deleted file: {path}")
                except Exception as e:
                    failed_count += 1
                    logging.error(f"Failed to delete {item}: {str(e)}")
                    
            progress = int((i + 1) / len(indices) * 100)
            self.progress_bar.setValue(progress)
            
        # Remove deleted items from results and list
        for idx in sorted(indices, reverse=True):
            if 0 <= idx < len(self.scan_results):
                del self.scan_results[idx]
                self.list_results.takeItem(idx)
                
        size_mb = total_size / (1024 * 1024)
        message = f"Deletion complete: {deleted_count} items deleted ({size_mb:.2f} MB freed)"
        if failed_count > 0:
            message += f", {failed_count} items failed"
            
        self.status_bar.setText(message)
        QMessageBox.information(self, "Deletion Complete", message)
        logging.info(message)
        
        # Update total size label
        remaining_size = sum(item.get('size', 0) for item in self.scan_results)
        remaining_mb = remaining_size / (1024 * 1024)
        self.label_total_size.setText(f"Total Size: {remaining_mb:.2f} MB")
        
    # Scan functions
    def scan_temp_files(self):
        """Scan for temporary files"""
        self.start_scan(self.temp_cleaner.scan, "temp_files")
        
    def scan_junk_files(self):
        """Scan for junk files"""
        self.start_scan(self.junk_cleaner.scan, "junk_files")
        
    def scan_adobe_temp(self):
        """Scan for Adobe temporary files"""
        self.start_scan(self.adobe_cleaner.scan, "adobe_temp")
        
    def scan_system_files(self):
        """Scan for old system files"""
        self.start_scan(self.system_cleaner.scan, "system_files")
        
    def scan_large_files(self):
        """Scan for large files"""
        size_mb = self.settings['file_size_mb']
        self.start_scan(self.large_scanner.scan, "large_files", size_mb)
        
    def scan_video_files(self):
        """Scan for old video files"""
        age_days = self.settings['video_age_days']
        self.start_scan(self.video_scanner.scan, "video_files", age_days)
        
    def scan_duplicates(self):
        """Scan for duplicate files"""
        # Ask user to select directory
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Scan for Duplicates")
        if directory:
            self.start_scan(self.duplicate_finder.scan, "duplicates", directory)
            
    def clear_dns_cache(self):
        """Clear DNS cache"""
        self.status_bar.setText("Clearing DNS cache...")
        success, message = self.dns_cleaner.clear_cache()
        
        if success:
            QMessageBox.information(self, "Success", message)
            logging.info("DNS cache cleared successfully")
        else:
            QMessageBox.warning(self, "Error", message)
            logging.error(f"DNS cache clear failed: {message}")
            
        self.status_bar.setText("Ready")
        
    def scan_registry(self):
        """Scan registry for issues"""
        if self.settings['registry_backup']:
            reply = QMessageBox.question(
                self,
                "Registry Backup",
                "A registry backup will be created before scanning.\n\n"
                "Do you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
                
            self.registry_cleaner.backup_registry()
            
        self.start_scan(self.registry_cleaner.scan, "registry")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    window = PCCleanerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

