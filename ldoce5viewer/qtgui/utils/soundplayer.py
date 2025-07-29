import sys
import os
import abc
from tempfile import NamedTemporaryFile, mkdtemp
import logging
import platform

from PySide6.QtCore import *
from ...utils.compat import range

_logger = logging.getLogger(__name__)

# Gstreamer 1.0
try:
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import GObject, Gst
    GObject.threads_init()
    Gst.init(None)
except (ImportError, ValueError):
    Gst = None
    GObject = None

# Gstreamer 0.10
try:
    if Gst is not None:
        raise ImportError()
    import gst
    import gobject
    gobject.threads_init()
except ImportError:
    gst = None
    gobject = None

# Cocoa via PyObjC
try:
    import AppKit
except:
    AppKit = None


# WinMCI
if sys.platform == 'win32':
    try:
        import mp3play
    except:
        mp3play = None
else:
    mp3play = None


# Qt-Phonon (Note: Phonon is not available in PySide6)
try:
    from PySide6.phonon import Phonon
except ImportError:
    Phonon = None


# Qt-Multimedia
try:
    import PySide6.QtMultimedia as QtMultimedia
except ImportError:
    QtMultimedia = None


class Backend(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self, parent, temp_dir):
        pass
    @abc.abstractmethod
    def play(self, data):
        pass
    @abc.abstractmethod
    def close(self):
        pass


class NullBackend(Backend):
    def __init__(self, parent, temp_dir):
        pass
    def play(self, data):
        pass
    def close(self):
        pass


class GstreamerBackend(Backend):
    """Backend for Gstreamer 1.0"""

    def __init__(self, parent, temp_dir):
        self._player = None
        self._data = None

    def play(self, data):
        if self._player:
            self._player.set_state(Gst.State.NULL)

        try:
            self._player = Gst.parse_launch(
                    'appsrc name=src ! decodebin ! autoaudiosink')
        except:
            _logger.error(
                "Gstreamer's good-plugins package is needed to play sound")
            return

        self._player.set_state(Gst.State.NULL)
        bus = self._player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._on_message)

        def need_data(appsrc, size):
            if not self._data:
                appsrc.emit('end-of-stream')
                return
            appsrc.emit('push-buffer', Gst.Buffer.new_wrapped(self._data[:size]))
            self._data = self._data[size:]

        self._data = data
        self._player.get_by_name('src').connect('need-data', need_data)
        self._player.set_state(Gst.State.PLAYING)

    def _on_message(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            self._player.set_state(Gst.State.NULL)
            self._player = None

    def close(self):
        if self._player:
            self._player.set_state(Gst.State.NULL)
        self._player = None


class GstreamerOldBackend(Backend):
    """Backend for Gstreamer 0.10"""

    def __init__(self, parent, temp_dir):
        self._player = None
        self._data = None

    def play(self, data):
        if self._player:
            self._player.set_state(gst.STATE_NULL)

        try:
            self._player = gst.parse_launch(
                    'appsrc name=src ! decodebin2 ! autoaudiosink')
        except:
            _logger.error(
                "Gstreamer's good-plugins package is needed to play sound")
            return

        self._player.set_state(gst.STATE_NULL)
        bus = self._player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._on_message)

        def need_data(appsrc, size):
            if not self._data:
                appsrc.emit('end-of-stream')
                return
            appsrc.emit('push-buffer', gst.Buffer(self._data[:size]))
            self._data = self._data[size:]

        self._data = data
        self._player.get_by_name('src').connect('need-data', need_data)
        self._player.set_state(gst.STATE_PLAYING)

    def _on_message(self, bus, message):
        if message.type == gst.MESSAGE_EOS:
            self._player.set_state(gst.STATE_NULL)
            self._player = None

    def close(self):
        if self._player:
            self._player.set_state(gst.STATE_NULL)
        self._player = None


class WinMCIBackend(Backend):
    def __init__(self, parent, temp_dir):
        self._mp3 = None
        self._NUM_TRY = 30
        self._temp_dir = temp_dir

    def _get_f(self):
        for i in range(self._NUM_TRY):
            path = os.path.join(self._temp_dir,
                    "sound.tmp{0}.mp3".format(i))
            try:
                os.unlink(path)
            except:
                pass
            try:
                f = open(path, "wb")
            except IOError:
                continue
            else:
                return f
        return None

    def play(self, data):
        if self._mp3:
            self._mp3.stop()
            self._mp3.close()
            self._mp3 = None
        f = self._get_f()
        if f is None:
            return
        f.write(data)
        path = f.name
        f.close()
        self._mp3 = mp3play.load(path)
        self._mp3.play()

    def close(self):
        for i in range(self._NUM_TRY):
            path = os.path.join(self._temp_dir,
                    "sound.tmp{0}.mp3".format(i))
            try:
                os.unlink(path)
            except:
                pass


