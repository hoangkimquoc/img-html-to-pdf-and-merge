import os
import threading
import tempfile
from PIL import Image
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QListWidgetItem, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QThreadPool, QRunnable, QObject
from PyQt6.QtGui import QIcon, QPixmap, QImage, QImageReader

from qfluentwidgets import (
    PrimaryPushButton, PushButton, ComboBox, CheckBox, LineEdit,
    InfoBar, InfoBarPosition, SubtitleLabel, BodyLabel, isDarkTheme,
    HyperlinkButton, FluentIcon, TextEdit
)

from ...utils.drop_list_widget import DropListWidget
from ...core.config_manager import ConfigManager
from ...core.language_manager import LanguageManager
from ...core.theme_manager import ThemeManager
from ...core.html_to_pdf_converter import HtmlToPdfConverter
from ..icons import Icons

class ThumbnailSignals(QObject):
    loaded = pyqtSignal(object, QImage)

class ThumbnailRunnable(QRunnable):
    def __init__(self, path, item):
        super().__init__()
        self.path = path
        self.item = item
        self.signals = ThumbnailSignals()

    def run(self):
        try:
            reader = QImageReader(self.path)
            reader.setAutoTransform(True)
            # Read image
            img = reader.read()
            if not img.isNull():
                # Scale in thread to save main thread time
                img = img.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.signals.loaded.emit(self.item, img)
        except Exception:
            pass

class SortSignals(QObject):
    finished = pyqtSignal(list)

class SortRunnable(QRunnable):
    def __init__(self, files, sort_index):
        super().__init__()
        self.files = files[:] # Copy list
        self.sort_index = sort_index
        self.signals = SortSignals()

    def run(self):
        try:
            # 0: Name, 1: MTime, 2: CTime, 3: Size
            if self.sort_index == 0:
                self.files.sort(key=lambda x: os.path.basename(x).lower())
            elif self.sort_index == 1:
                self.files.sort(key=lambda x: os.path.getmtime(x))
            elif self.sort_index == 2:
                self.files.sort(key=lambda x: os.path.getctime(x))
            elif self.sort_index == 3:
                self.files.sort(key=lambda x: os.path.getsize(x))
            
            self.signals.finished.emit(self.files)
        except Exception:
            self.signals.finished.emit(self.files)

class ConversionSignals(QObject):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)
    progress = pyqtSignal(str)  # For progress log updates

