#!/usr/bin/env python3
"""Launch script with dependency check."""

import subprocess
import sys
import os

REQUIRED = [
    "PyQt6",
    "PyQt6-Fluent-Widgets",
    "Pillow",
    "pypdf",
    "selenium"
]


def check_dependencies():
    """Check and install missing dependencies."""
    missing = []
    
    for package in REQUIRED:
        try:
            # Handle package name differences
            module_name = package
            if package == "PyQt6-Fluent-Widgets":
                module_name = "qfluentwidgets"
            elif package == "Pillow":
                module_name = "PIL"
                
            __import__(module_name)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Installing missing packages: {missing}")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", *missing
        ])


def main():
    check_dependencies()
    
    # Add src to path so we can import img_to_pdf
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    from img_to_pdf.__main__ import main as app_main
    sys.exit(app_main())


if __name__ == "__main__":
    main()
