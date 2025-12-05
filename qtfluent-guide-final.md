# Hướng dẫn Xây dựng Dự án Python Desktop từ Đầu với QFluentWidgets

Tài liệu này hướng dẫn step-by-step cách tạo một ứng dụng desktop Python với giao diện Fluent Design hiện đại.

---

## Bước 1: Khởi tạo Project

### 1.1 Tạo cấu trúc thư mục

```
my_app/
├── src/
│   └── my_app/
│       ├── __init__.py
│       ├── __main__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config_manager.py
│       │   └── theme_manager.py
│       ├── gui/
│       │   ├── __init__.py
│       │   ├── main_window.py
│       │   ├── icons.py
│       │   └── interfaces/
│       │       ├── __init__.py
│       │       ├── home_interface.py
│       │       └── settings_interface.py
│       └── services/
│           └── __init__.py
├── tests/
│   └── __init__.py
├── pyproject.toml
├── build.py
├── launch.py
└── README.md
```

### 1.2 Tạo pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-app"
version = "0.1.0"
description = "My Desktop Application"
requires-python = ">=3.9"
license = {text = "MIT"}

dependencies = [
    "PyQt6>=6.6.0",
    "PyQt6-Fluent-Widgets[full]>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-qt>=4.3.0",
]
build = [
    "pyinstaller>=6.0.0",
]

[project.scripts]
my-app = "my_app.__main__:main"

[tool.setuptools.packages.find]
where = ["src"]
```

---

## Bước 2: Tạo Core Components

### 2.1 src/my_app/__init__.py

```python
"""My App - A modern desktop application."""

__version__ = "0.1.0"
__author__ = "Your Name"
```

### 2.2 src/my_app/core/theme_manager.py

```python
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
```

### 2.3 src/my_app/core/config_manager.py

```python
"""Configuration manager with JSON persistence."""

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration."""
    
    DEFAULT_DIR = Path.home() / '.my_app'
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
    
    def _defaults(self) -> dict:
        return {
            'theme': 'dark',
            'window_geometry': None,
        }
```

---

## Bước 3: Tạo GUI Components

### 3.1 src/my_app/gui/icons.py

```python
"""Icon provider using FluentIcon."""

from qfluentwidgets import FluentIcon as FIF


class Icons:
    """Centralized icon access."""
    
    @staticmethod
    def home(): return FIF.HOME.icon()
    
    @staticmethod
    def folder(): return FIF.FOLDER.icon()
    
    @staticmethod
    def file(): return FIF.DOCUMENT.icon()
    
    @staticmethod
    def settings(): return FIF.SETTING.icon()
    
    @staticmethod
    def refresh(): return FIF.SYNC.icon()
    
    @staticmethod
    def search(): return FIF.SEARCH.icon()
    
    @staticmethod
    def add(): return FIF.ADD.icon()
    
    @staticmethod
    def delete(): return FIF.DELETE.icon()
    
    @staticmethod
    def info(): return FIF.INFO.icon()
    
    @staticmethod
    def help(): return FIF.HELP.icon()
    
    @staticmethod
    def theme(): return FIF.CONSTRACT.icon()
```

### 3.2 src/my_app/gui/interfaces/home_interface.py

```python
"""Home interface - main content area."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

from qfluentwidgets import (
    PrimaryPushButton, PushButton, SearchLineEdit,
    InfoBar, InfoBarPosition
)


class HomeInterface(QWidget):
    """Home page of the application."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HomeInterface")  # REQUIRED!
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Welcome to My App")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Search box
        self.search_box = SearchLineEdit(self)
        self.search_box.setPlaceholderText("Search something...")
        self.search_box.setClearButtonEnabled(True)
        layout.addWidget(self.search_box)
        
        # Buttons
        self.primary_btn = PrimaryPushButton("Primary Action", self)
        self.primary_btn.clicked.connect(self.on_primary_click)
        layout.addWidget(self.primary_btn)
        
        self.secondary_btn = PushButton("Secondary Action", self)
        layout.addWidget(self.secondary_btn)
        
        # Spacer
        layout.addStretch()
    
    def on_primary_click(self):
        InfoBar.success(
            title="Success",
            content="Action completed!",
            parent=self.window(),
            position=InfoBarPosition.TOP_RIGHT,
            duration=3000
        )
```

### 3.3 src/my_app/gui/interfaces/settings_interface.py

```python
"""Settings interface."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

