# ImageToPDF Converter

A modern, beautiful, and powerful Image to PDF converter application built with Python and Qt (PyQt6 & QFluentWidgets).

![Screenshot](image.png)

## 📥 for Normal Users (No Python Required)
If you just want to use the application, you do NOT need to install Python.

1. **Download**: Go to the `dist` folder (or releases page) and find `ImageToPDF.exe`.
2. **Run**: Double-click the `ImageToPDF.exe` file.
   - The app will start immediately.
   - You can move this file anywhere (USB drive, Desktop, etc.).

---

## 💻 for Python Users / Developers

If you want to modify the code or run it from source, follow these steps.

### Prerequisites
- Python 3.10 or higher installed.

### 1. Installation
Install the required libraries:
```bash
pip install -r requirements.txt
```
*Note: If `requirements.txt` is missing, manually install:*
```bash
pip install PyQt6 "PyQt6-Fluent-Widgets[full]" Pillow pyinstaller
```

### 2. Running the App
You can run the application in two ways:
- **Option A**: Double-click `launch.bat`.
- **Option B**: Run via terminal:
  ```bash
  python launch.py
  ```

### 3. Building EXE (Creating Standalone File)
To create the `ImageToPDF.exe` file yourself:

1. Run the build script:
   ```bash
   python build.py --onefile
   ```
2. Wait for the process to finish.
3. The new `ImageToPDF.exe` will appear in the `dist` folder.

---

## ✨ Features

- **Modern UI**: Designed with Fluent Design System, supporting both Light and Dark themes.
- **Drag & Drop**: Easily add images by dragging and dropping them into the application.
- **Multiple Modes**:
  - **All in one**: Merge all selected images into a single PDF file.
  - **One by one**: Convert each image into a separate PDF file.
- **Smart Sorting**: Sort images by Name, Size, Date Modified, or Date Created.
- **Image Processing**:
  - Auto-resize options (Original, Portrait, No Margin).
  - Compression quality settings (Original, High, Medium, Low).
- **Multilingual**: Support for English and Vietnamese (Tiếng Việt).
- **Support**: Links to Ko-fi for project support.

## 📝 License
MIT License
