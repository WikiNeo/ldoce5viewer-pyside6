# LDOCE5 Viewer (PySide6)

A modern dictionary viewer for the Longman Dictionary of Contemporary English 5th Edition (LDOCE 5).

This project has been migrated from PyQt5 to PySide6, bringing support for modern Qt features, HiDPI displays, and improved WebEngine functionality. **Recently upgraded to Python 3.13** with enhanced compatibility and performance improvements.

![LDOCE5 Viewer](ldoce5viewer/qtgui/resources/ldoce5viewer.png)

## Features

- **Modern Interface**: Clean, responsive UI with HiDPI support
- **Full-Text Search**: Fast search across dictionary entries, definitions, and examples
- **Audio Pronunciation**: Built-in audio playback for word pronunciations
- **Advanced Search**: Filter by word types, usage patterns, and more
- **Export & Print**: Print dictionary entries or export to various formats
- **Cross-Platform**: Works on macOS, Linux, and Windows
- **Wayland Compatibility**: Automatic Wayland detection and X11 fallback for optimal performance
- **Python 3.13 Ready**: Fully compatible with the latest Python version

## Prerequisites

### System Requirements

- **Python**: 3.13 or higher (recommended for optimal performance and security)
- **Qt**: PySide6 6.8.x (installed automatically - stable version for best compatibility)
- **Dictionary Data**: LDOCE 5 CD/DVD or digital copy

> **Note**: This project has been recently upgraded to require Python 3.13, bringing improved performance, better security, and modern language features. All deprecated modules have been updated for full compatibility.

### Package Manager

