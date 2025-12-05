"""Configuration manager."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration."""
    
    DEFAULT_DIR = Path.home() / '.img_to_pdf'
    DEFAULT_FILE = 'config.json'
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_dir = config_path.parent if config_path else self.DEFAULT_DIR
        self.config_path = config_path or (self.config_dir / self.DEFAULT_FILE)
        self._config: dict = {}
        self._ensure_dir()
    
    def _ensure_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> dict:
        """Load configuration from file."""
        if not self.config_path.exists():
            self._config = self._defaults()
            return self._config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self._config = self._defaults()
        
        return self._config
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        self._config[key] = value
    
    def get_theme(self) -> str:
        return self.get('theme', 'dark')
    
    def set_theme(self, theme: str) -> None:
        self.set('theme', theme)

    def get_language(self) -> str:
        return self.get('language', 'vi')

    def set_language(self, language: str) -> None:
        self.set('language', language)
    
    def _defaults(self) -> dict:
        return {
            'theme': 'dark',
            'language': 'vi',
            'window_geometry': None,
        }
