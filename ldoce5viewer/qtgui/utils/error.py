"""Error console"""

import threading
from logging import StreamHandler

from PySide6.QtCore import QObject, QRecursiveMutex, Signal
from PySide6.QtWidgets import QPlainTextEdit


class MyStreamHandler(StreamHandler):
    def __init__(self):
        StreamHandler.__init__(self)
        self.createLock()

    def createLock(self):
        # Use standard threading lock for Python 3.13 compatibility
        self.lock = threading.RLock()

    def acquire(self):
        self.lock.acquire()

    def release(self):
        self.lock.release()


class StdErrWrapper(QObject):
    _write = Signal(str)
    _flush = Signal()

    def __init__(self, old_stderr):
        QObject.__init__(self)
        self._old_stderr = old_stderr
        self._widget = None
        self._mutex = QRecursiveMutex()

    def setApplication(self, app):
        assert self._widget is None

        widget = QPlainTextEdit()
        widget.setWindowTitle("Error Console")
        widget.resize(486, 300)
        widget.appendHtml(
            '<span style="color: green">'
            "An unhandled error occurred.<br>"
            "Sorry for the inconvinience.<br>"
            "Please copy the following text into a bug report:<br><br>"
            "</span>"
        )
        app.aboutToQuit.connect(self.restoreStdErr)
        self._write.connect(self._write_handler)
        self._flush.connect(self._flush_handler)
        self._widget = widget

    def _write_handler(self, data):
        self._mutex.lock()
        if self._widget:
            self._widget.show()
            self._widget.insertPlainText(data)
        self._mutex.unlock()

    def _flush_handler(self):
        self._mutex.lock()
        if self._widget:
            self._widget.show()
        self._mutex.unlock()

    def restoreStdErr(self):
        self._mutex.lock()
        if self._widget:
            self._widget.close()
            self._widget = None
        self._mutex.unlock()

    @property
    def encoding(self):
        return "utf-8"

    def write(self, s):
        self._mutex.lock()
        if self._widget:
            if isinstance(s, bytes):
                s = s.decode("utf-8", "replace")
            self._write.emit(s)
        else:
            self._old_stderr.write(s)
        self._mutex.unlock()

    def flush(self):
        self._mutex.lock()
        if self._widget:
            self._flush.emit()
        else:
            self._old_stderr.flush()
        self._mutex.unlock()