from qfluentwidgets import (
    SwitchButton, ComboBox, PushButton,
    InfoBar, InfoBarPosition
)

from ...core.theme_manager import ThemeManager


class SettingsInterface(QWidget):
    """Settings page."""
    
    theme_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsInterface")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Theme selector
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = ComboBox(self)
        self.theme_combo.addItems(["Light", "Dark", "Auto"])
        self.theme_combo.setCurrentText("Dark" if ThemeManager.is_dark() else "Light")
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)
        
        # Dark mode toggle (alternative)
        toggle_layout = QHBoxLayout()
        toggle_label = QLabel("Dark Mode:")
        self.dark_toggle = SwitchButton(self)
        self.dark_toggle.setChecked(ThemeManager.is_dark())
        self.dark_toggle.checkedChanged.connect(self.on_dark_toggle)
        toggle_layout.addWidget(toggle_label)
        toggle_layout.addWidget(self.dark_toggle)
        toggle_layout.addStretch()
        layout.addLayout(toggle_layout)
        
        layout.addStretch()
    
    def on_theme_changed(self, theme: str):
        ThemeManager.apply_theme(theme.lower())
        self.theme_changed.emit(theme.lower())
        
        InfoBar.info(
            title="Theme Changed",
            content=f"Switched to {theme} theme",
            parent=self.window(),
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000
        )
    
    def on_dark_toggle(self, checked: bool):
        theme = "dark" if checked else "light"
        ThemeManager.apply_theme(theme)
        self.theme_combo.setCurrentText(theme.capitalize())
        self.theme_changed.emit(theme)
```

### 3.4 src/my_app/gui/main_window.py

```python
"""Main window using FluentWindow."""

import logging
from PyQt6.QtCore import pyqtSignal

from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon as FIF,
    MessageBox, InfoBar, InfoBarPosition
)

from .interfaces.home_interface import HomeInterface
from .interfaces.settings_interface import SettingsInterface
from ..core.config_manager import ConfigManager
from ..core.theme_manager import ThemeManager

logger = logging.getLogger(__name__)


class MainWindow(FluentWindow):
    """Main application window."""
    
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Initialize config
        self.config = ConfigManager()
        self.config.load()
        
        # Create interfaces
        self.home_interface = HomeInterface(self)
        self.settings_interface = SettingsInterface(self)
        
        # Connect signals
        self.settings_interface.theme_changed.connect(self.on_theme_changed)
        
        # Setup
        self.init_navigation()
        self.init_window()
        
        # Apply saved theme
        ThemeManager.apply_theme(self.config.get_theme())
    
    def init_navigation(self):
        """Setup navigation sidebar."""
        # Home (TOP)
        self.addSubInterface(
            self.home_interface,
            FIF.HOME,
            "Home",
            NavigationItemPosition.TOP
        )
        
        # Separator
        self.navigationInterface.addSeparator()
        
        # Theme toggle action (BOTTOM)
        self.navigationInterface.addItem(
            routeKey='theme_toggle',
            icon=FIF.CONSTRACT,
            text='Toggle Theme',
            onClick=self.toggle_theme,
            position=NavigationItemPosition.BOTTOM
        )
        
        # Settings (BOTTOM)
        self.addSubInterface(
            self.settings_interface,
            FIF.SETTING,
            "Settings",
            NavigationItemPosition.BOTTOM
        )
    
    def init_window(self):
        """Setup window properties."""
        self.setWindowTitle("My App")
        self.resize(1000, 700)
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
    
    def toggle_theme(self):
        """Toggle between dark and light theme."""
        new_theme = ThemeManager.toggle()
        self.on_theme_changed(new_theme)
        
        InfoBar.info(
            title="Theme Changed",
            content=f"Switched to {new_theme} theme",
            parent=self,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000
        )
    
    def on_theme_changed(self, theme: str):
        """Handle theme change."""
        self.config.set_theme(theme)
        self.config.save()
        self.theme_changed.emit(theme)
    
    def closeEvent(self, event):
        """Save state on close."""
        # Save geometry
        self.config.set('window_geometry', {
            'x': self.x(),
            'y': self.y(),
            'width': self.width(),
            'height': self.height()
        })
        self.config.save()
        event.accept()
```

---

## Bước 4: Entry Point

### 4.1 src/my_app/__main__.py

```python
"""Application entry point."""

