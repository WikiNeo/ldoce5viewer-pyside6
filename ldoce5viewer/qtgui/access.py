'''application-specific URI scheme handler for QtWebKit'''

from __future__ import absolute_import
from __future__ import print_function

import sys
import imp
import os.path
import traceback

from PySide6.QtCore import (
    Qt, Q_ARG, QMetaObject, QIODevice, QTimer, Signal, Slot, QBuffer
)
from PySide6.QtNetwork import (
    QNetworkAccessManager, QNetworkReply, QNetworkRequest
)
from PySide6.QtWebEngineCore import (
    QWebEngineUrlScheme, QWebEngineUrlSchemeHandler
)

from .. import __version__
from .. import __name__ as basepkgname
from ..ldoce5 import LDOCE5, NotFoundError, FilemapError, ArchiveError
from ..utils.text import enc_utf8

from .advanced import search_and_render
from .utils import fontfallback
from .config import get_config

STATIC_REL_PATH = 'static'


def _load_static_data(filename):
    """Load a static file from the 'static' directory"""

    is_frozen = (hasattr(sys, 'frozen')  # new py2exe
                 or imp.is_frozen('__main__'))  # tools/freeze

    if is_frozen:
        if sys.platform.startswith("darwin"):
            path = os.path.join(os.path.dirname(sys.executable),
                                "../Resources",
                                STATIC_REL_PATH, filename)
        else:
            path = os.path.join(os.path.dirname(sys.executable),
                                STATIC_REL_PATH, filename)
        with open(path, 'rb') as f:
            data = f.read()
    else:
        try:
            from pkgutil import get_data as _get
        except ImportError:
            from pkg_resources import resource_string as _get

        data = _get(basepkgname, os.path.join(STATIC_REL_PATH, filename))

    if filename.endswith('.css'):
        s = data.decode('utf-8')
        s = fontfallback.css_replace_fontfamily(s)
        data = s.encode('utf-8')
    elif filename.endswith('.html'):
        s = data.decode('utf-8')
        s = s.replace('{% current_version %}', __version__)
        data = s.encode('utf-8')

    return data


class MyNetworkAccessManager(QNetworkAccessManager):
    '''Customized NetworkAccessManager'''

    def __init__(self, parent, searcher_hp, searcher_de):
        QNetworkAccessManager.__init__(self, parent)
        self._searcher_hp = searcher_hp
        self._searcher_de = searcher_de

    def createRequest(self, operation, request, data):
        if (operation == self.GetOperation and
                request.url().scheme() in ('dict', 'static', 'search')):
            return MyNetworkReply(
                self, operation, request,
                self._searcher_hp, self._searcher_de)
        else:
            return super(MyNetworkAccessManager, self).createRequest(
                operation, request, data)


