# LDOCE5 Viewer (PySide6)

A modern dictionary viewer for the Longman Dictionary of Contemporary English 5th Edition (LDOCE 5).

![LDOCE5 Viewer](ldoce5viewer/qtgui/resources/ldoce5viewer.png)

## Features

- **Modern Interface**: Clean, responsive UI with HiDPI support
- **Full-Text Search**: Fast search across dictionary entries, definitions, and examples
- **Audio Pronunciation**: Built-in audio playback for word pronunciations
- **Cross-Platform**: Works on macOS, Linux

## Prerequisites

- **Python**: 3.13 or higher
- **Dictionary Data**: LDOCE 5 CD/DVD or digital copy
- **uv package manager**: [Install uv](https://docs.astral.sh/uv/)

## Installation

### Linux (Arch Linux)

```bash
# Clone the repository
git clone https://github.com/yourusername/ldoce5viewer-pyside6.git
cd ldoce5viewer-pyside6

# Run the installation script
./install-arch.sh
```

**Launch from:**

- Application menu (search "LDOCE5 Viewer")
- Command line: `ldoce5viewer`

### macOS

```bash
# Clone the repository
git clone https://github.com/yourusername/ldoce5viewer-pyside6.git
cd ldoce5viewer-pyside6

# Run the installation script
./install-macos.sh
```

**Launch from:**

- Command line: `ldoce5viewer`

### Development Installation

```bash
# Clone repository
git clone https://github.com/yourusername/ldoce5viewer-pyside6.git
cd ldoce5viewer-pyside6

# Install dependencies
uv sync

# Run in development mode
uv run python ldoce5viewer.py
```

## First-Time Setup

1. **Launch the application** (using any method above)
2. **Welcome dialog** will appear asking to create index database
3. **Browse for dictionary data**: Locate your `ldoce5.data` folder
4. **Wait for indexing**: Takes 3-10 minutes to build database
5. **Start using**: Search for words and view definitions

## Dictionary Data

You need the **LDOCE5 dictionary data files** from:

- Official LDOCE5 CD/DVD
- Legitimate LDOCE5 installation
- Files are typically in a folder called `ldoce5.data` containing `.skn` files

## Troubleshooting

### Platform-Specific

**Arch Linux Audio Support:**

```bash
sudo pacman -S gstreamer gst-plugins-base gst-plugins-good
```

**macOS Permissions:**
The app may ask for microphone/audio permissions for pronunciation features.

## License

This project is licensed under the GNU General Public License v3.0 or later (GPLv3+).
