#!/bin/bash

# LDOCE5 Viewer Installation Script for macOS
# This script installs LDOCE5 Viewer with full macOS integration

set -e  # Exit on any error

echo "🍎 Installing LDOCE5 Viewer for macOS..."
echo "========================================"

# Check if we're in the right directory
if [ ! -f "ldoce5viewer.py" ] || [ ! -d "ldoce5viewer" ]; then
    echo "❌ Error: Please run this script from the ldoce5viewer project root directory"
    echo "   Make sure you've cloned the repository first:"
    echo "   git clone https://github.com/yourusername/ldoce5viewer-pyside6.git"
    echo "   cd ldoce5viewer-pyside6"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed"
    echo "   Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   Or use Homebrew: brew install uv"
    exit 1
fi

echo "📦 Installing dependencies using uv..."
uv sync

echo "🔧 Installing the application..."
uv pip install -e .

echo "🎨 Setting up macOS application bundle..."

# Create application bundle structure
APP_NAME="LDOCE5 Viewer"
APP_BUNDLE="$HOME/Applications/${APP_NAME}.app"
CONTENTS_DIR="${APP_BUNDLE}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

# Remove existing app bundle if it exists
if [ -d "$APP_BUNDLE" ]; then
    echo "🗑️  Removing existing application bundle..."
    rm -rf "$APP_BUNDLE"
fi

# Create directory structure
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

echo "📄 Creating Info.plist..."
# Create Info.plist
cat > "${CONTENTS_DIR}/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleDevelopmentRegion</key>
	<string>en</string>
	<key>CFBundleDisplayName</key>
	<string>LDOCE5 Viewer</string>
	<key>CFBundleExecutable</key>
	<string>ldoce5viewer</string>
	<key>CFBundleIconFile</key>
	<string>ldoce5viewer.icns</string>
	<key>CFBundleIdentifier</key>
	<string>net.hakidame.ldoce5viewer</string>
	<key>CFBundleInfoDictionaryVersion</key>
	<string>6.0</string>
	<key>CFBundleName</key>
	<string>LDOCE5 Viewer</string>
	<key>CFBundlePackageType</key>
	<string>APPL</string>
	<key>CFBundleShortVersionString</key>
	<string>0.1.0</string>
	<key>CFBundleVersion</key>
	<string>1</string>
	<key>LSApplicationCategoryType</key>
	<string>public.app-category.education</string>
	<key>LSMinimumSystemVersion</key>
	<string>10.15</string>
	<key>NSHighResolutionCapable</key>
	<true/>
	<key>NSRequiresAquaSystemAppearance</key>
	<false/>
	<key>CFBundleDocumentTypes</key>
	<array>
		<dict>
			<key>CFBundleTypeDescription</key>
			<string>LDOCE5 Dictionary Data</string>
			<key>CFBundleTypeExtensions</key>
			<array>
				<string>ldoce5</string>
			</array>
			<key>CFBundleTypeName</key>
			<string>LDOCE5 Dictionary</string>
			<key>CFBundleTypeRole</key>
			<string>Viewer</string>
			<key>LSHandlerRank</key>
			<string>Owner</string>
		</dict>
	</array>
	<key>NSAppleScriptEnabled</key>
	<true/>
	<key>NSPrincipalClass</key>
	<string>NSApplication</string>
</dict>
</plist>
EOF

echo "🖼️  Copying application icon..."
# Copy icon file
if [ -f "ldoce5viewer/qtgui/resources/ldoce5viewer.icns" ]; then
    cp "ldoce5viewer/qtgui/resources/ldoce5viewer.icns" "$RESOURCES_DIR/"
else
    echo "⚠️  Warning: ldoce5viewer.icns not found, using PNG icon as fallback"
    if [ -f "ldoce5viewer/qtgui/resources/ldoce5viewer.png" ]; then
        cp "ldoce5viewer/qtgui/resources/ldoce5viewer.png" "$RESOURCES_DIR/ldoce5viewer.icns"
    fi
