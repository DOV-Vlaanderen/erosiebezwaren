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

from ui_gpszoomdialog import Ui_GpsZoomDialog

class RoundingDoubleValidator(QDoubleValidator):
    def __init__(self, lineEdit, bottom, top, decimals):
        self.lineEdit = lineEdit
        QDoubleValidator.__init__(self, bottom, top, decimals)

    def fixup(self, value):
        try:
            v = float(value)
            if v < self.bottom():
                value = str(self.bottom())
            if v > self.top():
                value = str(self.top())
        except ValueError:
            value = '0'

        self.lineEdit.setText(value)

class GpsZoomDialog(QDialog, Ui_GpsZoomDialog):
    def __init__(self, main):
        self.main = main
        QDialog.__init__(self, self.main.iface.mainWindow())
        self.setupUi(self)

        self.main.selectionManagerPoints.activate()

        self.led_latDecDeg.setValidator(RoundingDoubleValidator(self.led_latDecDeg, -90.0, 90.0, 10))
        self.led_lonDecDeg.setValidator(RoundingDoubleValidator(self.led_lonDecDeg, -180.0, 180.0, 10))

        self.transform_31370_to_4326 = QgsCoordinateTransform(
            QgsCoordinateReferenceSystem(31370, QgsCoordinateReferenceSystem.EpsgCrsId),
            QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))

        self.transform_4326_to_31370 = QgsCoordinateTransform(
            QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId),
            QgsCoordinateReferenceSystem(31370, QgsCoordinateReferenceSystem.EpsgCrsId))

        point = self.main.iface.mapCanvas().extent().center()
        self.point = self.transform_31370_to_4326.transform(point)

        self.connectChangedSignals()

        QObject.connect(self.btn_zoom, SIGNAL('clicked(bool)'), self.zoomTo)
        QObject.connect(self.btn_zoom, SIGNAL('clicked(bool)'), self.hide)

        self.populate()

    def connectChangedSignals(self):
        for w in (self.sb_latDeg, self.sb_latMin, self.sb_latSec, self.sb_lonDeg, self.sb_lonMin, self.sb_lonSec):
            QObject.connect(w, SIGNAL('valueChanged(QString)'), self.updatePoint_dms)

        for w in (self.led_latDecDeg, self.led_lonDecDeg):
            QObject.connect(w, SIGNAL('textChanged(QString)'), self.updatePoint_deg)

    def disconnectChangedSignals(self):
        for w in (self.sb_latDeg, self.sb_latMin, self.sb_latSec, self.sb_lonDeg, self.sb_lonMin, self.sb_lonSec):
            QObject.disconnect(w, SIGNAL('valueChanged(QString)'), self.updatePoint_dms)

        for w in (self.led_latDecDeg, self.led_lonDecDeg):
            QObject.disconnect(w, SIGNAL('textChanged(QString)'), self.updatePoint_deg)

    def populate(self, disable=None):
        self.disconnectChangedSignals()

        latDeg = int(self.point.y())
        latMin = abs(self.point.y()-latDeg)*60.0
        latSec = abs(latMin-int(latMin))*60.0

        if not disable == 'dms':
            self.sb_latDeg.setValue(latDeg)
            self.sb_latMin.setValue(int(latMin))
            self.sb_latSec.setValue(latSec)
        if not disable == 'deg':
            self.led_latDecDeg.setText('%f' % self.point.y())

        lonDeg = int(self.point.x())
        lonMin = abs(self.point.x()-lonDeg)*60.0
        lonSec = abs(lonMin-int(lonMin))*60.0

        if not disable == 'dms':
            self.sb_lonDeg.setValue(lonDeg)
            self.sb_lonMin.setValue(int(lonMin))
            self.sb_lonSec.setValue(lonSec)
        if not disable == 'deg':
            self.led_lonDecDeg.setText('%f' % self.point.x())

        p = self.transform_4326_to_31370.transform(self.point)
        self.main.selectionManagerPoints.clearWithMode(0, toggleRendering=False)
        self.main.selectionManagerPoints.selectGeometry(QgsGeometry.fromPoint(p))

        self.connectChangedSignals()

    def updatePoint_dms(self):
        lat = self.sb_latDeg.value() + (self.sb_latMin.value()/60.0) + (self.sb_latSec.value()/6000.0)
        lon = self.sb_lonDeg.value() + (self.sb_lonMin.value()/60.0) + (self.sb_lonSec.value()/6000.0)
        self.point.setY(lat)
        self.point.setX(lon)

        self.populate(disable='dms')

    def updatePoint_deg(self):
        lat = float(self.led_latDecDeg.text())
        lon = float(self.led_lonDecDeg.text())
        self.point.setY(lat)
        self.point.setX(lon)

        self.populate(disable='deg')

    def zoomTo(self):
        p = self.transform_4326_to_31370.transform(self.point)

        self.main.iface.mapCanvas().zoomScale(5000)
        self.main.iface.mapCanvas().zoomByFactor(1, p)
