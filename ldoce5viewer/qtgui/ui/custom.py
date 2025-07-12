from __future__ import absolute_import
from __future__ import print_function

import sys
import os.path
from PySide6.QtCore import (Qt, QUrl, QTimer, Signal, QMimeData, QSize, QRect,
                               QEvent, QPointF, QByteArray, QIODevice, QBuffer)
from PySide6.QtGui import (QFont, QPixmap, QBrush, QColor, QPainter, QIcon,
                             QKeySequence, QDesktopServices, QAction, QTextDocument)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import (QListWidget, QListWidgetItem, QApplication, QMenu,
                                 QTextEdit, QFrame, QVBoxLayout, QScrollArea,
                                 QLabel, QWidget, QHBoxLayout, QSplitter, QStyle, QToolButton,
                                 QLineEdit, QStyledItemDelegate, QSizeGrip, QStyleOptionToolButton,
                                 QStylePainter)
from ...utils.text import ellipsis


DisplayRole = Qt.DisplayRole
State_Selected = QStyle.State_Selected


INDEX_SELECTED_COLOR = QColor(228, 228, 228)


class ToolButton(QToolButton):
    """QToolButton without menu-arrow"""

    def paintEvent(self, event):
        opt = QStyleOptionToolButton()
        self.initStyleOption(opt)
        opt.features &= ~QStyleOptionToolButton.HasMenu
        painter = QStylePainter(self)
        painter.drawComplexControl(QStyle.CC_ToolButton, opt)

    def sizeHint(self):
        opt = QStyleOptionToolButton()
        self.initStyleOption(opt)
        opt.features &= ~QStyleOptionToolButton.HasMenu
        content_size = opt.iconSize
        return self.style().sizeFromContents(
                QStyle.CT_ToolButton, opt, content_size, self)


