# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_gpszoomdialog import Ui_GpsZoomDialog


class GpsZoomDialog(QDialog, Ui_GpsZoomDialog):
    def __init__(self, main):
        self.main = main
        QDialog.__init__(self, self.main.iface.mainWindow())
        self.setupUi(self)

        QObject.connect(self.btn_zoom, SIGNAL('clicked(bool)'), self.zoomTo)
        QObject.connect(self.btn_zoom, SIGNAL('clicked(bool)'), self.hide)

        # self.populate()

    def populate(self):
        center = self.main.iface.mapCanvas().extent().center()
        t = QgsCoordinateTransform(QgsCoordinateReferenceSystem(31370, QgsCoordinateReferenceSystem.EpsgCrsId),
            QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
        center = t.transform(center)

        latDeg = int(center.y())
        latMin = (abs(center.y())-abs(latDeg))/100.0*60.0*100.0
        latSec = (abs(latMin)-abs(int(latMin)))/100.0*60.0*100.0
        self.sb_latDeg.setValue(latDeg)
        self.sb_latMin.setValue(int(latMin))
        self.sb_latSec.setValue(latSec)

        lonDeg = int(center.x())
        lonMin = (abs(center.x())-abs(lonDeg))/100.0*60.0*100.0
        lonSec = (abs(lonMin)-abs(int(lonMin)))/100.0*60.0*100.0
        self.sb_lonDeg.setValue(lonDeg)
        self.sb_lonMin.setValue(int(lonMin))
        self.sb_lonSec.setValue(lonSec)

    def zoomTo(self):
        lat = self.sb_latDeg.value() + (self.sb_latMin.value()/60.0*100.0/100.0) + (self.sb_latSec.value()/60.0*100.0/10000.0)
        lon = self.sb_lonDeg.value() + (self.sb_lonMin.value()/60.0*100.0/100.0) + (self.sb_lonSec.value()/60.0*100.0/10000.0)
        t = QgsCoordinateTransform(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId),
            QgsCoordinateReferenceSystem(31370, QgsCoordinateReferenceSystem.EpsgCrsId))
        p = t.transform(lon, lat)

        self.main.iface.mapCanvas().zoomScale(5000)
        self.main.iface.mapCanvas().zoomByFactor(1, p)
