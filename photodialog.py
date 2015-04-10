# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os
import time

from PIL import Image
from lib import flickcharm

from ui_photodialog import Ui_PhotoDialog

class Photo(QLabel):
    def __init__(self, path):
        QLabel.__init__(self)
        self.path = path

        self.setScaledContents(False)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setMinimumSize(self.getScaledSize())
        self.setPixmap(QPixmap(self.path).scaled(self.getScaledSize()))

    def getSize(self):
        if 'size' not in self.__dict__:
            self.size = Image.open(self.path).size
        return self.size

    def getScaledSize(self):
        width, height = self.getSize()
        return QSize(500, height/(width/500.0))

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
            self.label.setText("Voeg volgende foto's' toe aan het dossier:")
        elif len(self.loadedPhotos) == 1:
            self.label.setText("Voeg volgende foto toe aan het dossier:")
        else:
            self.label.setText("Voeg volgende foto's toe aan het dossier:" % len(self.loadedPhotos))
