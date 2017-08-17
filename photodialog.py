#-*- coding: utf-8 -*-

#  DOV Erosiebezwaren, QGis plugin to assess field erosion on tablets
#  Copyright (C) 2015-2017  Roel Huybrechts
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os
import re
import shutil
import subprocess
import time

try:
    from PIL import Image
    import ExifTags
except ImportError:
    EXIFORIENTATION = None
else:
    EXIFORIENTATION = None
    for i in ExifTags.TAGS.keys():
        if ExifTags.TAGS[i] == 'Orientation':
            EXIFORIENTATION = i
            break

from lib import flickcharm

# Import local version of the 'platform' library included in Python. This version fixes issues with platform detection
# on Windows 8+. The issue is described and fixed in ticket https://bugs.python.org/issue19143. Once this fix is released
# in Python 2.7.11 and this version in included in QGis, the local version can be dropped in favor of the default library.
from lib import platform

from ui_photodialog import Ui_PhotoDialog

class PhotoApp(object):
    def __init__(self):
        try:
            self.version = platform.win32_ver()[0]
        except:
            self.version = '8'

        if self.version not in ('8', '10'):
            self.version = '8'

    def appPath(self):
        if self.version == '8':
            return " shell:AppsFolder\\Microsoft.MoCamera_cw5n1h2txyewy!Microsoft.Camera"
        elif self.version == '10':
            return " shell:AppsFolder\\Microsoft.WindowsCamera_8wekyb3d8bbwe!App"

    def fileFilter(self):
        if self.version == '8':
            return re.compile(r'^WIN_([0-9]{8}_[0-9]{6}).*\.JPG$')
        elif self.version == '10':
            return re.compile(r'^WIN_([0-9]{8}_[0-9]{2}_[0-9]{2}_[0-9]{2}).*\.jpg$')

    def timeFormat(self):
        if self.version == '8':
            return "%Y%m%d_%H%M%S"
        elif self.version == '10':
            return "%Y%m%d_%H_%M_%S"

class Photo(QLabel):
    def __init__(self, path):
        QLabel.__init__(self)
        self.path = path
        self.pixmap = QPixmap(self.path)

        self.setScaledContents(False)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.rotatePixmap()
        self.pixmap = self.pixmap.scaledToWidth(500)
        self.setMinimumSize(self.pixmap.size())
        self.setPixmap(self.pixmap)

    def rotatePixmap(self):
        if EXIFORIENTATION:
            exif = dict(Image.open(self.path)._getexif().items())
            rotation = 0
            if exif[EXIFORIENTATION] == 3:
                rotation = 180
            elif exif[EXIFORIENTATION] == 6:
                rotation = 270
            elif exif[EXIFORIENTATION] == 8:
                rotation = 90
            if rotation > 0:
                self.pixmap = self.pixmap.transformed(QTransform().rotate(-1*rotation))

class PhotoDialog(QDialog, Ui_PhotoDialog):
    saved = pyqtSignal()

    def __init__(self, iface, parcelId):
        QDialog.__init__(self, iface.mainWindow())
        self.flick = flickcharm.FlickCharm(self)
        self.app = PhotoApp()
        self.iface = iface

        self.cmd = os.path.join(os.environ['SYSTEMROOT'], 'explorer.exe')
        self.cmd += self.app.appPath()

        self.photoPath = os.path.join(os.environ['USERPROFILE'], 'Pictures', 'Camera Roll')
        self.savePath = os.path.join(os.path.dirname(QgsProject.instance().fileName()), 'fotos', parcelId)

        self.initTime = time.localtime()
        self.loadedPhotos = set()
        self.filterRegex = self.app.fileFilter()

        self.setupUi(self)
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)

        self.flick.activateOn(self.scrollArea)

        self.timer = QTimer()
        QObject.connect(self.timer, SIGNAL('timeout()'), self.loadPhotos)
        QObject.connect(self, SIGNAL('finished(int)'), self.timer, SLOT('stop()'))
        QObject.connect(self, SIGNAL('finished(int)'), self.closed)

    def closed(self, result):
        if result == self.Accepted:
            if not os.path.exists(self.savePath):
                os.makedirs(self.savePath)
            for photo in self.loadedPhotos:
                shutil.move(os.path.join(self.photoPath, photo), self.savePath)
            self.saved.emit()

    def show(self):
        QDialog.show(self)
        sp = subprocess.Popen(self.cmd)
        self.timer.start(1000)

    def filter(self, photoName):
        r = self.filterRegex.search(photoName)
        if not r:
            return False

        try:
            photoTime = time.strptime(r.group(1), self.app.timeFormat())
            return photoTime >= self.initTime
        except IndexError:
            return False

    def loadPhotos(self):
        for p in os.listdir(self.photoPath):
            if self.filter(p) and p not in self.loadedPhotos:
                try:
                    self.verticalPhotoLayout.addWidget(Photo(os.path.join(self.photoPath, p)))
                    self.loadedPhotos.add(p)
                except IOError:
                    continue

        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(len(self.loadedPhotos)>0)
        if len(self.loadedPhotos) == 0:
            self.label.setText("Voeg volgende foto's toe aan het dossier:")
        elif len(self.loadedPhotos) == 1:
            self.label.setText("Voeg volgende foto toe aan het dossier:")
        else:
            self.label.setText("Voeg volgende %i foto's toe aan het dossier:" % len(self.loadedPhotos))