class PhononBackend(Backend):
    def __init__(self, parent, temp_dir):
        self._player = Phonon.createPlayer(Phonon.NoCategory)
        self._player.finished.connect(self._onFinished)
        self._alive = set()

    def _onFinished(self):
        self._clean_tmp()

    def _play(self):
        source = Phonon.MediaSource(self._path)
        self._player.setCurrentSource(source)
        self._player.play()

    def play(self, data):
        self._player.stop()
        self._clean_tmp()
        with NamedTemporaryFile(mode='w+b', prefix='',
                suffix='.tmp.mp3', delete=False) as f:
            f.write(data)
            self._path = f.name
            self._alive.add(f.name)
        QTimer.singleShot(0, self._play)

    def _clean_tmp(self):
        removed = []
        for path in self._alive:
            try:
                os.unlnk(path)
            except:
                pass
            else:
                removed.append(path)
        self._alive.difference_update(removed)

    def close(self):
        self._player.stop()
        self._clean_tmp()


class QtMultimediaBackend(Backend):
    def __init__(self, parent, temp_dir):
        self._player = QtMultimedia.QMediaPlayer()
        self._tmpdir = mkdtemp()
        
        # PySide6: Set up audio output
        try:
            self._audio_output = QtMultimedia.QAudioOutput()
            # Set volume to ensure sound is audible
            self._audio_output.setVolume(0.8)  # 80% volume
            self._player.setAudioOutput(self._audio_output)
            _logger.debug("QtMultimedia audio output configured with volume 0.8")
        except Exception as e:
            _logger.error("QtMultimedia audio output setup failed: %s", str(e))
        
        # Connect to error signals for debugging
        self._player.errorOccurred.connect(self._on_error)
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)
        
        _logger.debug("QtMultimediaBackend initialized")

    def _on_error(self, error):
        _logger.error("QtMultimedia error: %s", error)

    def _on_media_status_changed(self, status):
        _logger.debug("QtMultimedia media status: %s", status)

    def _play(self):
        url = QUrl.fromLocalFile(self._path)
        _logger.debug("QtMultimedia playing file: %s", self._path)
        # PySide6: Use setSource() directly instead of QMediaContent
        self._player.setSource(url)
        _logger.debug("QtMultimedia setSource() called with: %s", url.toString())
        self._player.play()
        _logger.debug("QtMultimedia play() called")

    def play(self, data):
        _logger.debug("QtMultimediaBackend.play() called with %d bytes", len(data))
        self._player.stop()
        with NamedTemporaryFile(mode='w+b', prefix='',
                suffix='.tmp.mp3', dir=self._tmpdir, delete=False) as f:
            f.write(data)
            self._path = f.name
        _logger.debug("QtMultimedia temp file created: %s", self._path)
        QTimer.singleShot(0, self._play)

    def close(self):
        _logger.debug("QtMultimediaBackend.close() called")
        self._player.stop()
        # Properly clean up the audio output
        if hasattr(self, '_audio_output'):
            self._audio_output = None
        # Clean up temporary directory
        if hasattr(self, '_tmpdir'):
            import shutil
            try:
                shutil.rmtree(self._tmpdir)
                _logger.debug("QtMultimedia temp directory cleaned up")
            except:
                pass


class AppKitBackend(Backend):
    def __init__(self, parent, temp_dir):
        self._sound = None
        _logger.debug("AppKitBackend initialized")

    def stop(self):
        if self._sound:
            self._sound.stop()

    def play(self, data):
        _logger.debug("AppKitBackend.play() called with %d bytes", len(data))
        if self._sound:
            self._sound.stop()

        try:
            self._sound = AppKit.NSSound.alloc().initWithData_(data)
            if self._sound:
                _logger.debug("AppKit NSSound created successfully")
                result = self._sound.play()
                _logger.debug("AppKit play() result: %s", result)
            else:
                _logger.warning("AppKit NSSound creation failed")
        except Exception as e:
            _logger.exception("AppKit backend error: %s", str(e))

    def close(self):
        _logger.debug("AppKitBackend.close() called")
        # Properly stop and release the NSSound object
        if self._sound:
            self._sound.stop()
            # Release the NSSound object to prevent hanging
            self._sound = None
        _logger.debug("AppKit NSSound properly released")


def create_soundplayer(parent, temp_dir):
    backends = []
    
    # On macOS (Darwin), prioritize AppKit backend over QtMultimedia
    # for better reliability with Python 3.13
    if platform.system() == "Darwin":
        if AppKit:
            backends.append(AppKitBackend)
            _logger.debug("AppKit backend available (prioritized on macOS)")
        if QtMultimedia:
            backends.append(QtMultimediaBackend)
            _logger.debug("QtMultimedia backend available")
    else:
        # On other platforms, prioritize QtMultimedia
        if QtMultimedia:
            backends.append(QtMultimediaBackend)
            _logger.debug("QtMultimedia backend available")
        if AppKit:
            backends.append(AppKitBackend)
            _logger.debug("AppKit backend available")
    
    # Add other backends in order of preference
    if mp3play:
        backends.append(WinMCIBackend)
        _logger.debug("WinMCI backend available")
    if Phonon:
        backends.append(PhononBackend)
        _logger.debug("Phonon backend available")
    if Gst:
        backends.append(GstreamerBackend)
        _logger.debug("Gstreamer backend available")
    if gst:
        backends.append(GstreamerOldBackend)
        _logger.debug("GstreamerOld backend available")
    backends.append(NullBackend)

    selected_backend = backends[0]
    _logger.info("Selected audio backend: %s", selected_backend.__name__)
    return selected_backend(parent, temp_dir)