class MyNetworkReply(QNetworkReply):
    '''Customized NetworkReply

    It handles the 'dict' and 'static' schemes.
    '''

    def __init__(self, parent, operation, request,
                 searcher_hp, searcher_de):
        QNetworkReply.__init__(self, parent)

        url = request.url()
        self.setRequest(request)
        self.setUrl(url)
        self.setOperation(operation)
        self.open(QIODevice.ReadOnly)

        self._finished = False
        self._data = None
        self._offset = 0

        self._url = url
        self._searcher_hp = searcher_hp
        self._searcher_de = searcher_de
        QTimer.singleShot(0, self._load)  # don't disturb the UI thread

    def _load(self):
        url = self._url
        config = get_config()
        searcher_hp = self._searcher_hp
        searcher_de = self._searcher_de
        mime = None
        error = False

        if url.scheme() == 'static':
            try:
                self._data = _load_static_data(url.path().lstrip('/'))
            except EnvironmentError:
                self._data = '<h2>Static File Not Found</h2>'
                mime = 'text/html'
                error = True

        elif url.scheme() == 'dict':
            try:
                path = url.path().split('#', 1)[0]
                ldoce5 = LDOCE5(config.get('dataDir', ''), config.filemap_path)
                (self._data, mime) = ldoce5.get_content(path)
            except NotFoundError:
                self._data = '<h2>Content Not Found</h2>'
                mime = 'text/html'
                error = True
            except FilemapError:
                self._data = '<h2>File-Location Map Not Available</h2>'
                mime = 'text/html'
                error = True
            except ArchiveError:
                self._data = '<h2>Dictionary Data Not Available</h2>'
                mime = 'text/html'
                error = True

        elif url.scheme() == 'search':
            if searcher_hp and searcher_de:
                try:
                    self._data = enc_utf8(search_and_render(
                        url, searcher_hp, searcher_de))
                    mime = 'text/html'
                except:
                    s = u"<h2>Error</h2><div>{0}</div>".format(
                        '<br>'.join(traceback.format_exc().splitlines()))
                    self._data = enc_utf8(s)
                    mime = 'text/html'
                    error = True
            else:
                mime = 'text/html'
                self._data = ("""<p>The full-text search index """
                              """has not been created yet or broken.</p>""")
                error = True

        if mime:
            self.setHeader(QNetworkRequest.ContentTypeHeader, mime)
        self.setHeader(QNetworkRequest.ContentLengthHeader, len(self._data))
        self.setOpenMode(self.ReadOnly | self.Unbuffered)

        if error:
            nwerror = QNetworkReply.ContentNotFoundError
            error_msg = u'Content Not Found'
            self.setError(nwerror, error_msg)
            QMetaObject.invokeMethod(
                self, 'error', Qt.QueuedConnection,
                Q_ARG(QNetworkReply.NetworkError, nwerror))

        QMetaObject.invokeMethod(self, 'metaDataChanged', Qt.QueuedConnection)
        QMetaObject.invokeMethod(self, 'downloadProgress', Qt.QueuedConnection,
                                 Q_ARG('qint64', len(self._data)),
                                 Q_ARG('qint64', len(self._data)))
        QMetaObject.invokeMethod(self, 'readyRead', Qt.QueuedConnection)
        QMetaObject.invokeMethod(self, 'finished', Qt.QueuedConnection)

        self._finished = True

    def isFinished(self):
        return self._finished

    def isSequential(self):
        return True

    def abort(self):
        self.close()

    def size(self):
        return len(self._data)

    def bytesAvailable(self):
        return (super(MyNetworkReply, self).bytesAvailable()
                + len(self._data) - self._offset)

    def readData(self, maxSize):
        if self._data is None:
            return b''
        
        end = min(self._offset + maxSize, len(self._data))
        data = self._data[self._offset:end]
        self._offset = end
        return data


