"""Theme manager using QFluentWidgets."""

import logging
from qfluentwidgets import setTheme, setThemeColor, Theme, isDarkTheme

logger = logging.getLogger(__name__)


class ThemeManager:
    """Centralized theme management."""
    
    DARK = "dark"
    LIGHT = "light"
    AUTO = "auto"
    
    DEFAULT_ACCENT = "#0078d4"  # Windows blue
    
    _THEME_MAP = {
        "dark": Theme.DARK,
        "light": Theme.LIGHT,
        "auto": Theme.AUTO,
    }
    
    @classmethod
    def apply_theme(cls, theme_name: str) -> None:
        """Apply theme to application."""
        theme = cls._THEME_MAP.get(theme_name.lower(), Theme.AUTO)
        setTheme(theme)
        logger.info(f"Applied theme: {theme_name}")
    
    @classmethod
    def set_accent_color(cls, color: str) -> None:
        """Set accent color."""
        setThemeColor(color)
        logger.info(f"Set accent color: {color}")
    
    @classmethod
    def is_dark(cls) -> bool:
        """Check if current theme is dark."""
        return isDarkTheme()
    
    @classmethod
    def toggle(cls) -> str:
        """Toggle between dark and light theme."""
        new_theme = cls.LIGHT if cls.is_dark() else cls.DARK
        cls.apply_theme(new_theme)
        return new_theme
    
    @classmethod
    def initialize(cls, theme: str = "auto", accent: str = None) -> None:
        """Initialize theme system."""
        cls.set_accent_color(accent or cls.DEFAULT_ACCENT)
        cls.apply_theme(theme)
