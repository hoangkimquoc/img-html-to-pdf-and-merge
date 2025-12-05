from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

from qfluentwidgets import (
    ComboBox, InfoBar, InfoBarPosition, SubtitleLabel, BodyLabel
)

from ...core.theme_manager import ThemeManager
from ...core.config_manager import ConfigManager
from ...core.language_manager import LanguageManager

class SettingsInterface(QWidget):
    """Settings page."""
    
    theme_changed = pyqtSignal(str)
    language_changed = pyqtSignal(str)
    
    def __init__(self, config: ConfigManager, lang: LanguageManager, parent=None):
        super().__init__(parent)
        self.config = config
        self.lang = lang
        self.setObjectName("SettingsInterface")
        self.setup_ui()
        self.update_texts()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        self.title = SubtitleLabel(self.lang.t("settings"), self)
        layout.addWidget(self.title)
        
        # Theme selector
        theme_layout = QHBoxLayout()
        self.theme_label = BodyLabel(self.lang.t("theme"), self)
        self.theme_combo = ComboBox(self)
        self.theme_combo.addItems([self.lang.t("light"), self.lang.t("dark")])
        
        current_theme = self.config.get_theme()
        idx = 1 if current_theme == 'dark' else 0
        self.theme_combo.setCurrentIndex(idx)
        
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)
        
        # Language selector
        lang_layout = QHBoxLayout()
        self.lang_label = BodyLabel(self.lang.t("language"), self)
        self.lang_combo = ComboBox(self)
        self.lang_combo.addItems([self.lang.t("en_label"), self.lang.t("vi_label")])
        
        current_lang = self.config.get_language()
        idx = 1 if current_lang == 'vi' else 0
        self.lang_combo.setCurrentIndex(idx)
        
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        layout.addStretch()
    
    def update_texts(self):
        self.title.setText(self.lang.t("settings"))
        self.theme_label.setText(self.lang.t("theme"))
        self.lang_label.setText(self.lang.t("language"))
        
        # Update combo items without triggering signals if possible, or just leave them
        # Re-populating combos might be annoying for user if they are open, but okay for now.
        # Actually, let's just update the items text if we can, but it's easier to just leave them 
        # or rebuild. For now, I'll leave the combo items as they were initialized or user selected.
        # But wait, the combo items themselves are localized ("Sáng"/"Tối").
        
        # Block signals to prevent loops
        self.theme_combo.blockSignals(True)
        self.lang_combo.blockSignals(True)
        
        current_theme_idx = self.theme_combo.currentIndex()
        self.theme_combo.clear()
        self.theme_combo.addItems([self.lang.t("light"), self.lang.t("dark")])
        self.theme_combo.setCurrentIndex(current_theme_idx)
        
        current_lang_idx = self.lang_combo.currentIndex()
        self.lang_combo.clear()
        self.lang_combo.addItems([self.lang.t("en_label"), self.lang.t("vi_label")])
        self.lang_combo.setCurrentIndex(current_lang_idx)
        
        self.theme_combo.blockSignals(False)
        self.lang_combo.blockSignals(False)

    def on_theme_changed(self, index):
        theme = "dark" if index == 1 else "light"
        ThemeManager.apply_theme(theme)
        self.config.set_theme(theme)
        self.config.save()
        self.theme_changed.emit(theme)
        
    def on_language_changed(self, index):
        lang_code = "vi" if index == 1 else "en"
        self.lang.lang = lang_code
        self.config.set_language(lang_code)
        self.config.save()
        self.language_changed.emit(lang_code)
        self.update_texts()
