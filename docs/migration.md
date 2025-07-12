# Migration

## LDOCE5 Viewer Migration: PyQt5 → PySide6

### **Core Framework Migration**
1. **Dependencies Updated** - Changed `pyproject.toml` from PyQt5 to PySide6 packages
2. **Import Statements** - Updated all Python files to use `PySide6.*` instead of `PyQt5.*`
3. **WebKit → WebEngine** - Replaced deprecated PyQt5 WebKit with PySide6 WebEngine
4. **SIP References** - Updated PyQt5.sip references to PySide6 equivalents
5. **UI Files** - Updated .ui files to reference PySide6 instead of PyQt5

### **Project Branding & Documentation**
6. **Project Name** - Updated from "ldoce5viewer-pyqt5" to reflect PySide6 usage
7. **Documentation** - Updated README and other docs to reflect the migration

### **Critical Functionality Fixes** (this session)
8. **Audio Playback System** - Fixed broken audio after migration:
   - **Backend Detection**: Implemented proper audio backend selection (QtMultimedia vs AppKit)
   - **QtMultimedia Integration**: Fixed PySide6 audio output configuration with `QAudioOutput`
   - **Cross-platform Support**: Ensured audio works on both macOS (AppKit) and other platforms
   - **Debug Logging**: Added comprehensive debug output for troubleshooting

9. **UI/UX Improvements**:
   - **Cursor Styling**: Added pointer cursor on hover for audio play buttons
   - **Better Visual Feedback**: Improved user experience with clickable element indication

### **Technical Architecture Changes**
- **WebEngine Integration**: Successfully migrated from WebKit to WebEngine while maintaining all URL scheme handlers
- **Audio URL Handling**: Maintained custom audio:// URL scheme through navigation interception
- **Static Asset Serving**: Preserved all static file serving (CSS, JS, images) through custom URL scheme handlers

### **Result**
✅ **Fully functional PySide6-based dictionary application** with:
- Working audio pronunciation playback
- Proper web content rendering
- Maintained all original features
- Enhanced user experience
- Cross-platform compatibility

The migration successfully modernized the application from the deprecated PyQt5 framework to the actively maintained PySide6, ensuring long-term viability while preserving all functionality.