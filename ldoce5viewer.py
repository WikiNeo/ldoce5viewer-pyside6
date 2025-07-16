#!/usr/bin/env python3

import sys
import os
import warnings

# Fix for Wayland compatibility with QtWebEngine
# QtWebEngine often freezes on Wayland, so we force X11 on Wayland systems
if os.environ.get('WAYLAND_DISPLAY') or os.environ.get('XDG_SESSION_TYPE') == 'wayland':
    if 'QT_QPA_PLATFORM' not in os.environ:
        os.environ['QT_QPA_PLATFORM'] = 'xcb'
        print("Detected Wayland session, forcing X11 compatibility for QtWebEngine")

# Suppress syntax warning from whoosh library (uses "is 0" instead of "== 0")
warnings.filterwarnings("ignore", message='"is" with a literal', category=SyntaxWarning)

from ldoce5viewer import qtgui


if __name__ == '__main__':
    sys.exit(qtgui.run(sys.argv))

