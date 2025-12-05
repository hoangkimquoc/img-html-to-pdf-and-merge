# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run.py'],
    pathex=['src'],
    binaries=[],
    datas=[('i18n.en.json', '.'), ('i18n.vi.json', '.')],
    hiddenimports=['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'qfluentwidgets', 'qfluentwidgets.common', 'qfluentwidgets.components', 'qfluentwidgets.window', 'qframelesswindow', 'PIL', 'PIL.Image', 'PIL.ImageQt'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'hypothesis', 'PyQt6.QtBluetooth', 'PyQt6.QtMultimedia', 'PyQt6.QtNetwork', 'PyQt6.QtSql', 'tkinter', 'unittest'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ImageToPDF',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Icon.ico'],
)
