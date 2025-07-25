#!/usr/bin/env python3

import subprocess
from setuptools import setup
from ldoce5viewer import __version__

def iter_static():
    import os, os.path

    for root, dirs, files in os.walk("ldoce5viewer/static"):
        for filename in files:
            yield os.path.relpath(os.path.join(root, filename), "ldoce5viewer")

    for root, dirs, files in os.walk("ldoce5viewer/qtgui/resources"):
        for filename in files:
            yield os.path.relpath(os.path.join(root, filename), "ldoce5viewer")

    for root, dirs, files in os.walk("ldoce5viewer/qtgui/ui"):
        for filename in files:
            yield os.path.relpath(os.path.join(root, filename), "ldoce5viewer")


extra_options = {}

# -------------- For Windows-------------------
try:
    import py2exe
except ImportError:
    print('py2exe NOT found')
    pass
else:
    print('USING py2exe')
    extra_options.update(dict(
        name='LDOCE5 Viewer',
        windows = [{
            'script': 'ldoce5viewer.py',
            'icon_resources': [(1, 'ldoce5viewer/resources/ldoce5viewer.ico')],
        }],
        options = {'py2exe': {
            'includes': ['sip'],
            'packages': ['lxml.etree', 'gzip', 'lxml._elementpath'],
            #'excludes': ['_ssl', 'ssl', 'bz2', 'sqlite3', 'select',
            #             'xml', 'unittest', 'email', 'distutils', 'xmlrpclib',
            #             'doctest', 'pdb', 'tarfile'],
            'compressed': True,
            'optimize': 2,
            'bundle_files': 3,
            'dist_dir': 'exedist',
            }},
        zipfile=None
        ))


# -------------- For Mac OS X----------------
try:
    import py2app
except ImportError:
    print('py2app NOT found')
    pass
else:
    print('USING py2app')
    qt_plugins_path = subprocess.check_output('qmake -query QT_INSTALL_PLUGINS', shell=True)
    qt_plugins_path = qt_plugins_path[0:len(qt_plugins_path)-1] # remove "\n"
    extra_options.update(dict(
        name='LDOCE5 Viewer',
        app=['ldoce5viewer.py'],
        options={'py2app': {
            'iconfile': './ldoce5viewer/qtgui/resources/ldoce5viewer.icns',
            'argv_emulation': False,
            'optimize': 0,
            'includes': ['sip', 'lxml._elementpath'],
            'packages': [],
            'excludes': [
                'email', 'sqlite3',
                'PyQt4.QtCLucene',
                'PyQt4.QtHtml',
                'PyQt4.QtHelp',
                'PyQt4.QtTest',
                'PyQt4.QtOpenGL',
                'PyQt4.QtScript',
                'PyQt4.QtScriptTools',
                'PyQt4.QtSql',
                'PyQt4.QtDeclarative',
                'PyQt4.QtMultimedia',
                'PyQt4.QtDesigner',
                'PyQt4.QtXml',
                'PyQt4.QtXmlPatterns',
            ],
            #'qt_plugins': [
            #    'imageformats/libqjpeg.dylib',
            #]
        }},
        data_files=[
            ('qt_plugins/imageformats', [qt_plugins_path]),
            ('', ['ldoce5viewer/static']),
        ],
    ))

# --------- Main----------------------
if 'name' not in extra_options:
    extra_options['name'] = 'ldoce5viewer'

setup(
    version = __version__,
    description = 'LDOCE5 Viewer',
    url = 'http://hakidame.net/ldoce5viewer/',
    license = 'GPLv3+',
    platforms='any',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Development Status :: 5 - Production/Stable'
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Education',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Education',
        ],
    author = 'Taku Fukada',
    author_email = 'naninunenor@gmail.com',
    package_dir = {'ldoce5viewer': 'ldoce5viewer'},
    packages = [
        'ldoce5viewer',
        'ldoce5viewer.qtgui',
        'ldoce5viewer.qtgui.ui',
        'ldoce5viewer.qtgui.resources',
        'ldoce5viewer.qtgui.utils',
        'ldoce5viewer.qtgui.utils.mp3play',
        'ldoce5viewer.utils',
        'ldoce5viewer.ldoce5',
        ],
    package_data = {'ldoce5viewer': list(iter_static())},
    scripts = ['scripts/ldoce5viewer'],
    **extra_options
)

