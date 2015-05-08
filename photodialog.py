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

from ui_photodialog import Ui_PhotoDialog

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
        self.iface = iface

        #cmd = "C:\\Windows\\explorer.exe shell:AppsFolder\\Panasonic.CameraPlus_ehmb8xpdwb7p4!App"
        self.cmd = os.path.join(os.environ['SYSTEMROOT'], 'explorer.exe')
        self.cmd += " shell:AppsFolder\\Microsoft.MoCamera_cw5n1h2txyewy!Microsoft.Camera"
        self.photoPath = os.path.join(os.environ['USERPROFILE'], 'Pictures', 'Camera Roll')
        self.savePath = os.path.join(os.path.dirname(QgsProject.instance().fileName()), 'fotos', parcelId)

        self.initTime = time.localtime()
        self.loadedPhotos = set()
        self.filterRegex = re.compile(r'^WIN_([0-9]{8}_[0-9]{6}).*\.JPG$')

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
            photoTime = time.strptime(r.group(1), "%Y%m%d_%H%M%S")
            return photoTime >= self.initTime
        except IndexError:
            return False

    def loadPhotos(self):
        for p in os.listdir(self.photoPath):
            if self.filter(p) and p not in self.loadedPhotos:
                self.verticalPhotoLayout.addWidget(Photo(os.path.join(self.photoPath, p)))
                self.loadedPhotos.add(p)

        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(len(self.loadedPhotos)>0)
        if len(self.loadedPhotos) == 0:
            self.label.setText("Voeg volgende foto's toe aan het dossier:")
        elif len(self.loadedPhotos) == 1:
            self.label.setText("Voeg volgende foto toe aan het dossier:")
        else:
            self.label.setText("Voeg volgende %i foto's toe aan het dossier:" % len(self.loadedPhotos))