fi

echo "🚀 Creating launcher executable..."
# Create launcher script
cat > "${MACOS_DIR}/ldoce5viewer" << EOF
#!/bin/bash

# LDOCE5 Viewer Launcher Script for macOS
# This script launches the LDOCE5 Viewer with proper environment setup

# Set up environment variables for consistent behavior
export LANG="\${LANG:-en_US.UTF-8}"
export LC_ALL="\${LC_ALL:-en_US.UTF-8}"

# Set the project directory
PROJECT_DIR="$PWD"

# Change to the project directory
cd "\$PROJECT_DIR" || {
    # Try to find the project directory relative to the app bundle
    SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
    APP_DIR="\$(dirname "\$(dirname "\$(dirname "\$SCRIPT_DIR")")")"
    PROJECT_DIR="\$APP_DIR"
    
    cd "\$PROJECT_DIR" || {
        echo "Error: Cannot find LDOCE5 Viewer project directory"
        echo "Expected location: \$PROJECT_DIR"
        osascript -e 'display alert "LDOCE5 Viewer Error" message "Cannot find project directory. Please reinstall the application." buttons {"OK"} default button "OK"'
        exit 1
    }
}

# Function to find uv in common macOS locations
find_uv() {
    # Check if uv is in PATH
    if command -v uv &> /dev/null; then
        command -v uv
        return 0
    fi
    
    # Common locations where uv might be installed on macOS
    local uv_locations=(
        "\$HOME/.local/bin/uv"
        "\$HOME/.cargo/bin/uv"
        "/usr/local/bin/uv"
        "/opt/homebrew/bin/uv"
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
    osascript -e 'display alert "LDOCE5 Viewer Error" message "Cannot find uv executable. Please install uv from https://docs.astral.sh/uv/" buttons {"OK"} default button "OK"'
    exit 1
fi

# Set up additional PATH entries for common macOS locations
export PATH="\$HOME/.local/bin:\$HOME/.cargo/bin:/usr/local/bin:/opt/homebrew/bin:\$PATH"

# Launch the application using uv with full path
# Redirect output to avoid console spam in GUI mode
exec "\$UV_PATH" run python ldoce5viewer.py "\$@" 2>/dev/null
EOF

# Make the launcher script executable
chmod +x "${MACOS_DIR}/ldoce5viewer"

echo "🔗 Creating command-line symlink..."
# Create a symlink in /usr/local/bin for command-line access
sudo mkdir -p /usr/local/bin 2>/dev/null || true
if sudo ln -sf "${MACOS_DIR}/ldoce5viewer" /usr/local/bin/ldoce5viewer 2>/dev/null; then
    echo "✅ Command-line launcher created at /usr/local/bin/ldoce5viewer"
else
    echo "⚠️  Could not create command-line launcher (requires sudo)"
    echo "   You can manually create it later with:"
    echo "   sudo ln -sf '${MACOS_DIR}/ldoce5viewer' /usr/local/bin/ldoce5viewer"
fi

echo "🔄 Updating Launch Services database..."
# Register the app with Launch Services
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP_BUNDLE"

echo ""
echo "✅ LDOCE5 Viewer installed successfully!"
echo "======================================="
echo ""
echo "You can now launch it from:"
echo "  🍎 Applications folder (Finder → Applications → LDOCE5 Viewer)"
echo "  🔍 Spotlight search (Cmd+Space, type 'LDOCE5')"
echo "  🖥️  Launchpad"
echo "  💻 Command line: ldoce5viewer (if symlink was created)"
echo "  📁 Dock (drag from Applications folder)"
echo ""
echo "ℹ️  Notes:"
echo "  • The application is installed as a native macOS app bundle"
echo "  • First run will ask you to set up your LDOCE5 dictionary data"
echo "  • The app supports macOS dark mode and Retina displays"
echo "  • Audio playback uses native macOS frameworks (AVFoundation)"
echo ""
echo "🎉 Installation complete!" 