class LineEdit(QLineEdit):
    """QLineEdit with a clear button"""

    _ICONSIZE = 16
    escapePressed = Signal()
    shiftReturnPressed = Signal()

    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)
        ICONSIZE = self._ICONSIZE

        self._buttonFind = QToolButton(self)
        self._buttonFind.setCursor(Qt.ArrowCursor);
        self._buttonFind.setIconSize(QSize(ICONSIZE, ICONSIZE))
        self._buttonFind.setIcon(QIcon(':/icons/edit-find.png'))
        self._buttonFind.setStyleSheet(
                "QToolButton { border: none; margin: 0; padding: 0; }")
        self._buttonFind.setFocusPolicy(Qt.NoFocus)
        self._buttonFind.clicked.connect(self.selectAll)

        self._buttonClear = QToolButton(self)
        self._buttonClear.hide();
        self._buttonClear.setToolTip("Clear")
        self._buttonClear.setCursor(Qt.ArrowCursor);
        self._buttonClear.setIconSize(QSize(ICONSIZE, ICONSIZE))
        self._buttonClear.setIcon(QIcon(':/icons/edit-clear.png'))
        self._buttonClear.setStyleSheet(
                "QToolButton { border: none; margin: 0; padding: 0; }")
        self._buttonClear.setFocusPolicy(Qt.NoFocus)
        self._buttonClear.clicked.connect(self.clear);

        minsize = self.minimumSizeHint()
        framewidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        margin = self.textMargins()
        margin.setLeft(3 + ICONSIZE + 1)
        margin.setRight(1 + ICONSIZE + 3)
        self.setTextMargins(margin)

        height = max(minsize.height(), ICONSIZE + (framewidth + 2) * 2)
        self.setMinimumSize(
            max(minsize.width(), (ICONSIZE + framewidth + 2 + 2) * 2),
            int(height / 2.0 + 0.5) * 2)

        self.textChanged.connect(self.__onTextChanged)

    def resizeEvent(self, event):
        ICONSIZE = self._ICONSIZE
        framewidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        rect = self.rect()
        self._buttonFind.move(
                framewidth + 3 - 1,
                (rect.height() - ICONSIZE) // 2 - 1)
        self._buttonClear.move(
                rect.width() - framewidth - 3 - ICONSIZE - 1,
                (rect.height() - ICONSIZE) // 2 - 1)

    def __onTextChanged(self, text):
        self._buttonClear.setVisible(bool(text))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.escapePressed.emit()
        elif event.key() == Qt.Key_Return and \
                event.modifiers() & Qt.ShiftModifier:
            self.shiftReturnPressed.emit()
        else:
            super(LineEdit, self).keyPressEvent(event)


class LineEditFind(QLineEdit):
    shiftReturnPressed = Signal()
    escapePressed = Signal()

    def __init__(self, parent):
        super(LineEditFind, self).__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.escapePressed.emit()
        elif event.key() == Qt.Key_Return and \
                event.modifiers() == Qt.ShiftModifier:
            self.shiftReturnPressed.emit()
        elif event.key() == Qt.Key_Return:
            self.returnPressed.emit()
        else:
            super(LineEditFind, self).keyPressEvent(event)


class HtmlListWidget(QListWidget):

    class HtmlItemDelegate(QStyledItemDelegate):

        MARGIN_H = 5
        if sys.platform.startswith("win"):
            MARGIN_V = 3
        elif sys.platform.startswith("darwin"):
            MARGIN_V = 4
        else:
            MARGIN_V = 5

        def __init__(self, parent=None):
            super(HtmlListWidget.HtmlItemDelegate, self).__init__(parent)
            self._doc = QTextDocument()
            self._doc.setDocumentMargin(0)
            self._item_size = None

        def paint(self, painter, option, index):
            doc = self._doc
            painter.resetTransform()
            rect = option.rect
            if option.state & State_Selected:
                painter.fillRect(rect, INDEX_SELECTED_COLOR)
            doc.setHtml(index.data(DisplayRole))
            px = rect.x() + self.MARGIN_H
            py = rect.y() + self.MARGIN_V
            painter.translate(px, py)
            doc.drawContents(painter)

        def sizeHint(self, option, index):
            s = self._item_size
            if not s:
                doc = self._doc
                doc.setDefaultFont(option.font)
                doc.setHtml('<body>MNmn012<span class="p">012</span></body>')
                height = doc.size().height() + self.MARGIN_V * 2
                s = self._item_size = QSize(0, int(height))
            return s

        def setStyleSheet(self, s):
            self._doc.setDefaultStyleSheet(s)
            self._item_size = None

    def __init__(self, parent):
        super(HtmlListWidget, self).__init__(parent)
        QListWidget.setStyleSheet(self,
                "QListWidget{background-color: white;}")
        self._item_delegate = HtmlListWidget.HtmlItemDelegate(parent)
        self.setItemDelegate(self._item_delegate)

    def keyPressEvent(self, event):
        event.ignore()

    def setStyleSheet(self, s):
        self._item_delegate.setStyleSheet(s)


class SizeGrip(QSizeGrip):
    """QSizeGrip for QSplitter"""

    def __init__(self, parent):
        super(SizeGrip, self).__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        option = QStyleOptionSizeGrip()
        option.initFrom(self)
        option.corner = Qt.BottomRightCorner
        self.style().drawControl(QStyle.CE_SizeGrip, option, painter, self)


class ListWidget(QListWidget):
    """QListWidget with LeftArrow / RightArrow key handling"""

    # Item selection keys
    leftPressed = Signal()
    rightPressed = Signal()

    def __init__(self, parent):
        super(ListWidget, self).__init__(parent)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            self.leftPressed.emit()
        elif key == Qt.Key_Right:
            self.rightPressed.emit()
        else:
            super(ListWidget, self).keyPressEvent(event)

    def paintEvent(self, event):
        super(ListWidget, self).paintEvent(event)

        painter = QPainter(self.viewport())

        # Change the color of selected item
        for i in range(self.count()):
            if self.item(i).isSelected():
                itemRect = self.visualItemRect(self.item(i))
                painter.fillRect(itemRect, INDEX_SELECTED_COLOR)

        # custom stylesheet doesn't work properly with QListWidget::item
        # use paintEvent

    def leaveEvent(self, event):
        self.clearSelection()
        super(ListWidget, self).leaveEvent(event)


class CustomWebEnginePage(QWebEnginePage):
    """Custom WebEngine page that intercepts audio navigation requests"""
    
    def __init__(self, parent=None):
        super(CustomWebEnginePage, self).__init__(parent)
        self._main_window = None
    
    def set_main_window(self, main_window):
        """Set reference to main window for audio playback"""
        self._main_window = main_window
    
    def acceptNavigationRequest(self, url, nav_type, isMainFrame):
        """Intercept navigation requests to handle audio URLs"""
        scheme = url.scheme()
        
        print(f"DEBUG: Navigation request intercepted - URL: {url.toString()}, scheme: {scheme}, isMainFrame: {isMainFrame}")
        
        # Handle audio URLs by calling the main window's playback method
        if scheme == 'audio':
            print(f"DEBUG: Intercepting audio URL: {url.toString()}")
            if self._main_window:
                print(f"DEBUG: Calling main window _playbackAudio with path: {url.path()}")
                # Call the main window's _playbackAudio method
                self._main_window._playbackAudio(url.path())
            else:
                print(f"DEBUG: No main window reference available for audio playback")
            return False  # Don't navigate to the audio URL
        
        # Handle other custom schemes normally
        return super(CustomWebEnginePage, self).acceptNavigationRequest(url, nav_type, isMainFrame)


class WebView(QWebEngineView):
    wheelWithCtrl = Signal(int)

    def __init__(self, parent):
        super(WebView, self).__init__(parent)
        
        # Use custom page to intercept audio navigation
        custom_page = CustomWebEnginePage(self)
        self.setPage(custom_page)
        
        # Initialize main window reference
        self._main_window = None

        self.setStyleSheet("QWebEngineView{background-color: white;}")

        self._actionSearchText = QAction(self)
        if sys.platform != "darwin":
            self._actionSearchText.setIcon(
                    QIcon.fromTheme('edit-find',
                        QIcon(':/icons/edit-find.png')))
        self._actionCopyPlain = QAction(self)
        self._actionCopyPlain.setText('Copy')
        if sys.platform != "darwin":
            self._actionCopyPlain.setIcon(
                    QIcon.fromTheme('edit-copy',
                        QIcon(':/icons/edit-copy.png')))
        self._actionCopyPlain.triggered.connect(self._copyAsPlainText)
        self._actionCopyPlain.setShortcut(QKeySequence.Copy)
        self.page().selectionChanged.connect(self.__onSelectionChanged)
        self.__onSelectionChanged()
        self._actionDownloadAudio = QAction(u'Download mp3',  self)
    
    def set_main_window(self, main_window):
        """Set reference to main window for audio playback"""
        self._main_window = main_window
        # Also set it on the custom page
        if isinstance(self.page(), CustomWebEnginePage):
            self.page().set_main_window(main_window)

    def _copyAsPlainText(self):
        # WebEngine doesn't have selectedText() directly, use page().selectedText()
        def handle_text(text):
            QApplication.clipboard().setText(text.strip())
        self.page().runJavaScript("window.getSelection().toString()", handle_text)

    def selectedText(self):
        # Compatibility method for WebKit API
        # Note: This is async in WebEngine, so we return empty string
        # The actual copy functionality is handled by _copyAsPlainText
        return ""

    @property
    def actionSearchText(self):
        return self._actionSearchText

    @property
    def actionCopyPlain(self):
        return self._actionCopyPlain

    @property
    def actionDownloadAudio(self):
        return self._actionDownloadAudio

    @property
    def audioUrlToDownload(self):
        return getattr(self, '_audioUrlToDownload', QUrl())

    def __onSelectionChanged(self):
        # WebEngine doesn't provide easy access to selection state
        # We'll always enable the copy action
        self._actionCopyPlain.setEnabled(True)

    def contextMenuEvent(self, event):
        # WebEngine handles context menus differently
        # We'll create a basic context menu
        menu = QMenu(self)
        
        # Add copy action
        menu.addAction(self.actionCopyPlain)
        
        # Add search action if there's selected text
        # Note: We can't easily check for selected text in WebEngine
        # so we'll always show the search option
        menu.addAction(self.actionSearchText)
        
        # Add separator
        menu.addSeparator()
        
        # Add download audio action (simplified)
        menu.addAction(self.actionDownloadAudio)
        
        # Display the context menu
        menu.exec_(event.globalPos())

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            pass
        else:
            super(WebView, self).keyPressEvent(event)

    #--------------
    # Mouse Events
    #--------------

    def mousePressEvent(self, event):
        if sys.platform not in ('win32', 'darwin'):
            if self.handleNavMouseButtons(event):
                return
        super(WebView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if sys.platform in ('win32', 'darwin'):
            if self.handleNavMouseButtons(event):
                return
        super(WebView, self).mouseReleaseEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
             self.wheelWithCtrl.emit(event.pixelDelta())
             return
        super(WebView, self).wheelEvent(event)

    def handleNavMouseButtons(self, event):
        if event.button() == Qt.XButton1:
            self.back()
            return True
        elif event.button() == Qt.XButton2:
            self.forward()
            return True
        return False

    # Compatibility methods for WebKit API
    def findText(self, text, options=None):
        # WebEngine uses different find API
        if options is None:
            options = QWebEnginePage.FindFlags()
        self.page().findText(text, options)

    def triggerPageAction(self, action):
        # Map WebKit actions to WebEngine actions
        if action == "Back":
            self.back()
        elif action == "Forward":
            self.forward()
        elif action == "Reload":
            self.reload()
        else:
            # Try to trigger the action on the page
            try:
                self.page().triggerAction(action)
            except:
                pass  # Ignore if action doesn't exist

