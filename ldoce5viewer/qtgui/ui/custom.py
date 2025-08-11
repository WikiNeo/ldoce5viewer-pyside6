import logging
import sys

from PySide6.QtCore import QSize, Qt, QUrl, Signal
from PySide6.QtGui import QAction, QColor, QIcon, QKeySequence, QPainter, QTextDocument
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QListWidget,
    QMenu,
    QSizeGrip,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionToolButton,
    QStylePainter,
    QToolButton,
)

# Logger
logger = logging.getLogger(__name__)

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
            QStyle.CT_ToolButton, opt, content_size, self
        )


class LineEdit(QLineEdit):
    """QLineEdit with a clear button"""

    _ICONSIZE = 16
    escapePressed = Signal()
    shiftReturnPressed = Signal()

    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)
        ICONSIZE = self._ICONSIZE

        self._buttonFind = QToolButton(self)
        self._buttonFind.setCursor(Qt.ArrowCursor)
        self._buttonFind.setIconSize(QSize(ICONSIZE, ICONSIZE))
        self._buttonFind.setIcon(QIcon(":/icons/edit-find.png"))
        self._buttonFind.setStyleSheet(
            "QToolButton { border: none; margin: 0; padding: 0; }"
        )
        self._buttonFind.setFocusPolicy(Qt.NoFocus)
        self._buttonFind.clicked.connect(self.selectAll)

        self._buttonClear = QToolButton(self)
        self._buttonClear.hide()
        self._buttonClear.setToolTip("Clear")
        self._buttonClear.setCursor(Qt.ArrowCursor)
        self._buttonClear.setIconSize(QSize(ICONSIZE, ICONSIZE))
        self._buttonClear.setIcon(QIcon(":/icons/edit-clear.png"))
        self._buttonClear.setStyleSheet(
            "QToolButton { border: none; margin: 0; padding: 0; }"
        )
        self._buttonClear.setFocusPolicy(Qt.NoFocus)
        self._buttonClear.clicked.connect(self.clear)

        minsize = self.minimumSizeHint()
        framewidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        margin = self.textMargins()
        margin.setLeft(3 + ICONSIZE + 1)
        margin.setRight(1 + ICONSIZE + 3)
        self.setTextMargins(margin)

        height = max(minsize.height(), ICONSIZE + (framewidth + 2) * 2)
        self.setMinimumSize(
            max(minsize.width(), (ICONSIZE + framewidth + 2 + 2) * 2),
            int(height / 2.0 + 0.5) * 2,
        )

        self.textChanged.connect(self.__onTextChanged)

    def resizeEvent(self, event):
        ICONSIZE = self._ICONSIZE
        framewidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        rect = self.rect()
        self._buttonFind.move(framewidth + 3 - 1, (rect.height() - ICONSIZE) // 2 - 1)
        self._buttonClear.move(
            rect.width() - framewidth - 3 - ICONSIZE - 1,
            (rect.height() - ICONSIZE) // 2 - 1,
        )

    def __onTextChanged(self, text):
        self._buttonClear.setVisible(bool(text))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.escapePressed.emit()
        elif event.key() == Qt.Key_Return and event.modifiers() & Qt.ShiftModifier:
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
        elif event.key() == Qt.Key_Return and event.modifiers() == Qt.ShiftModifier:
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
        QListWidget.setStyleSheet(self, "QListWidget{background-color: white;}")
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
    """Custom WebEngine page that intercepts audio and lookup navigation requests"""

    def __init__(self, parent=None):
        super(CustomWebEnginePage, self).__init__(parent)
        self._main_window = None

    def set_main_window(self, main_window):
        """Set reference to main window for audio playback"""
        self._main_window = main_window

    def acceptNavigationRequest(self, url, nav_type, isMainFrame):
        """Intercept navigation requests to handle audio and lookup URLs"""
        scheme = url.scheme()

        logger.debug(
            "Navigation request intercepted - URL: %s, scheme: %s, isMainFrame: %s",
            url.toString(),
            scheme,
            isMainFrame,
        )

        # Handle audio URLs by calling the main window's playback method
        if scheme == "audio":
            logger.debug("Intercepting audio URL: %s", url.toString())
            if self._main_window:
                logger.debug(
                    "Calling main window _playbackAudio with path: %s", url.path()
                )
                # Call the main window's _playbackAudio method
                self._main_window._playbackAudio(url.path())
            else:
                logger.warning("No main window reference available for audio playback")
            return False  # Don't navigate to the audio URL

        # Handle lookup URLs by calling the main window's link click handler
        if scheme == "lookup":
            logger.debug("Intercepting lookup URL: %s", url.toString())
            if self._main_window:
                logger.debug(
                    "Calling main window _onWebViewLinkClicked with URL: %s",
                    url.toString(),
                )
                # Call the main window's _onWebViewLinkClicked method
                self._main_window._onWebViewLinkClicked(url)
            else:
                logger.warning("No main window reference available for lookup handling")
            return False  # Don't navigate to the lookup URL

        # Handle other custom schemes normally
        return super(CustomWebEnginePage, self).acceptNavigationRequest(
            url, nav_type, isMainFrame
        )


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
                QIcon.fromTheme("edit-find", QIcon(":/icons/edit-find.png"))
            )
        self._actionCopyPlain = QAction(self)
        self._actionCopyPlain.setText("Copy")
        if sys.platform != "darwin":
            self._actionCopyPlain.setIcon(
                QIcon.fromTheme("edit-copy", QIcon(":/icons/edit-copy.png"))
            )
        self._actionCopyPlain.triggered.connect(self._copyAsPlainText)
        self._actionCopyPlain.setShortcut(QKeySequence.Copy)
        self.page().selectionChanged.connect(self.__onSelectionChanged)
        self.__onSelectionChanged()
        self._actionDownloadAudio = QAction("Download mp3", self)

        # Add copy as markdown action
        self._actionCopyMarkdown = QAction(self)
        self._actionCopyMarkdown.setText("Copy as Markdown")
        if sys.platform != "darwin":
            self._actionCopyMarkdown.setIcon(
                QIcon.fromTheme("edit-copy", QIcon(":/icons/edit-copy.png"))
            )
        self._actionCopyMarkdown.triggered.connect(self._copyAsMarkdown)

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

    def _copyAsMarkdown(self):
        # Get the full page HTML and convert to markdown
        def handle_html(html):
            try:
                markdown_text = self._html_to_markdown(html)

                # Additional safety check - remove any remaining thesaurus content
                # This is a final failsafe in case something slipped through
                import re

                lines = markdown_text.split("\n")
                cleaned_lines = []
                for line in lines:
                    if not re.search(r"thesaurus", line, re.IGNORECASE):
                        cleaned_lines.append(line)
                markdown_text = "\n".join(cleaned_lines)

                # Clean up any extra whitespace from line removal
                markdown_text = re.sub(r"\n\s*\n\s*\n+", "\n\n", markdown_text)
                markdown_text = markdown_text.strip()

                QApplication.clipboard().setText(markdown_text)
                # Optionally show a status message
                if hasattr(self, "_main_window") and self._main_window:
                    # Could add a status bar message here if needed
                    pass
            except Exception as e:
                # Fallback to plain text if conversion fails
                self.page().runJavaScript(
                    "document.body.innerText",
                    lambda text: QApplication.clipboard().setText(
                        f"# Definition\n\n{text.strip()}"
                    ),
                )

        self.page().runJavaScript("document.documentElement.outerHTML", handle_html)

    def selectedText(self):
        # Compatibility method for WebKit API
        # Note: This is async in WebEngine, so we return empty string
        # The actual copy functionality is handled by _copyAsPlainText
        return ""

    def _html_to_markdown(self, html):
        """Convert HTML content to markdown format"""
        import re
        from html import unescape

        # Remove HTML comments and script/style tags
        html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
        html = re.sub(
            r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE
        )

        # Extract the main content (usually in body)
        body_match = re.search(
            r"<body[^>]*>(.*?)</body>", html, flags=re.DOTALL | re.IGNORECASE
        )
        if body_match:
            html = body_match.group(1)

        # Remove unwanted sections before processing
        # Remove entire Thesaurus section including headers and content
        html = re.sub(
            r"<h1[^>]*>\s*#?\s*Thesaurus\s*</h1>.*?(?=<h1|<h2|<div[^>]*class[^>]*entry|$)",
            "",
            html,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # Remove specific unwanted links and their containers
        html = re.sub(
            r'<a[^>]*href="[^"]*"[^>]*>Activator</a>', "", html, flags=re.IGNORECASE
        )
        html = re.sub(
            r'<a[^>]*href="[^"]*"[^>]*>Other Dicts?</a>', "", html, flags=re.IGNORECASE
        )
        html = re.sub(
            r'<a[^>]*href="[^"]*"[^>]*>Corpus</a>', "", html, flags=re.IGNORECASE
        )

        # Remove Example Bank text
        html = re.sub(r"<p[^>]*>\s*Example Bank\s*</p>", "", html, flags=re.IGNORECASE)

        # Remove list items containing these links or empty list items
        html = re.sub(
            r"<li[^>]*>.*?(Activator|Other Dicts?|Corpus).*?</li>",
            "",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )
        html = re.sub(
            r"<li[^>]*>\s*</li>", "", html, flags=re.IGNORECASE
        )  # Remove empty list items

        # Remove empty lists after removing items
        html = re.sub(r"<ul[^>]*>\s*</ul>", "", html, flags=re.IGNORECASE)
        html = re.sub(r"<ol[^>]*>\s*</ol>", "", html, flags=re.IGNORECASE)

        # Remove audio links but preserve the text content around them
        # Pattern: [](audio:///path/to/audio.mp3) -> remove completely
        html = re.sub(r"\[\]\(audio:///[^)]+\)", "", html)

        # Remove any remaining audio-related links
        html = re.sub(
            r'<a[^>]*href="audio://[^"]*"[^>]*>.*?</a>', "", html, flags=re.IGNORECASE
        )

        # Convert common HTML elements to markdown
        markdown = html

        # Headers
        markdown = re.sub(
            r"<h1[^>]*>(.*?)</h1>", r"# \1\n\n", markdown, flags=re.IGNORECASE
        )
        markdown = re.sub(
            r"<h2[^>]*>(.*?)</h2>", r"## \1\n\n", markdown, flags=re.IGNORECASE
        )
        markdown = re.sub(
            r"<h3[^>]*>(.*?)</h3>", r"### \1\n\n", markdown, flags=re.IGNORECASE
        )
        markdown = re.sub(
            r"<h4[^>]*>(.*?)</h4>", r"#### \1\n\n", markdown, flags=re.IGNORECASE
        )

        # Bold and italic
        markdown = re.sub(
            r"<(strong|b)[^>]*>(.*?)</\1>", r"**\2**", markdown, flags=re.IGNORECASE
        )
        markdown = re.sub(
            r"<(em|i)[^>]*>(.*?)</\1>", r"*\2*", markdown, flags=re.IGNORECASE
        )

        # Links (but skip audio links which should already be removed)
        markdown = re.sub(
            r'<a[^>]*href=["\'](?!audio:)([^"\'>]*)["\'][^>]*>(.*?)</a>',
            r"[\2](\1)",
            markdown,
            flags=re.IGNORECASE,
        )

        # Lists
        markdown = re.sub(r"<ul[^>]*>", "\n", markdown, flags=re.IGNORECASE)
        markdown = re.sub(r"</ul>", "\n", markdown, flags=re.IGNORECASE)
        markdown = re.sub(r"<ol[^>]*>", "\n", markdown, flags=re.IGNORECASE)
        markdown = re.sub(r"</ol>", "\n", markdown, flags=re.IGNORECASE)
        markdown = re.sub(
            r"<li[^>]*>(.*?)</li>", r"- \1\n", markdown, flags=re.IGNORECASE
        )

        # Paragraphs and line breaks
        markdown = re.sub(
            r"<p[^>]*>(.*?)</p>", r"\1\n\n", markdown, flags=re.IGNORECASE
        )
        markdown = re.sub(r"<br[^>]*/?>", "\n", markdown, flags=re.IGNORECASE)

        # Divs and spans - just remove tags but keep content
        markdown = re.sub(
            r"<div[^>]*>(.*?)</div>", r"\1\n", markdown, flags=re.IGNORECASE | re.DOTALL
        )
        markdown = re.sub(
            r"<span[^>]*>(.*?)</span>", r"\1", markdown, flags=re.IGNORECASE
        )

        # Remove any remaining HTML tags
        markdown = re.sub(r"<[^>]+>", "", markdown)

        # Decode HTML entities
        markdown = unescape(markdown)

        # Clean up specific unwanted text patterns that might remain
        markdown = re.sub(
            r"^-?\s*(Activator|Other Dicts?|Corpus|Example Bank)\s*$",
            "",
            markdown,
            flags=re.MULTILINE | re.IGNORECASE,
        )
        markdown = re.sub(
            r"^\s*-\s*(Activator|Other Dicts?|Corpus|Example Bank).*$",
            "",
            markdown,
            flags=re.MULTILINE | re.IGNORECASE,
        )

        # Remove Thesaurus headers that might have slipped through (all variations)
        markdown = re.sub(
            r"^#+\s*Thesaurus\s*$", "", markdown, flags=re.MULTILINE | re.IGNORECASE
        )
        markdown = re.sub(
            r"^#+\s*Thesaurus\s*\n", "", markdown, flags=re.MULTILINE | re.IGNORECASE
        )
        markdown = re.sub(
            r"^#+\s*Thesaurus.*$", "", markdown, flags=re.MULTILINE | re.IGNORECASE
        )

        # Remove empty list items (lines with just "-" or "- ")
        markdown = re.sub(r"^\s*-\s*$", "", markdown, flags=re.MULTILINE)

        # Remove lines with just whitespace or dashes
        markdown = re.sub(r"^\s*-+\s*$", "", markdown, flags=re.MULTILINE)

        # Clean up whitespace
        markdown = re.sub(
            r"\n\s*\n\s*\n+", "\n\n", markdown
        )  # Multiple newlines to double
        markdown = re.sub(
            r"^\s+", "", markdown, flags=re.MULTILINE
        )  # Leading whitespace
        markdown = re.sub(
            r"\s+$", "", markdown, flags=re.MULTILINE
        )  # Trailing whitespace
        markdown = markdown.strip()

        # Final aggressive cleanup of any remaining Thesaurus content
        # Remove any lines containing "Thesaurus" (case insensitive)
        lines = markdown.split("\n")
        cleaned_lines = []
        for line in lines:
            if not re.search(r"thesaurus", line, re.IGNORECASE):
                cleaned_lines.append(line)
        markdown = "\n".join(cleaned_lines)

        # Final whitespace cleanup after line removal
        markdown = re.sub(r"\n\s*\n\s*\n+", "\n\n", markdown)
        markdown = markdown.strip()

        # Add a header if content doesn't start with one AND it looks like it needs one
        if markdown and not markdown.startswith("#"):
            # Try to extract word from title or first meaningful text
            first_line = markdown.split("\n")[0].strip()
            # Only add a header if the first line looks like a word/title (not a definition)
            # Check if it contains common definition markers like parentheses, slashes, etc.
            if (
                first_line
                and len(first_line) < 50
                and not re.search(
                    r"[/()[\]]", first_line
                )  # No pronunciation or grammatical markers
                and not re.search(
                    r"\b(noun|verb|adjective|adverb|also|British|American)\b",
                    first_line,
                    re.IGNORECASE,
                )
            ):
                markdown = f"# {first_line}\n\n" + "\n".join(markdown.split("\n")[1:])
            # If the content looks like it starts with a definition, don't add any header

        return markdown

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
    def actionCopyMarkdown(self):
        return self._actionCopyMarkdown

    @property
    def audioUrlToDownload(self):
        return getattr(self, "_audioUrlToDownload", QUrl())

    def __onSelectionChanged(self):
        # WebEngine doesn't provide easy access to selection state
        # We'll always enable the copy action
        self._actionCopyPlain.setEnabled(True)

    def contextMenuEvent(self, event):
        # WebEngine handles context menus differently
        # We'll create a basic context menu
        menu = QMenu(self)

        # Add copy actions
        menu.addAction(self.actionCopyPlain)
        menu.addAction(self.actionCopyMarkdown)

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

    # --------------
    # Mouse Events
    # --------------

    def mousePressEvent(self, event):
        if sys.platform not in ("win32", "darwin"):
            if self.handleNavMouseButtons(event):
                return
        super(WebView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if sys.platform in ("win32", "darwin"):
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
        if event.button() == Qt.XButton2:
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