We recommend using [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Alternatively, you can use `pip` with a virtual environment, but ensure you have Python 3.13 installed.

## Installation

### Arch Linux Installation (Recommended)

For Arch Linux users, we provide an automated installation script:

```bash
# Ensure you have Python 3.13 installed
sudo pacman -S python

# Run the installation script
./install-arch.sh
```

The installation script will:
- ✅ Install all dependencies using `uv` with Python 3.13
- ✅ Set up desktop integration (application menu entry)
- ✅ Install application icons
- ✅ Create a robust launcher script that works from anywhere
- ✅ Configure Wayland compatibility automatically
- ✅ Enable launching from task managers and system tools

After installation, you can launch the application from:
- **Application menu** (search for "LDOCE5 Viewer")
- **Command line**: `~/.local/bin/ldoce5viewer`
- **Task managers** and system monitoring tools

### Development Installation

For development or if you want the latest features:

```bash
# Ensure Python 3.13 is active
python --version  # Should show 3.13.x

# Install dependencies
uv sync

# Run the application
uv run python ldoce5viewer.py
```

### Generic Linux Installation

For other Linux distributions:

```bash
# Install Python 3.13 (example for Ubuntu 24.04+)
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev

# Install dependencies
uv sync

# Install the package
uv pip install -e .

# Run the application
uv run python ldoce5viewer.py
```

## Recent Updates (Python 3.13 Upgrade)

### What's New

- **🚀 Python 3.13 Support**: Fully compatible with the latest Python version
- **🔧 Improved Compatibility**: All deprecated modules updated (distutils, imp, SafeConfigParser)
- **🛡️ Enhanced Security**: Benefits from Python 3.13's security improvements
- **⚡ Better Performance**: Leverages Python 3.13's performance optimizations
- **🐛 Bug Fixes**: Resolved logging compatibility issues and crash-related problems

### Compatibility Notes

- **PySide6 Version**: Using stable PySide6 6.8.x for maximum compatibility
- **Logging System**: Updated custom handlers for Python 3.13 compatibility
- **Configuration**: Updated ConfigParser usage for modern Python
- **Build System**: Migrated from distutils to setuptools

### Migration from Older Versions

If upgrading from an older installation:

```bash
# Clean old environment
uv clean

# Reinstall with Python 3.13
uv sync

# Rebuild UI components if needed
cd ldoce5viewer/qtgui/ui && make clean && make
cd ../resources && make clean && make
```

## Platform-Specific Setup

### Arch Linux

The application automatically handles Wayland compatibility by detecting your session and switching to X11 when needed. This prevents the common QtWebEngine freezing issue on Wayland.

**Required packages:**
```bash
# Install Python 3.13 and essential tools
sudo pacman -S python python-pip

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# For audio support
sudo pacman -S gstreamer gst-plugins-base gst-plugins-good

# For better font support
sudo pacman -S ttf-liberation ttf-dejavu
```

### Other Linux Distributions

**Ubuntu/Debian (24.04+ for Python 3.13):**
```bash
# Install Python 3.13 and development tools
sudo apt install python3.13 python3.13-dev python3.13-venv libxml2-dev libxslt1-dev

# For audio support
sudo apt install gstreamer1.0-plugins-base gstreamer1.0-plugins-good
```

**Fedora (40+ for Python 3.13):**
```bash
# Install Python 3.13 and development tools
sudo dnf install python3.13 python3.13-devel libxml2-devel libxslt-devel

# For audio support
sudo dnf install gstreamer1-plugins-base gstreamer1-plugins-good
```

## Development Setup

### Setting Up Your Development Environment

1. **Verify Python Version**
   ```bash
   python --version  # Should be 3.13.x
   ```

2. **Install Dependencies**
   ```bash
   uv sync
   ```

3. **Set Up Dictionary Data**
   - Copy your LDOCE 5 data to `~/Documents/LDOEC5 Data/ldoce5.data/`
   - The directory should contain `.skn` files and other dictionary data

4. **Run the Application**
   ```bash
   uv run python ldoce5viewer.py
   ```

### Building UI Files

The project uses Qt Designer `.ui` files that need to be compiled:

```bash
# Build UI files
cd ldoce5viewer/qtgui/ui
make

# Build resource files
cd ../resources
make
```

### Development Dependencies

The project uses these main dependencies:

- **PySide6**: Qt6 bindings for Python (6.8.x for stability)
- **lxml**: XML processing
- **whoosh**: Full-text search engine
- **setuptools**: Modern build system (replaces deprecated distutils)
- **Python 3.13**: Latest Python with improved performance and security

## Project Structure

```
ldoce5viewer-pyside6/
├── ldoce5viewer/           # Main application package
│   ├── __init__.py
│   ├── ldoce5/            # Dictionary data processing
│   │   ├── extract.py     # Data extraction from LDOCE files
│   │   ├── idmreader.py   # IDM file reader
│   │   └── ...
│   ├── qtgui/             # GUI components
│   │   ├── main.py        # Main window
│   │   ├── access.py      # URL scheme handlers
│   │   ├── config.py      # Configuration management
│   │   ├── ui/            # UI files (.ui)
│   │   ├── resources/     # Icons and static files
│   │   └── utils/         # Utility modules
│   ├── static/            # Web assets (CSS, JS, images)
│   └── utils/             # General utilities
├── scripts/               # Launcher scripts
├── install-arch.sh        # Arch Linux installation script
├── pyproject.toml         # Project configuration
├── setup.py              # Setup script
├── ldoce5viewer.desktop   # Desktop integration file
└── README.md             # This file
```

## Configuration

### Dictionary Data Setup

1. **Locate your LDOCE 5 data**
   - From CD/DVD: Copy the entire disc contents
   - From digital download: Extract the installation files

2. **Create the data directory**
   ```bash
   mkdir -p ~/Documents/LDOEC5\ Data/ldoce5.data
   ```

3. **Copy dictionary files**
   - Copy all `.skn` files to the data directory
   - Copy supporting files (images, audio, etc.)

4. **Generate file index**
   - First run will automatically generate the file index
   - This may take several minutes

### Application Settings

The application stores settings in:
- **Linux**: `~/.config/LDOCE5Viewer/`
- **macOS**: `~/Library/Application Support/LDOCE5Viewer/`
- **Windows**: `%APPDATA%/LDOCE5Viewer/`

## Troubleshooting

### Common Issues

#### Dictionary Data Not Found
```
Error: Dictionary data not found
```
**Solution**: Ensure LDOCE 5 data is in `~/Documents/LDOEC5 Data/ldoce5.data/`

#### Configuration Missing
```
Dictionary Data Not Available (empty dataDir configuration)
```
**Solution**: The app needs to know where your dictionary data is located. Run the app once and use the indexing dialog to set the data directory, or manually configure it by running the app and going through the initial setup.

#### File Index Missing
```
Error: File-Location Map Not Available
```
**Solution**: Delete `~/.config/LDOCE5Viewer/filemap.cdb` and restart to regenerate the index

#### Audio Not Playing
```
Audio files not found or unsupported format
```
**Solution**: Check audio backend installation and file permissions

#### WebEngine Errors
```
Please register the custom scheme 'dict' via QWebEngineUrlScheme::registerScheme()
```
**Solution**: This is a known warning and doesn't affect functionality

### Platform-Specific Issues

#### Arch Linux

**Wayland Freezing Issues**: The application automatically detects Wayland and switches to X11 compatibility mode. If you see the message "Detected Wayland session, forcing X11 compatibility for QtWebEngine", this is normal and ensures the application works properly.

**Task Manager Launch Issues**: The application now works correctly when launched from task managers, system monitors, or other system tools.

#### Dependencies**: 
```bash
# Install missing dependencies (Arch Linux)
sudo pacman -S python python-pip uv

# Verify Python 3.13 installation
python --version  # Should show 3.13.x
```

#### Other Linux Distributions

- **Python Version**: Ensure Python 3.13 is installed and active
- **Missing Dependencies**: Install `libxml2-dev` and `libxslt1-dev` on Debian/Ubuntu
- **PySide6 Issues**: If you encounter Qt-related crashes, the application automatically uses PySide6 6.8.x for stability
- **Audio Backend**: Install `gstreamer` or `pulseaudio` for audio support
- **Font Issues**: Install Microsoft fonts for better compatibility

#### Python 3.13 Specific Issues

**ImportError with logging module**:
```
AttributeError: 'MyStreamHandler' object has no attribute 'lock'
```
**Solution**: This has been fixed in the current version. Update to the latest code.

**Deprecated module warnings**:
```
ModuleNotFoundError: No module named 'distutils'
```
**Solution**: The project now uses setuptools. Run `uv sync` to update dependencies.

**Configuration parser issues**:
```
ImportError: cannot import name 'SafeConfigParser'
```
**Solution**: Fixed in the current version using modern ConfigParser.

#### macOS/Windows

- **Path Issues**: Use forward slashes in paths
- **Audio**: Ensure appropriate audio backends are available
- **Permissions**: Grant necessary file access permissions

### Debug Mode

Run with debug output:

```bash
uv run python ldoce5viewer.py --debug
```

This will show detailed logging information to help diagnose issues.

## Contributing

### Getting Started

1. **Ensure Python 3.13**: Verify you have Python 3.13 installed
   ```bash
   python --version  # Should show 3.13.x
   ```
2. Fork the repository
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Install development dependencies (`uv sync`)
5. Make your changes
6. Run tests and ensure code quality
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate (Python 3.13 style)
- Document new features and API changes
- Add tests for new functionality
- Ensure Python 3.13 compatibility for any new dependencies

### Project Maintenance

Keep the project clean:

```bash
# Remove build artifacts and cache files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

# Clean uv cache if needed
uv clean

# The .gitignore file automatically excludes:
# - Build artifacts (*.egg-info/, build/, dist/)
# - Python cache (__pycache__/, *.pyc)
# - IDE files (.idea/, .vscode/)
# - OS files (.DS_Store, Thumbs.db)
# - Temporary/debug files (debug_*.py, test_*.py)
```

### Testing

```bash
# Verify Python version first
python --version  # Should be 3.13.x

# Run basic functionality test
python -m pytest tests/ || echo "Test framework not yet implemented"

# Test application startup
uv run python ldoce5viewer.py --debug

# Test installation (after running install script)
~/.local/bin/ldoce5viewer --debug

# Test build process
cd ldoce5viewer/qtgui/ui && make clean && make
cd ../resources && make clean && make
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.txt](LICENSE.txt) file for details.

## References

- [LDOCE 5 Official Website](https://www.ldoceonline.com/)
- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [Python 3.13 Release Notes](https://docs.python.org/3.13/whatsnew/3.13.html)
- [CDB Database Format](https://en.wikipedia.org/wiki/Cdb_(software))
- [Qt WebEngine](https://doc.qt.io/qt-6/qtwebengine-index.html)
- [uv Package Manager](https://github.com/astral-sh/uv)

## Acknowledgments

- Original LDOCE5 Viewer developers
- Qt/PySide6 development team
- Contributors and beta testers

---

**Note**: This project is not affiliated with Pearson Education or Longman. LDOCE 5 is a trademark of Pearson Education Limited.
