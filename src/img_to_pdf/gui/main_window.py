import logging
import os
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from qfluentwidgets import (
    FluentWindow, NavigationItemPosition
)

from .interfaces.home_interface import HomeInterface
from .interfaces.settings_interface import SettingsInterface
from .icons import Icons
from ..core.config_manager import ConfigManager
from ..core.theme_manager import ThemeManager
from ..core.language_manager import LanguageManager

logger = logging.getLogger(__name__)

class MainWindow(FluentWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.config = ConfigManager()
        self.config.load()
        
        self.lang = LanguageManager(default=self.config.get_language())
        
        # Initialize theme
        ThemeManager.initialize(self.config.get_theme())
        
        # Create interfaces
        self.home_interface = HomeInterface(self.config, self.lang, self)
        self.settings_interface = SettingsInterface(self.config, self.lang, self)
        
        # Connect signals
        self.settings_interface.language_changed.connect(self.on_language_changed)
        self.settings_interface.theme_changed.connect(self.on_theme_changed)
        
        # Setup
        self.init_navigation()
        self.init_window()
        
    def init_navigation(self):
        """Setup navigation sidebar."""
        self.addSubInterface(
            self.home_interface,
            Icons.home(),
            self.lang.t("home"),
            NavigationItemPosition.TOP
        )
        
        self.addSubInterface(
            self.settings_interface,
            Icons.settings(),
            self.lang.t("settings"),
            NavigationItemPosition.BOTTOM
        )
        
    def init_window(self):
        """Setup window properties."""
        self.setWindowTitle(self.lang.t("title"))
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'Icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.resize(900, 700)
        self.setMinimumSize(800, 600)
        
        # Restore geometry
        geometry = self.config.get('window_geometry')
        if geometry:
            try:
                self.setGeometry(
                    geometry.get('x', 100),
                    geometry.get('y', 100),
                    geometry.get('width', 1280),
                    geometry.get('height', 720)
                )
            except Exception as e:
                logger.warning(f"Failed to restore geometry: {e}")
                
    def on_theme_changed(self, theme):
        """Handle theme change."""
        self.home_interface.update_theme()
                
    def on_language_changed(self, lang_code):
        """Handle language change."""
        # Update window title
        self.setWindowTitle(self.lang.t("title"))
        
        # Update interfaces
        self.home_interface.update_texts()
        self.settings_interface.update_texts()
        
        # Update navigation items
        # Note: FluentWindow doesn't have a direct method to update item text by interface easily
        # without accessing internal widgets or re-adding.
        # However, we can iterate over items in navigationInterface.
        # For simplicity, we might accept that nav items don't update immediately or we try to find them.
        
        # Attempt to update navigation text (this depends on QFluentWidgets internal structure)
        # But standard way is usually to just reload or let it be.
        # Let's try to update if possible.
        # The widget associated with the interface is stored.
        
        # We can re-set the text for the specific widget keys if we knew them.
        # addSubInterface uses the interface's objectName as route key by default if not provided.
        
        item = self.navigationInterface.widget(self.home_interface.objectName())
        if item:
            item.setText(self.lang.t("home"))
            
        item = self.navigationInterface.widget(self.settings_interface.objectName())
        if item:
            item.setText(self.lang.t("settings"))

    def closeEvent(self, event):
        """Save state on close."""
        self.config.set('window_geometry', {
            'x': self.x(),
            'y': self.y(),
            'width': self.width(),
            'height': self.height()
        })
        self.config.save()
        event.accept()
