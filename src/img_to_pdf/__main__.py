"""Application entry point."""

import sys
import logging
import os
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from .core.config_manager import ConfigManager
from .core.theme_manager import ThemeManager
from .gui.main_window import MainWindow

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Main entry point."""
    logger.info("Starting application")
    
    # Enable High DPI BEFORE QApplication
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("ImageToPDF")
    app.setApplicationVersion("1.0.0")

    # Set AppUserModelID for Windows taskbar icon
    try:
        myappid = 'kav.imgtopdf.merge.1.0' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass
    
    # Set application icon
    # Set application icon
    def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            # In dev mode, use the directory of the run.py/launch.py or current working dir
            # Assuming we are running from root
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    icon_path = resource_path('Icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Create and show window
    window = MainWindow()
    window.show()
    
    logger.info("Application started")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
