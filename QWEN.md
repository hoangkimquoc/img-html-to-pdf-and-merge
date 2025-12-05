# img-to-pdf-merge Project Documentation

## Project Overview

The **img-to-pdf-merge** project is a Python desktop application that converts images to PDF format with a modern, Fluent Design-inspired user interface. It allows users to add multiple images, configure conversion settings, and export them as a single or multiple PDF files. The application supports drag-and-drop functionality, multiple image formats, and offers various compression and sorting options.

## Key Features

- **Image to PDF Conversion**: Convert single or multiple images to PDF format
- **Modern UI**: Built with PyQt6 and PyQt-Fluent-Widgets for a modern Fluent Design interface
- **Multi-language Support**: Supports both English and Vietnamese with easy localization
- **Drag-and-Drop**: Intuitive drag-and-drop functionality for adding images
- **Multiple Input Methods**: Add individual images or entire folders
- **Image Sorting**: Sort images by name, modification date, creation date, or file size
- **Compression Options**: Original size, high quality, medium, or low compression
- **Responsive Interface**: Adapts to different screen sizes and DPI settings

## Technologies Used

- **Python 3.x**: Core programming language
- **PyQt6**: GUI framework for desktop application
- **PyQt6-Fluent-Widgets**: Modern Fluent Design UI components
- **Pillow (PIL)**: Image processing library
- **JSON**: Localization file format

## File Structure

- `imgtopdf.py`: Main application source code
- `i18n.en.json`: English localization file
- `i18n.vi.json`: Vietnamese localization file
- `qtfluent-guide.md`: Comprehensive guide on PyQt-Fluent-Widgets
- `QWEN.md`: This documentation file

## Building and Running

### Prerequisites

1. Python 3.x installed on your system
2. Required Python packages (install via pip)

### Installation

1. Clone or download the project files
2. Install the required packages:

```bash
pip install PyQt6 PyQt6-Fluent-Widgets\[full\] Pillow
```

### Running the Application

Execute the main Python file:

```bash
python imgtopdf.py
```

## Configuration and Customization

### UI Settings

- Default output path: `C:/KavPDF/` (configurable in the UI)
- Window size: 900x700 pixels
- Default settings: Portrait orientation, original size, no margins

### Localization

The application supports multiple languages through JSON files:
- English: `i18n.en.json`
- Vietnamese: `i18n.vi.json`

To add a new language:
1. Create a new JSON file with the language code (e.g., `i18n.fr.json`)
2. Copy the structure from an existing file
3. Translate all the key-value pairs
4. Update the language combo box in the UI to include the new language option

## Development Conventions

### Code Structure

The application follows a single-file architecture with the following main components:

- `Lang` class: Handles internationalization and localization
- `DropListWidget` class: Custom QListWidget with drag-and-drop functionality
- `ImageToPDFWindow` class: Main application window with all UI and logic

### UI Design Patterns

- Uses PyQt6-Fluent-Widgets for modern Fluent Design interface
- Implements Qt's signal-slot mechanism for event handling
- Responsive design with proper layout management
- Theme support (light/dark/auto)

### Image Processing

- Converts images to RGB mode if they're in RGBA or P mode
- Supports resizing with LANCZOS resampling for quality
- Offers multiple compression levels (50%-100% quality)

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Ensure all required packages are installed via pip
2. **DPI Scaling**: The application sets High DPI scaling attributes for proper display on high-resolution screens
3. **Unsupported Image Formats**: The app supports PNG, JPG, JPEG, BMP, GIF, TIFF, and WEBP formats

### UI-Specific Issues

- If the application appears too small or too large, ensure High DPI scaling is properly configured
- On Windows, ensure Microsoft Visual C++ Redistributable is installed for proper DLL loading

## Application Workflow

1. **Image Selection**: Users can add images via "Add Images" button, "Add Folder" button, or drag-and-drop
2. **Configuration**: Set conversion method (one by one or all in one), compression level, and sorting options
3. **Output Path**: Specify output directory and save location for the PDF file
4. **Conversion**: Click "Convert" to start the conversion process
5. **Results**: Success or error messages are displayed via InfoBar notifications

## Customization Options

### UI Customization
- Change theme color using the centralized `ThemeManager` class
- Modify default window size by changing `resize()` parameters
- Adjust default output path by modifying the `output_path` variable

### Feature Extensions
- Add more image formats by updating the `exts` tuple
- Extend compression options by modifying the `get_quality_setting()` method
- Add more sorting options in the `sort_image_files()` method