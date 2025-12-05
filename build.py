#!/usr/bin/env python3
"""Build script for PyInstaller."""

import os
import sys
import argparse
from pathlib import Path

APP_NAME = "ImageToPDF"
ENTRY_POINT = "run.py"


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
        "PIL",
        "PIL.Image",
        "PIL.ImageQt",
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
        "--paths=src",
        "--onefile" if onefile else "--onedir",
        "--windowed" if not debug else "--console",
        f"--icon=Icon.ico",
        "--clean",
        "--noconfirm",
        # Add data files if needed, e.g. i18n json files
        "--add-data=i18n.en.json;.",
        "--add-data=i18n.vi.json;.",
        "--add-data=Icon.ico;.",
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