# WebEngine URL Scheme Handler
class WebEngineUrlSchemeHandler(QWebEngineUrlSchemeHandler):
    """WebEngine URL scheme handler for dict://, static://, and search:// schemes"""
    
    def __init__(self, parent, searcher_hp=None, searcher_de=None):
        super(WebEngineUrlSchemeHandler, self).__init__(parent)
        self._searcher_hp = searcher_hp
        self._searcher_de = searcher_de
        # Keep references to buffers to prevent them from being garbage collected
        self._active_buffers = {}
    
    def update_searchers(self, searcher_hp, searcher_de):
        """Update the searcher references"""
        self._searcher_hp = searcher_hp
        self._searcher_de = searcher_de
    
    def requestStarted(self, job):
        """Handle URL scheme requests"""
        url = job.requestUrl()
        scheme = url.scheme()
        
        print(f"DEBUG: URL scheme handler called - URL: {url.toString()}, scheme: {scheme}")
        
        try:
            if scheme == 'static':
                self._handle_static_request(job, url)
            elif scheme == 'dict':
                self._handle_dict_request(job, url)
            elif scheme == 'search':
                self._handle_search_request(job, url)
            else:
                self._handle_error(job, f"Unknown scheme: {scheme}")
        except Exception as e:
            print(f"DEBUG: Exception in URL scheme handler: {str(e)}")
            import traceback
            traceback.print_exc()
            self._handle_error(job, f"Error handling request: {str(e)}")
    
    def _handle_static_request(self, job, url):
        """Handle static:// requests"""
        try:
            path = url.path().lstrip('/')
            print(f"DEBUG: Loading static file: {path}")
            data = _load_static_data(path)
            
            # Determine MIME type
            mime_type = 'text/html'
            if path.endswith('.css'):
                mime_type = 'text/css'
            elif path.endswith('.js'):
                mime_type = 'application/javascript'
            elif path.endswith('.png'):
                mime_type = 'image/png'
            elif path.endswith('.jpg') or path.endswith('.jpeg'):
                mime_type = 'image/jpeg'
            elif path.endswith('.gif'):
                mime_type = 'image/gif'
            
            print(f"DEBUG: Static file loaded, size: {len(data)}, mime: {mime_type}")
            self._send_response(job, data, mime_type)
        except Exception as e:
            print(f"DEBUG: Static file error: {str(e)}")
            self._handle_error(job, f"Static file not found: {str(e)}")
    
    def _handle_dict_request(self, job, url):
        """Handle dict:// requests"""
        try:
            path = url.path().split('#', 1)[0]
            print(f"DEBUG: Loading dict content for path: {path}")
            config = get_config()
            ldoce5 = LDOCE5(config.get('dataDir', ''), config.filemap_path)
            data, mime_type = ldoce5.get_content(path)
            
            if not mime_type:
                mime_type = 'text/html'
            
            print(f"DEBUG: Dict content loaded, size: {len(data) if data else 0}, mime: {mime_type}")
            self._send_response(job, data, mime_type)
        except NotFoundError as e:
            print(f"DEBUG: Dict content not found: {str(e)}")
            self._handle_error(job, "Content Not Found")
        except FilemapError as e:
            print(f"DEBUG: Dict filemap error: {str(e)}")
            self._handle_error(job, "File-Location Map Not Available")
        except ArchiveError as e:
            print(f"DEBUG: Dict archive error: {str(e)}")
            self._handle_error(job, "Dictionary Data Not Available")
        except Exception as e:
            print(f"DEBUG: Dict general error: {str(e)}")
            import traceback
            traceback.print_exc()
            self._handle_error(job, f"Dictionary error: {str(e)}")
    
    def _handle_search_request(self, job, url):
        """Handle search:// requests"""
        try:
            if self._searcher_hp and self._searcher_de:
                data = enc_utf8(search_and_render(
                    url, self._searcher_hp, self._searcher_de))
                self._send_response(job, data, 'text/html')
            else:
                error_msg = "The full-text search index has not been created yet or broken."
                self._handle_error(job, error_msg)
        except Exception as e:
            self._handle_error(job, f"Search error: {str(e)}")
    
    def _send_response(self, job, data, mime_type):
        """Send successful response"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            elif data is None:
                data = b''
            
            # Create buffer and keep it alive
            buffer = QBuffer()
            buffer.setData(data)
            buffer.open(QIODevice.ReadOnly)
            
            # Store buffer reference to prevent garbage collection
            job_id = id(job)
            self._active_buffers[job_id] = buffer
            
            # Clean up buffer when job is done
            def cleanup_buffer():
                self._active_buffers.pop(job_id, None)
            
            # Connect to job's destroyed signal if available
            if hasattr(job, 'destroyed'):
                job.destroyed.connect(cleanup_buffer)
            
            print(f"DEBUG: Sending response, data size: {len(data)}, mime: {mime_type}")
            job.reply(mime_type.encode('utf-8'), buffer)
            
        except Exception as e:
            print(f"DEBUG: Error sending response: {str(e)}")
            import traceback
            traceback.print_exc()
            self._handle_error(job, f"Response error: {str(e)}")
    
    def _handle_error(self, job, error_message):
        """Send error response"""
        print(f"DEBUG: Sending error response: {error_message}")
        error_html = f"<html><body><h2>Error</h2><p>{error_message}</p></body></html>"
        self._send_response(job, error_html, 'text/html')


def register_url_schemes():
    """Register custom URL schemes for WebEngine"""
    schemes = ['dict', 'static', 'search']
    
    for scheme_name in schemes:
        scheme = QWebEngineUrlScheme(scheme_name.encode('utf-8'))
        scheme.setFlags(
            QWebEngineUrlScheme.LocalAccessAllowed |
            QWebEngineUrlScheme.LocalScheme |
            QWebEngineUrlScheme.ContentSecurityPolicyIgnored
        )
        QWebEngineUrlScheme.registerScheme(scheme)
