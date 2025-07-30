#!/bin/bash

# LDOCE5 Viewer Installation Script for Arch Linux
# This script installs LDOCE5 Viewer with full desktop integration

set -e  # Exit on any error

echo "🔧 Installing LDOCE5 Viewer for Arch Linux..."
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "ldoce5viewer.py" ] || [ ! -d "ldoce5viewer" ]; then
    echo "❌ Error: Please run this script from the ldoce5viewer project root directory"
    echo "   Make sure you've cloned the repository first:"
    echo "   git clone https://github.com/yourusername/ldoce5viewer-pyqt5.git"
    echo "   cd ldoce5viewer-pyqt5"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed"
    echo "   Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "📦 Installing dependencies using uv..."
uv sync

echo "🔧 Installing the application with desktop integration..."
uv pip install -e .

echo "🎨 Setting up desktop integration (launcher and icons)..."
mkdir -p ~/.local/share/applications ~/.local/share/icons/hicolor/scalable/apps ~/.local/bin

# Copy icons
cp ldoce5viewer/qtgui/resources/ldoce5viewer.svg ~/.local/share/icons/hicolor/scalable/apps/
cp ldoce5viewer/qtgui/resources/ldoce5viewer.png ~/.local/share/icons/hicolor/scalable/apps/

# Copy desktop file
cp ldoce5viewer.desktop ~/.local/share/applications/

echo "🚀 Creating launcher script..."
# Create launcher script
cat > ~/.local/bin/ldoce5viewer << EOF
#!/bin/bash

# LDOCE5 Viewer Launcher Script
# This script launches the LDOCE5 Viewer with proper environment setup
# Works from desktop launcher, command line, and task managers

# Set up environment variables for consistent behavior
export LANG="\${LANG:-en_US.UTF-8}"
export LC_ALL="\${LC_ALL:-en_US.UTF-8}"

# Set the project directory (adjust if needed)
PROJECT_DIR="$PWD"

# Change to the project directory
cd "\$PROJECT_DIR" || {
    echo "Error: Cannot find LDOCE5 Viewer project directory at \$PROJECT_DIR"
    echo "Please update the PROJECT_DIR variable in this script to point to the correct location."
    exit 1
}

# Function to find uv in common locations
find_uv() {
    # Check if uv is in PATH
    if command -v uv &> /dev/null; then
        command -v uv
        return 0
    fi

    # Common locations where uv might be installed
    local uv_locations=(
        "\$HOME/.local/bin/uv"
        "\$HOME/.cargo/bin/uv"
        "/usr/local/bin/uv"
        "/usr/bin/uv"
    )

    for location in "\${uv_locations[@]}"; do
        if [ -x "\$location" ]; then
            echo "\$location"
            return 0
        fi
    done

    return 1
}

# Find uv
UV_PATH=\$(find_uv)
if [ \$? -ne 0 ]; then
    echo "Error: Cannot find uv executable"
    echo "Please install uv: https://docs.astral.sh/uv/"
    echo "Or update this script to include the correct path to uv"
    exit 1
fi

# Set up additional PATH entries for common locations
export PATH="\$HOME/.local/bin:\$HOME/.cargo/bin:/usr/local/bin:\$PATH"

# Launch the application using uv with full path
exec "\$UV_PATH" run python ldoce5viewer.py "\$@"
EOF

# Make the launcher script executable
chmod +x ~/.local/bin/ldoce5viewer

echo "⚙️  Updating desktop file configuration..."
# Update the desktop file to use the correct launcher
sed -i "s|Exec=ldoce5viewer|Exec=$HOME/.local/bin/ldoce5viewer|" ~/.local/share/applications/ldoce5viewer.desktop
echo "Path=$PWD" >> ~/.local/share/applications/ldoce5viewer.desktop

echo "🔄 Updating desktop database..."
# Update desktop database
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
gtk-update-icon-cache ~/.local/share/icons/hicolor/ 2>/dev/null || true

echo ""
echo "✅ LDOCE5 Viewer installed successfully!"
echo "========================================"
echo ""
echo "You can now launch it from:"
echo "  📱 Application menu (search for 'LDOCE5 Viewer')"
echo "  💻 Command line: ~/.local/bin/ldoce5viewer"
echo "  🔧 Task managers and system tools"
echo ""
echo "ℹ️  Notes:"
echo "  • The application automatically handles Wayland compatibility"
echo "  • First run will ask you to set up your LDOCE5 dictionary data"
echo "  • For audio support, you may need: sudo pacman -S gstreamer gst-plugins-base gst-plugins-good"
echo ""
echo "🎉 Installation complete!"
