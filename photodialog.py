# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os
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
    def __init__(self, iface, photoPath):
        QDialog.__init__(self, iface.mainWindow())
        self.flick = flickcharm.FlickCharm(self)
        self.iface = iface
        self.photoPath = photoPath
        self.initTime = time.localtime()
        self.loadedPhotos = set()

        self.setupUi(self)
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)

        self.flick.activateOn(self.scrollArea)

        self.timer = QTimer()
        QObject.connect(self.timer, SIGNAL('timeout()'), self.loadPhotos)
        QObject.connect(self, SIGNAL('finished(int)'), self.timer, SLOT('stop()'))
        QObject.connect(self, SIGNAL('finished(int)'), self.closed)

    def closed(self, result):
        if result == self.Accepted:
            print "PHOTOS SAVED"
        elif result == self.Rejected:
            print "PHOTOS NOT SAVED"

    def show(self):
        QDialog.show(self)
        self.timer.start(1000)

    def filter(self, photoName):
        photoTime = time.strptime(photoName, "WIN_%Y%m%d_%H%M%S.JPG")
        return photoTime >= self.initTime

    def loadPhotos(self):
        for p in os.listdir(self.photoPath):
            if p.endswith('.JPG') and self.filter(p) and p not in self.loadedPhotos:
                self.verticalPhotoLayout.addWidget(Photo(os.path.join(self.photoPath, p)))
                self.loadedPhotos.add(p)

        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(len(self.loadedPhotos)>0)
        if len(self.loadedPhotos) == 0:
            self.label.setText("Voeg volgende foto's toe aan het dossier:")
        elif len(self.loadedPhotos) == 1:
            self.label.setText("Voeg volgende foto toe aan het dossier:")
        else:
            self.label.setText("Voeg volgende %i foto's toe aan het dossier:" % len(self.loadedPhotos))
