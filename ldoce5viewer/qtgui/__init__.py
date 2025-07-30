"""Entry point for the application"""

import codecs
import logging
import os.path
import sys
from optparse import OptionParser

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLineEdit

from .. import __author__
from .access import register_url_schemes
from .config import get_config
from .utils.error import MyStreamHandler, StdErrWrapper
from .utils.singleapp import SingleApplication

_SINGLEAPP_KEY = "ed437af1-0388-4e13-90e9-486bdc88c77a"

# set a dummy function if QLineEdit doesn't have setPlaceholderText
if not hasattr(QLineEdit, "setPlaceholderText"):

    def _dummySetPlaceholderText(self, *args, **kwargs):
        pass

    QLineEdit.setPlaceholderText = _dummySetPlaceholderText


def _setup_py2exe(config):
    # suspend py2exe's logging facility
    log_path = os.path.join(config._config_dir, "log.txt")
    try:
        f = codecs.open(log_path, "w", encoding="utf-8")
    except:
        pass
    else:
        sys.stderr = f


def run(argv):
    """start the application"""

    # CRITICAL: Register URL schemes BEFORE creating QApplication
    # This fixes the "Please register the custom scheme via QWebEngineUrlScheme::registerScheme()" warning
    # and ensures proper WebEngine functionality in all launch contexts
    register_url_schemes()

    config = get_config()

    # py2exe
    if sys.platform == "win32" and (
        hasattr(sys, "frozen") or hasattr(sys, "importers")
    ):
        _setup_py2exe(config)

    # Parse arguments
    optparser = OptionParser()
    optparser.set_defaults(debug=False)
    optparser.add_option("--debug", action="store_true", help="Enable debug mode")
    (options, args) = optparser.parse_args(argv)

    # stderr wrapper
    sys.stderr = StdErrWrapper(sys.stderr)

    # logging
    logger = logging.getLogger()
    handler = MyStreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if options.debug else logging.ERROR)

    # Create an application instance (URL schemes must be registered before this)
    app = SingleApplication(argv, _SINGLEAPP_KEY)
    if app.isRunning():
        app.sendMessage("activate")
        return 1

    # Load the configuration file
    config.debug = options.debug
    config.load()

    # Set the application's information
    app.setApplicationName(config.app_name)
    app.setOrganizationName(__author__)
    app.setWindowIcon(QIcon(":/icons/icon.png"))

    # Setup MainWindow
    from .main import MainWindow

    main_window = MainWindow()

    def messageHandler(msg):
        if msg == "activate":
            main_window.activateWindow()
            main_window.setVisible(True)

    app.messageAvailable.connect(messageHandler)

    # On Windows-ja
    if app.font().family() == "MS UI Gothic":
        cand = (("Segoe UI", None), ("Meiryo UI", None), ("Tahoma", 8))
        from PySide6.QtGui import QFont

        for name, point in cand:
            ps = app.font().pointSize()
            if point is None:
                point = ps if ps != -1 else 9
            font = QFont(name, point)
            if font.exactMatch():
                app.setFont(font)
                break

    # Redirect stderr to the Error Console
    if not options.debug:
        sys.stderr.setApplication(app)

    # Start the application
    r = app.exec_()

    # Quit
    config.save()
    return r