class HomeInterface(QWidget):
    """Home interface for image to PDF conversion."""
    
    def __init__(self, config: ConfigManager, lang: LanguageManager, parent=None):
        super().__init__(parent)
        self.config = config
        self.lang = lang
        self.setObjectName("HomeInterface")
        self.image_files = []  # List of dicts: {'path': str, 'type': 'image'|'html'}
        self.output_path = "C:/KavPDF/"
        self.thread_pool = QThreadPool.globalInstance()
        self.is_converting = False
        self.cancel_event = threading.Event()
        self.temp_pdf_files = []  # Track temporary PDF files from HTML conversion
        
        self.conversion_signals = ConversionSignals()
        self.conversion_signals.finished.connect(self.on_conversion_complete)
        self.conversion_signals.failed.connect(self.on_conversion_failed)
        self.conversion_signals.progress.connect(self.log_progress)
        
        self.setup_ui()
        self.update_texts()

    # ... (skipping unchanged methods) ...



    # ... (skipping unchanged methods) ...

    def perform_conversion(self, target_path, method, files, html_to_pdf_map):
        try:
            quality = self.get_quality_setting()
            
            # Build list of files to process (replacing HTML with their temp PDFs)
            files_to_process = []
            for file_obj in files:
                path = file_obj['path']
                file_type = file_obj['type']
                
                if file_type == 'html':
                    # Use pre-converted PDF if available
                    if path in html_to_pdf_map:
                        files_to_process.append({'path': html_to_pdf_map[path], 'type': 'pdf'})
                else:
                    files_to_process.append(file_obj)
            
            if self.cancel_event.is_set():
                self._cleanup_temp_files()
                self.conversion_signals.failed.emit("Conversion cancelled")
                return
            
            # Step 2: Process based on method
            if method == 1:  # All in one
                # Process files in original order to maintain sequence
                all_pdfs_in_order = []
                
                for file_obj in files_to_process:
                    if self.cancel_event.is_set():
                        self._cleanup_temp_files()
                        self.conversion_signals.failed.emit("Conversion cancelled")
                        return
                    
                    path = file_obj['path']
                    file_type = file_obj['type']
                    
                    # If it's already a PDF (HTML converted), use directly
                    if file_type == 'pdf' or path.lower().endswith('.pdf'):
                        all_pdfs_in_order.append(path)
                    else:
                        # Convert image to temporary PDF
                        try:
                            img = self.process_image(path)
                            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                            temp_pdf.close()
                            temp_pdf_path = temp_pdf.name
                            self.temp_pdf_files.append(temp_pdf_path)
                            
                            img.save(temp_pdf_path, "PDF", quality=quality)
                            all_pdfs_in_order.append(temp_pdf_path)
                        except Exception as e:
                            print(f"Failed to convert image {path}: {e}")
                
                if self.cancel_event.is_set():
                    self._cleanup_temp_files()
                    self.conversion_signals.failed.emit("Conversion cancelled")
                    return
                
                # Merge all PDFs in order using pypdf
                if all_pdfs_in_order:
                    try:
                        from pypdf import PdfWriter
                        
                        merger = PdfWriter()
                        for pdf_path in all_pdfs_in_order:
                            if self.cancel_event.is_set():
                                self._cleanup_temp_files()
                                self.conversion_signals.failed.emit("Conversion cancelled")
                                return
                            
                            try:
                                merger.append(pdf_path)
                            except Exception as e:
                                print(f"Failed to merge {pdf_path}: {e}")
                        
                        # Write merged PDF
                        merger.write(target_path)
                        merger.close()
                        
                        self._cleanup_temp_files()
                        self.conversion_signals.finished.emit(target_path)
                    except Exception as e:
                        self._cleanup_temp_files()
                        self.conversion_signals.failed.emit(f"Merge failed: {str(e)}")
                else:
                    self._cleanup_temp_files()
                    self.conversion_signals.failed.emit("No valid files to convert")
            else:  # One by one
                count = 0
                for i, file_obj in enumerate(files):
                    if self.cancel_event.is_set():
                        self._cleanup_temp_files()
                        self.conversion_signals.failed.emit("Conversion cancelled")
                        return
                    
                    path = file_obj['path']
                    file_type = file_obj['type']
                    name = os.path.splitext(os.path.basename(path))[0]
                    save_path = os.path.join(target_path, f"{name}.pdf")
                    
                    try:
                        if file_type == 'html':
                            # HTML already converted to PDF, copy it
                            import shutil
                            if path in html_to_pdf_map:
                                shutil.copy(html_to_pdf_map[path], save_path)
                                count += 1
                        else:
                            # Convert image to PDF
                            img = self.process_image(path)
                            img.save(save_path, "PDF", quality=quality)
                            count += 1
                    except Exception as e:
                        print(f"Failed to convert {path}: {e}")
                
                self._cleanup_temp_files()
                if count > 0:
                    self.conversion_signals.finished.emit(target_path)
                else:
                    self.conversion_signals.failed.emit("No valid files to convert")
        
        except Exception as e:
            self._cleanup_temp_files()
            self.conversion_signals.failed.emit(str(e))
    
    def _cleanup_temp_files(self):
        """Clean up temporary PDF files created from HTML conversion."""
        for temp_file in self.temp_pdf_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                print(f"Failed to delete temp file {temp_file}: {e}")
        self.temp_pdf_files = []

    # ... (skipping unchanged methods) ...

    def on_conversion_complete(self, pdf_path):
        self.log_progress(self.lang.t("log_complete"))
        self.log_progress(self.lang.t("log_saved", path=pdf_path))
        
        self.is_converting = False
        self.convertBtn.setEnabled(True)
        self.convertBtn.setText(self.lang.t("convert"))
        self.cancelBtn.setVisible(False)
        InfoBar.success(
            self.lang.t("saved_success_title"), 
            self.lang.t("saved_success_body", path=pdf_path), 
            parent=self, 
            position=InfoBarPosition.TOP_RIGHT
        )
        
        # Auto-open folder containing the PDF
        import subprocess
        import platform
        try:
            folder_path = os.path.dirname(pdf_path) if not os.path.isdir(pdf_path) else pdf_path
            if platform.system() == "Windows":
                # Windows: open folder in Explorer
                os.startfile(folder_path)
            elif platform.system() == "Darwin":
                # macOS: open folder in Finder
                subprocess.run(["open", folder_path])
            else:
                # Linux: open folder in file manager
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            print(f"Could not open folder: {e}")

    def on_conversion_failed(self, msg):
        self.log_progress(self.lang.t("log_error", msg=msg))
        
        self.is_converting = False
        self.convertBtn.setEnabled(True)
        self.convertBtn.setText(self.lang.t("convert"))
        self.cancelBtn.setVisible(False)
        InfoBar.error(
            self.lang.t("conversion_failed_title"), 
            msg, 
            parent=self, 
            position=InfoBarPosition.TOP_RIGHT
        )

    # ... (skipping unchanged methods) ...



    # ... (setup_ui and update_texts methods remain unchanged) ...

    # ... (add_images, add_folder methods remain unchanged) ...

    def add_image_files(self, files):
        new = [f for f in files if f not in self.image_files]
        if new:
            self.image_files.extend(new)
            self.apply_sort() # Sort immediately after adding
            InfoBar.success(
                self.lang.t("images_added_title"), 
                self.lang.t("images_added_body", n=len(new)), 
                parent=self, 
                position=InfoBarPosition.TOP_RIGHT
            )

    def refresh_list(self):
        self.listWidget.clear()
        # Use a default icon while loading
        default_icon = Icons.photo()
        
        for f in self.image_files:
            item = QListWidgetItem(os.path.basename(f))
            item.setIcon(default_icon)
            self.listWidget.addItem(item)
            
            # Load thumbnail async
            worker = ThumbnailRunnable(f, item)
            worker.signals.loaded.connect(self.on_thumbnail_loaded)
            self.thread_pool.start(worker)
            
        self.emptyHint.setVisible(len(self.image_files) == 0)

    def on_thumbnail_loaded(self, item, image):
        # Check if item is still valid (attached to a list widget)
        if item.listWidget() is not None:
            icon = QIcon(QPixmap.fromImage(image))
            item.setIcon(icon)

    def apply_sort(self):
        """Sort image files based on current selection and refresh list."""
        idx = self.sortCombo.currentIndex()
        
        # Disable controls while sorting
        self.set_controls_enabled(False)
        
        # Run sort in background
        worker = SortRunnable(self.image_files, idx)
        worker.signals.finished.connect(self.on_sort_finished)
        self.thread_pool.start(worker)

    def on_sort_finished(self, sorted_files):
        self.image_files = sorted_files
        self.refresh_list()
        self.set_controls_enabled(True)

    def set_controls_enabled(self, enabled):
        self.sortCombo.setEnabled(enabled)
        self.addImagesBtn.setEnabled(enabled)
        self.addFolderBtn.setEnabled(enabled)
        self.clearBtn.setEnabled(enabled)
        self.convertBtn.setEnabled(enabled)

    # ... (browse_output_path, clear_images, convert_images, perform_conversion, process_image, resize_image methods remain unchanged) ...

    # ... (rest of methods) ...
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        
        # Header
        self.create_header(layout)
        
        # Drop List with control buttons
        list_container = QWidget(self)
        list_h_layout = QHBoxLayout(list_container)
        list_h_layout.setContentsMargins(0, 0, 0, 0)
        list_h_layout.setSpacing(10)
        
        self.listWidget = DropListWidget(self.add_image_files, self.sync_files_from_list, self)
        list_h_layout.addWidget(self.listWidget)
        
        # Control buttons (vertical layout on the right)
        controls = QWidget(self)
        controls_layout = QVBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        
        from qfluentwidgets import TransparentToolButton, FluentIcon
        self.moveUpBtn = TransparentToolButton(FluentIcon.UP, self)
        self.moveDownBtn = TransparentToolButton(FluentIcon.DOWN, self)
        self.removeBtn = TransparentToolButton(FluentIcon.DELETE, self)
        
        self.moveUpBtn.setToolTip(self.lang.t("move_up"))
        self.moveDownBtn.setToolTip(self.lang.t("move_down"))
        self.removeBtn.setToolTip(self.lang.t("remove_item"))
        
        self.moveUpBtn.clicked.connect(self.move_item_up)
        self.moveDownBtn.clicked.connect(self.move_item_down)
        self.removeBtn.clicked.connect(self.remove_selected_items)
        
        controls_layout.addWidget(self.moveUpBtn)
        controls_layout.addWidget(self.moveDownBtn)
        controls_layout.addWidget(self.removeBtn)
        controls_layout.addStretch()
        
        list_h_layout.addWidget(controls)
        layout.addWidget(list_container)
        
        # Progress Log (hidden by default, shown during conversion)
        self.progressLog = TextEdit(self)
        self.progressLog.setReadOnly(True)
        self.progressLog.setMaximumHeight(120)
        self.progressLog.setPlaceholderText("Progress log will appear here during conversion...")
        self.progressLog.setVisible(False)
        layout.addWidget(self.progressLog)
        
        # Empty Hint
        # Use a layout on listWidget to center the label perfectly
        list_layout = QVBoxLayout(self.listWidget)
        self.emptyHint = SubtitleLabel(self.lang.t("empty_hint"), self.listWidget)
        self.emptyHint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emptyHint.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        list_layout.addWidget(self.emptyHint, 0, Qt.AlignmentFlag.AlignCenter)
        # Note: Styling for emptyHint is handled in update_texts or theme change
        
        # Buttons
        buttons = QWidget(self)
        hb = QHBoxLayout(buttons)
        hb.setContentsMargins(0, 0, 0, 0)
        self.addImagesBtn = PushButton(self.lang.t("add_images"), self)
        self.addFolderBtn = PushButton(self.lang.t("add_folder"), self)
        self.clearBtn = PushButton(self.lang.t("clear_all"), self)
        
        self.addImagesBtn.clicked.connect(self.add_images)
        self.addFolderBtn.clicked.connect(self.add_folder)
        self.clearBtn.clicked.connect(self.clear_images)
        
        hb.addWidget(self.addImagesBtn)
        hb.addWidget(self.addFolderBtn)
        hb.addWidget(self.clearBtn)
        layout.addWidget(buttons)
        
        # Settings Row
        settings = QWidget(self)
        sh = QHBoxLayout(settings)
        sh.setContentsMargins(0, 0, 0, 0)
        sh.setSpacing(0)
        
        # Method
        self.methodLabel = BodyLabel(self.lang.t("label_method"), self)
        self.methodCombo = ComboBox(self)
        
        # Quality
        self.qualityLabel = BodyLabel(self.lang.t("label_quality"), self)
        self.compressionCombo = ComboBox(self)
        
        # Sort
        self.sortLabel = BodyLabel(self.lang.t("label_sort"), self)
        self.sortCombo = ComboBox(self)
        self.sortCombo.currentIndexChanged.connect(self.apply_sort)
        
        self.originalCheck = CheckBox(self.lang.t("compression_original"), self)
        self.portraitCheck = CheckBox(self.lang.t("portrait"), self)
        self.marginCheck = CheckBox(self.lang.t("no_margin"), self)
        
        self.portraitCheck.setChecked(True)
        self.originalCheck.setChecked(True)
        self.marginCheck.setChecked(True)
        
        sh.addWidget(self.methodLabel)
        sh.addSpacing(8)
        sh.addWidget(self.methodCombo)
        sh.addSpacing(24)
        
        sh.addWidget(self.qualityLabel)
        sh.addSpacing(8)
        sh.addWidget(self.compressionCombo)
        sh.addSpacing(24)
        
        sh.addWidget(self.sortLabel)
        sh.addSpacing(8)
        sh.addWidget(self.sortCombo)
        sh.addSpacing(24)
        
        sh.addWidget(self.originalCheck)
        sh.addSpacing(16)
        sh.addWidget(self.portraitCheck)
        sh.addSpacing(16)
        sh.addWidget(self.marginCheck)
        sh.addStretch()
        layout.addWidget(settings)
        
        # Output Path
        pathBar = QWidget(self)
        ph = QHBoxLayout(pathBar)
        ph.setContentsMargins(0, 0, 0, 0)
        self.pathEdit = LineEdit(self)
        self.pathEdit.setText(self.output_path)
        self.browseBtn = PushButton(self.lang.t("browse"), self)
        self.browseBtn.clicked.connect(self.browse_output_path)
        ph.addWidget(self.pathEdit)
        ph.addWidget(self.browseBtn)
        layout.addWidget(pathBar)
        
        # Action Buttons
        actions = QWidget(self)
        ah = QHBoxLayout(actions)
        ah.setContentsMargins(0, 0, 0, 0)
        ah.setSpacing(10)
        
        self.convertBtn = PrimaryPushButton(self.lang.t("convert"), self)
        self.convertBtn.clicked.connect(self.convert_images)
        
        self.cancelBtn = PushButton(self.lang.t("cancel"), self)
        self.cancelBtn.clicked.connect(self.cancel_conversion)
        self.cancelBtn.setVisible(False)

        
        ah.addWidget(self.convertBtn)
        ah.addWidget(self.cancelBtn)
        layout.addWidget(actions)

    def update_texts(self):
        """Update UI texts based on current language."""
        self.header.setText(self.lang.t("title"))
        self.addImagesBtn.setText(self.lang.t("add_images"))
        self.addFolderBtn.setText(self.lang.t("add_folder"))
        self.clearBtn.setText(self.lang.t("clear_all"))
        self.browseBtn.setText(self.lang.t("browse"))
        self.convertBtn.setText(self.lang.t("convert"))
        self.cancelBtn.setText(self.lang.t("cancel"))
        self.emptyHint.setText(self.lang.t("empty_hint"))
        
        self.methodLabel.setText(self.lang.t("label_method"))
        self.qualityLabel.setText(self.lang.t("label_quality"))
        self.sortLabel.setText(self.lang.t("label_sort"))
        
        # Preserve indices
        method_idx = self.methodCombo.currentIndex()
        quality_idx = self.compressionCombo.currentIndex()
        sort_idx = self.sortCombo.currentIndex()
        
        self.methodCombo.blockSignals(True)
        self.methodCombo.clear()
        self.methodCombo.addItems([self.lang.t("method_one"), self.lang.t("method_all")])
        self.methodCombo.setCurrentIndex(method_idx if method_idx >= 0 else 1)
        self.methodCombo.blockSignals(False)
        
        self.compressionCombo.blockSignals(True)
        self.compressionCombo.clear()
        self.compressionCombo.addItems([
            self.lang.t("compression_original"),
            self.lang.t("compression_high"),
            self.lang.t("compression_medium"),
            self.lang.t("compression_low")
        ])
        self.compressionCombo.setCurrentIndex(quality_idx if quality_idx >= 0 else 0)
        self.compressionCombo.blockSignals(False)
        
        self.sortCombo.blockSignals(True)
        self.sortCombo.clear()
        self.sortCombo.addItems([
            self.lang.t("sort_name"),
            self.lang.t("sort_mtime"),
            self.lang.t("sort_ctime"),
            self.lang.t("sort_size")
        ])
        self.sortCombo.setCurrentIndex(sort_idx if sort_idx >= 0 else 0)
        self.sortCombo.blockSignals(False)
        
        self.originalCheck.setText(self.lang.t("compression_original"))
        self.portraitCheck.setText(self.lang.t("portrait"))
        self.marginCheck.setText(self.lang.t("no_margin"))
        
        self.update_theme()

    def update_theme(self):
        """Update UI styles based on current theme."""
        is_dark = isDarkTheme()
        color = "#d0d0d0" if is_dark else "#606060"
        self.emptyHint.setStyleSheet(f"color: {color}; padding: 12px; background: transparent;")
        
        # Dashed border style for drop area
        border_color = "#404040" if is_dark else "#d0d0d0"
        bg_color = "#202020" if is_dark else "#f9f9f9"
        
        self.listWidget.setStyleSheet(f"""
            ListWidget {{
                border: 2px dashed {border_color};
                border-radius: 10px;
                background-color: {bg_color};
            }}
            ListWidget::item {{
                height: 72px;
                padding: 4px;
            }}
        """)

    def add_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            self.lang.t("add_images"), 
            "", 
            "Images and HTML (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp *.html *.htm);;Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp);;HTML (*.html *.htm)"
        )
        if files:
            self.add_image_files(files)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.lang.t("add_folder"), "")
        if folder:
            exts = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp", ".html", ".htm")
            files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(exts)]
            if files:
                self.add_image_files(files)
            else:
                InfoBar.info(
                    self.lang.t("no_images_title"), 
                    "No files found", 
                    parent=self, 
                    position=InfoBarPosition.TOP_RIGHT
                )

    def add_image_files(self, files):
        # Convert to file objects with metadata
        existing_paths = [item['path'] for item in self.image_files]
        new_files = []
        for f in files:
            if f not in existing_paths:
                # Determine file type
                file_type = 'html' if f.lower().endswith(('.html', '.htm')) else 'image'
                new_files.append({'path': f, 'type': file_type})
        
        if new_files:
            self.image_files.extend(new_files)
            self.apply_sort() # Sort immediately after adding
            InfoBar.success(
                self.lang.t("images_added_title"), 
                self.lang.t("images_added_body", n=len(new_files)), 
                parent=self, 
                position=InfoBarPosition.TOP_RIGHT
            )

    def refresh_list(self):
        self.listWidget.clear()
        # Use default icons
        photo_icon = Icons.photo().icon()
        html_icon = FluentIcon.DOCUMENT.icon()
        
        for file_obj in self.image_files:
            path = file_obj['path']
            file_type = file_obj['type']
            
            item = QListWidgetItem(os.path.basename(path))
            # Store the full file object in item data for reliable sync
            item.setData(Qt.ItemDataRole.UserRole, file_obj)
            
            if file_type == 'html':
                # Use HTML icon for HTML files
                item.setIcon(html_icon)
            else:
                # Use photo icon and load thumbnail async
                item.setIcon(photo_icon)
                worker = ThumbnailRunnable(path, item)
                worker.signals.loaded.connect(self.on_thumbnail_loaded)
                self.thread_pool.start(worker)
            
            self.listWidget.addItem(item)
            
        self.emptyHint.setVisible(len(self.image_files) == 0)

    def on_thumbnail_loaded(self, item, image):
        # Check if item is still valid (attached to a list widget)
        if item.listWidget() is not None:
            icon = QIcon(QPixmap.fromImage(image))
            item.setIcon(icon)

    def apply_sort(self):
        """Sort image files based on current selection and refresh list."""
        idx = self.sortCombo.currentIndex()
        # 0: Name, 1: MTime, 2: CTime, 3: Size
        if idx == 0:
            # Sort by basename, case insensitive
            self.image_files.sort(key=lambda x: os.path.basename(x['path']).lower())
        elif idx == 1:
            self.image_files.sort(key=lambda x: os.path.getmtime(x['path']))
        elif idx == 2:
            self.image_files.sort(key=lambda x: os.path.getctime(x['path']))
        elif idx == 3:
            self.image_files.sort(key=lambda x: os.path.getsize(x['path']))
            
        self.refresh_list()

    def on_sort_finished(self, sorted_files):
        self.image_files = sorted_files
        self.refresh_list()
        self.set_controls_enabled(True)

    def set_controls_enabled(self, enabled):
        self.sortCombo.setEnabled(enabled)
        self.addImagesBtn.setEnabled(enabled)
        self.addFolderBtn.setEnabled(enabled)
        self.clearBtn.setEnabled(enabled)
        self.convertBtn.setEnabled(enabled)

    def browse_output_path(self):
        folder = QFileDialog.getExistingDirectory(self, self.lang.t("browse"), self.output_path)
        if folder:
            self.output_path = folder
            self.pathEdit.setText(folder)

    def clear_images(self):
        self.image_files = []
        self.refresh_list()
    
    def log_progress(self, message):
        """Append message to progress log with auto-scroll."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.progressLog.append(f"[{timestamp}] {message}")
        # Auto-scroll to bottom
        scrollbar = self.progressLog.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_progress_log(self):
        """Clear progress log."""
        self.progressLog.clear()
    
    def show_countdown(self, seconds=3):
        """
        Show countdown on cancel button.
        Returns True if user canceled, False if countdown completed.
        """
        import time
        for i in range(seconds, 0, -1):
            if self.cancel_event.is_set():
                return True
            self.cancelBtn.setText(f"Cancel ({i}s)")
            QApplication.processEvents()
            time.sleep(1)
        # Reset button text
        self.cancelBtn.setText(self.lang.t("cancel") if hasattr(self.lang, 't') else "Cancel")
        return False
    
    def move_item_up(self):
        """Move selected item up in the list."""
        current_row = self.listWidget.currentRow()
        if current_row > 0:
            # Remove item from widget (preserves data)
            item = self.listWidget.takeItem(current_row)
            # Re-insert it one position up
            self.listWidget.insertItem(current_row - 1, item)
            # Select the moved item
            self.listWidget.setCurrentRow(current_row - 1)
            # Sync image_files from widget order
            self.sync_files_from_list()
    
    def move_item_down(self):
        """Move selected item down in the list."""
        current_row = self.listWidget.currentRow()
        if current_row >= 0 and current_row < self.listWidget.count() - 1:
            # Remove item from widget (preserves data)
            item = self.listWidget.takeItem(current_row)
            # Re-insert it one position down
            self.listWidget.insertItem(current_row + 1, item)
            # Select the moved item
            self.listWidget.setCurrentRow(current_row + 1)
            # Sync image_files from widget order
            self.sync_files_from_list()
    
    def remove_selected_items(self):
        """Remove selected items from the list."""
        selected_items = self.listWidget.selectedItems()
        if not selected_items:
            return
        
        # Get indices of selected items
        indices_to_remove = []
        for item in selected_items:
            row = self.listWidget.row(item)
            indices_to_remove.append(row)
        
        # Remove from image_files (reverse order to maintain indices)
        for index in sorted(indices_to_remove, reverse=True):
            if 0 <= index < len(self.image_files):
                del self.image_files[index]
        
        # Refresh list
        self.refresh_list()
    
    def sync_files_from_list(self):
        """Sync image_files list order from current listWidget order (after drag-drop)."""
        # Build new ordered list from widget items using stored data
        new_order = []
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            # Retrieve the file object stored in item data
            file_obj = item.data(Qt.ItemDataRole.UserRole)
            if file_obj:
                new_order.append(file_obj)
        
        # Update image_files with new order
        if len(new_order) == len(self.image_files):
            self.image_files = new_order
            print(f"DEBUG: Synced order - {[os.path.basename(f['path']) for f in self.image_files]}")

    def cancel_conversion(self):
        if self.is_converting:
            self.cancel_event.set()
            self.cancelBtn.setEnabled(False)
            self.cancelBtn.setText(self.lang.t("canceling") if hasattr(self.lang, 't') else "Canceling...")

    def convert_images(self):
        if not self.image_files:
            InfoBar.warning(
                self.lang.t("no_images_title"), 
                self.lang.t("no_images_body"), 
                parent=self, 
                position=InfoBarPosition.TOP_RIGHT
            )
            return
        out_dir = self.pathEdit.text().strip()
        if not out_dir:
            InfoBar.warning(
                self.lang.t("no_output_title"), 
                self.lang.t("no_output_body"), 
                parent=self, 
                position=InfoBarPosition.TOP_RIGHT
            )
            return
        if not os.path.exists(out_dir):
            try:
                os.makedirs(out_dir)
            except Exception as e:
                InfoBar.error("Error", str(e), parent=self)
                return
        
        method = self.methodCombo.currentIndex() # 0: One by one, 1: All in one
        target_path = out_dir
        
        if method == 1: # All in one
            pdf_path, _ = QFileDialog.getSaveFileName(self, "Save PDF As", out_dir, "PDF Files (*.pdf)")
            if not pdf_path:
                return
            target_path = pdf_path
        
        # IMPORTANT: Convert HTML files to PDF on MAIN THREAD first
        # WebEngine requires main Qt thread
        self.temp_pdf_files = []
        html_to_pdf_map = {}  # Maps original HTML path to temp PDF path
        
        # Setup UI for conversion early (including cancel button)
        self.is_converting = True
        self.cancel_event.clear()
        self.convertBtn.setEnabled(False)
        self.cancelBtn.setVisible(True)
        self.cancelBtn.setEnabled(True)
        self.cancelBtn.setText(self.lang.t("cancel") if hasattr(self.lang, 't') else "Cancel")
        
        # Show progress log
        self.progressLog.setVisible(True)
        self.clear_progress_log()
        self.log_progress(self.lang.t("log_starting"))
        
        # Count HTML files for progress display
        html_count = sum(1 for f in self.image_files if f['type'] == 'html')
        html_idx = 0
        
        for file_obj in self.image_files:
            # Check for cancellation
            if self.cancel_event.is_set():
                self._cleanup_temp_files()
                self.is_converting = False
                self.convertBtn.setEnabled(True)
                self.convertBtn.setText(self.lang.t("convert"))
                self.cancelBtn.setVisible(False)
                return
                
            if file_obj['type'] == 'html':
                path = file_obj['path']
                html_idx += 1
                
                # Log start
                filename = os.path.basename(path)
                self.log_progress(self.lang.t("log_converting_html", idx=html_idx, total=html_count, file=filename))
                
                # Update UI to show progress
                self.convertBtn.setText(f"Converting HTML {html_idx}/{html_count}...")
                QApplication.processEvents()
                
                try:
                    # Create temp PDF
                    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                    temp_pdf.close()
                    temp_pdf_path = temp_pdf.name
                    self.temp_pdf_files.append(temp_pdf_path)
                    
                    # Convert HTML to PDF (on main thread)
                    converter = HtmlToPdfConverter()
                    result_path = converter.convert_file_sync(path, temp_pdf_path)
                    
                    if result_path:
                        html_to_pdf_map[path] = result_path
                        self.log_progress(self.lang.t("log_converted", file=filename))
                    else:
                        self.log_progress(self.lang.t("log_failed", file=filename))
                        print(f"Failed to convert HTML: {path}")
                except Exception as e:
                    print(f"Error converting HTML {path}: {e}")
        
        # Now start background thread with converted files
        self.convertBtn.setText(self.lang.t("converting") if hasattr(self.lang, 't') else "Converting...")
        
        if html_count > 0:
            self.log_progress(self.lang.t("log_html_complete", count=html_count))
        self.log_progress(self.lang.t("log_starting_merge"))
        
        # Pass a copy of the current (sorted) list to the thread
        files_to_convert = self.image_files[:]
        
        t = threading.Thread(target=self.perform_conversion, args=(target_path, method, files_to_convert, html_to_pdf_map))
        t.start()



    def process_image(self, path):
        img = Image.open(path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        if not self.originalCheck.isChecked():
            img = self.resize_image(img)
            
        return img

    def resize_image(self, img):
        if self.portraitCheck.isChecked():
            base_height = 842
            w_percent = base_height / float(img.size[1])
            w_size = int(float(img.size[0]) * float(w_percent))
            return img.resize((w_size, base_height), Image.Resampling.LANCZOS)
        base_width = 842
        h_percent = base_width / float(img.size[0])
        h_size = int(float(img.size[1]) * float(h_percent))
        return img.resize((base_width, h_size), Image.Resampling.LANCZOS)

    def get_quality_setting(self):
        idx = self.compressionCombo.currentIndex()
        if idx == 1: return 95
        if idx == 2: return 75
        if idx == 3: return 50
        return 100

    def create_header(self, layout):
        header_widget = QWidget(self)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.header = SubtitleLabel(self.lang.t("title"), self)
        
        self.supportBtn = HyperlinkButton(
            "https://ko-fi.com/solveproblem",
            "Support me on Ko-fi",
            self,
            FluentIcon.HEART
        )
        
        header_layout.addWidget(self.header)
        header_layout.addStretch(1)
        header_layout.addWidget(self.supportBtn)
        
        layout.addWidget(header_widget)
