# -*- coding: utf-8 -*-
"""Module containing the PhotoApp, PhotoDialog and Photo classes."""

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

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
import qgis.core as QGisCore

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

# Import local version of the 'platform' library included in Python. This
# version fixes issues with platform detection on Windows 8+. The issue is
# described and fixed in ticket https://bugs.python.org/issue19143. Once this
# fix is released in Python 2.7.11 and this version in included in QGis, the
# local version can be dropped in favor of the default library.
from lib import platform

from ui_photodialog import Ui_PhotoDialog


class PhotoApp(object):
    """Class grouping parameters of the Camera application."""

    def __init__(self):
        """Initialise and determine the version of Windows we are running."""
        try:
            self.version = platform.win32_ver()[0]
        except:
            self.version = '8'

        if self.version not in ('8', '10'):
            self.version = '8'

    def appPath(self):
        """Return the name of the Camera application, depending on Win version.

        Returns
        -------
        str
            Name of the Windows Camera MetroUI application.

        """
        if self.version == '8':
            return " shell:AppsFolder\\Microsoft." + \
                "MoCamera_cw5n1h2txyewy!Microsoft.Camera"
        elif self.version == '10':
            return " shell:AppsFolder\\Microsoft." + \
                "WindowsCamera_8wekyb3d8bbwe!App"

    def fileFilter(self):
        """Return a filter to find the timestamp in the filenames of photos.

        Returns
        -------
        re.RegexObject
            Regular expression with the timestamp of the photo as the first
            group.

        """
        if self.version == '8':
            return re.compile(r'^WIN_([0-9]{8}_[0-9]{6}).*\.JPG$')
        elif self.version == '10':
            return re.compile(
                r'^WIN_([0-9]{8}_[0-9]{2}_[0-9]{2}_[0-9]{2}).*\.jpg$')

    def timeFormat(self):
        """Return the time format.

        This method returns the timeformat used by the timestamp return by the
        regular expression of fileFilter(). Use this format together with
        fileFilter() to parse the timestamp of the filename.

        Returns
        -------
        str
            Format of the timestamp in the time.strptime syntax.

        """
        if self.version == '8':
            return "%Y%m%d_%H%M%S"
        elif self.version == '10':
            return "%Y%m%d_%H_%M_%S"


class Photo(QtGui.QLabel):
    """Class representing a photo in the PhotoDialog."""

    def __init__(self, path):
        """Initialisation.

        Parameters
        ----------
        path : str
            Path of the photo on the filesystem.

        """
        QtGui.QLabel.__init__(self)
        self.path = path
        self.pixmap = QtGui.QPixmap(self.path)

        self.setScaledContents(False)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                             QtGui.QSizePolicy.Fixed))

        self.rotatePixmap()
        self.pixmap = self.pixmap.scaledToWidth(500)
        self.setMinimumSize(self.pixmap.size())
        self.setPixmap(self.pixmap)

    def rotatePixmap(self):
        """Rotate the pixmap of the photo depending on the EXIF orientation."""
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
                self.pixmap = self.pixmap.transformed(
                    QtGui.QTransform().rotate(-1*rotation))


class PhotoDialog(QtGui.QDialog, Ui_PhotoDialog):
    """Dialog showing the photos that have been taken.

    Present the user with a dialog with the photos that have been taken and an
    option to either save them to the file of the parcel or cancel.

    Signals
    -------
    saved : QtCore.pyqtSignal
        Emitted when the user closed the dialog by clicking 'Save'.

    """

    saved = QtCore.pyqtSignal()

    def __init__(self, iface, parcelId):
        """Initialisation.

        Photos are stored in the folder 'fotos' in the same directory as the
        current QGis project.

        Parameters
        ----------
        iface : QGisGui.QGisInterface
            Instance of the QGis interface.
        parcelId : str
            Unique identification for the parcel. Used as the name of the
            subfolder to store the photos into.

        """
        QtGui.QDialog.__init__(self, iface.mainWindow())
        self.flick = flickcharm.FlickCharm(self)
        self.app = PhotoApp()
        self.iface = iface

        self.cmd = os.path.join(os.environ['SYSTEMROOT'], 'explorer.exe')
        self.cmd += self.app.appPath()

        self.photoPath = os.path.join(os.environ['USERPROFILE'], 'Pictures',
                                      'Camera Roll')
        self.savePath = os.path.join(os.path.dirname(
            QGisCore.QgsProject.instance().fileName()), 'fotos', parcelId)

        self.initTime = time.localtime()
        self.loadedPhotos = set()
        self.filterRegex = self.app.fileFilter()

        self.setupUi(self)
        self.buttonBox.button(QtGui.QDialogButtonBox.Save).setEnabled(False)

        self.flick.activateOn(self.scrollArea)

        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL('timeout()'),
                               self.loadPhotos)
        QtCore.QObject.connect(self, QtCore.SIGNAL('finished(int)'),
                               self.timer, QtCore.SLOT('stop()'))
        QtCore.QObject.connect(self, QtCore.SIGNAL('finished(int)'),
                               self.closed)

    def closed(self, result):
        """Catch the closed signal of the dialog.

        If the dialog was 'Accepted', move the photos to the folder of this
        parcel and emit the saved signal. In the other case, do nothing
        (note the photos are not deleted in this case).

        Parameters
        ----------
        result : int
            Resultcode of the closing of the dialog. Can be either
            `self.Accepted` or `self.Rejected`.

        """
        if result == self.Accepted:
            if not os.path.exists(self.savePath):
                os.makedirs(self.savePath)
            for photo in self.loadedPhotos:
                shutil.move(os.path.join(self.photoPath, photo), self.savePath)
            self.saved.emit()

    def show(self):
        """Show the dialog and start the Windows Camera application."""
        QtGui.QDialog.show(self)
        subprocess.Popen(self.cmd)
        self.timer.start(1000)

    def filter(self, photoName):
        """Filter the photo based on its filename.

        Get the timestamp from the filename of the photo and reject photos
        taken before opening the Camera application.

        Parameters
        ----------
        photoName : str
            Filename of the photo.

        Returns
        -------
        boolean
            `True` if the photo is taken after the Camera application was
            started, `False` otherwise. On errors return `False`.

        """
        r = self.filterRegex.search(photoName)
        if not r:
            return False

        try:
            photoTime = time.strptime(r.group(1), self.app.timeFormat())
            return photoTime >= self.initTime
        except IndexError:
            return False

    def loadPhotos(self):
        """Load the photos from the photo directory.

        Uses filter() to only show the ones taken by the user after starting
        the Camera application.
        """
        for p in os.listdir(self.photoPath):
            if self.filter(p) and p not in self.loadedPhotos:
                try:
                    self.verticalPhotoLayout.addWidget(Photo(os.path.join(
                        self.photoPath, p)))
                    self.loadedPhotos.add(p)
                except IOError:
                    continue

        self.buttonBox.button(QtGui.QDialogButtonBox.Save).setEnabled(len(
            self.loadedPhotos) > 0)
        if len(self.loadedPhotos) == 0:
            self.label.setText("Voeg volgende foto's toe aan het dossier:")
        elif len(self.loadedPhotos) == 1:
            self.label.setText("Voeg volgende foto toe aan het dossier:")
        else:
            self.label.setText("Voeg volgende %i foto's toe aan het dossier:" %
                               len(self.loadedPhotos))