import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

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
    app.setApplicationName("My App")
    app.setApplicationVersion("0.1.0")
    
    # Load config and initialize theme
    config = ConfigManager()
    config.load()
    ThemeManager.initialize(config.get_theme())
    
    # Create and show window
    window = MainWindow()
    window.show()
    
    logger.info("Application started")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
```

---

## Bước 5: Launch Script

### 5.1 launch.py

```python
#!/usr/bin/env python3
"""Launch script with dependency check."""

import subprocess
import sys

REQUIRED = [
    "PyQt6",
    "PyQt6-Fluent-Widgets",
]


def check_dependencies():
    """Check and install missing dependencies."""
    missing = []
    
    for package in REQUIRED:
        try:
            __import__(package.replace("-", "_").split("[")[0].lower())
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Installing missing packages: {missing}")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", *missing
        ])


def main():
    check_dependencies()
    
    from src.my_app.__main__ import main as app_main
    sys.exit(app_main())


if __name__ == "__main__":
    main()
```

---

## Bước 6: Build Script

### 6.1 build.py

```python
#!/usr/bin/env python3
"""Build script for PyInstaller."""

import os
import sys
import argparse
from pathlib import Path

APP_NAME = "MyApp"
ENTRY_POINT = "src/my_app/__main__.py"


def get_hidden_imports():
    return [
        "PyQt6.QtCore",
        "PyQt6.QtGui", 
        "PyQt6.QtWidgets",
        "qfluentwidgets",
        "qfluentwidgets.common",
        "qfluentwidgets.components",
        "qfluentwidgets.window",
        "qframelesswindow",
        "darkdetect",
        "scipy",
        "scipy.interpolate",
        "colorthief",
    ]


def get_excludes():
    return [
        "pytest", "hypothesis",
        "PyQt6.QtBluetooth", "PyQt6.QtMultimedia",
        "PyQt6.QtNetwork", "PyQt6.QtSql",
        "tkinter", "unittest",
    ]


def build(onefile=False, debug=False):
    import PyInstaller.__main__
    
    args = [
        ENTRY_POINT,
        f"--name={APP_NAME}",
        "--onefile" if onefile else "--onedir",
        "--windowed" if not debug else "--console",
        "--clean",
        "--noconfirm",
    ]
    
    for imp in get_hidden_imports():
        args.append(f"--hidden-import={imp}")
    
    for exc in get_excludes():
        args.append(f"--exclude-module={exc}")
    
    PyInstaller.__main__.run(args)
    print(f"\nBuild complete! Output in dist/{APP_NAME}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--onefile", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    
    build(args.onefile, args.debug)
```

---

## Bước 7: Chạy và Test

### 7.1 Cài đặt dependencies

```bash
pip install -e ".[dev]"
```

### 7.2 Chạy ứng dụng

```bash
# Cách 1: Module
python -m my_app

# Cách 2: Launch script
python launch.py

# Cách 3: Entry point (sau khi pip install)
my-app
```

### 7.3 Build executable

```bash
pip install pyinstaller
python build.py --onefile
```

---

## Checklist Hoàn thành

- [ ] Tạo cấu trúc thư mục
- [ ] Tạo pyproject.toml
- [ ] Tạo ThemeManager
- [ ] Tạo ConfigManager
- [ ] Tạo Icons wrapper
- [ ] Tạo Home Interface
- [ ] Tạo Settings Interface
- [ ] Tạo MainWindow (FluentWindow)
- [ ] Tạo __main__.py entry point
- [ ] Tạo launch.py
- [ ] Tạo build.py
- [ ] Test chạy ứng dụng
- [ ] Test theme switching
- [ ] Test build executable

---

## Mở rộng

### Thêm Interface mới

1. Tạo file `src/my_app/gui/interfaces/new_interface.py`
2. Kế thừa từ `QWidget`, set `objectName`
3. Import và thêm vào `MainWindow.init_navigation()`

### Thêm Service mới

1. Tạo file trong `src/my_app/services/`
2. Import và sử dụng trong Interface hoặc MainWindow

### Thêm Dialog

```python
from qfluentwidgets import MessageBox

def show_about(self):
    w = MessageBox(
        "About",
        "My App v0.1.0\n\nA modern desktop application.",
        self
    )
    w.exec()
```

---

*Template based on real-world QFluentWidgets implementation.*
