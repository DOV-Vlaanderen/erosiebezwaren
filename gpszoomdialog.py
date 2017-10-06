# -*- coding: utf-8 -*-
"""Module containing the GpsZoomDialog and RoundingDoubleValidator classes."""

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

from ui_gpszoomdialog import Ui_GpsZoomDialog


class RoundingDoubleValidator(QtGui.QDoubleValidator):
    """Subclass of a QtGui.QDoubleValidator that rounds the value.

    Rounds the value to the given number of decimals and updates the value of
    the lineEdit to this value.
    """

    def __init__(self, lineEdit, bottom, top, decimals):
        """Initialisation.

        Parameters
        ----------
        lineEdit : QtGui.QLineEdit
            QLineEdit to validate and update the value for.
        bottom : int or float
            Lowest value that is allowed. Values lower than this value will be
            replaced by this value.
        top : int or float
            Highest value that is allowed. Values greater than this value will
            be replaced by this value.
        decimals : int
            Use this number of decimals to format the result value.

        """
        self.lineEdit = lineEdit
        QtGui.QDoubleValidator.__init__(self, bottom, top, decimals)

    def fixup(self, value):
        """Round the given value and update the lineEdit accordingly.

        value : str
            Current value of the lineEdit to process.

        """
        try:
            v = float(value)
            if v < self.bottom():
                value = str(self.bottom())
            if v > self.top():
                value = str(self.top())
        except ValueError:
            value = '0'

        self.lineEdit.setText(value)


class GpsZoomDialog(QtGui.QDialog, Ui_GpsZoomDialog):
    u"""Dialog to zoom the map to GPS coördinates entered by the user."""

    def __init__(self, main):
        u"""Initialisation.

        Set the stored point, and as a consequence the initial coördinates, to
        the center of the map canvas.

        Parameters
        ----------
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.

        """
        self.main = main
        QtGui.QDialog.__init__(self, self.main.iface.mainWindow())
        self.setupUi(self)

        self.main.selectionManagerPoints.activate()

        self.led_latDecDeg.setValidator(RoundingDoubleValidator(
            self.led_latDecDeg, -90.0, 90.0, 10))
        self.led_lonDecDeg.setValidator(RoundingDoubleValidator(
            self.led_lonDecDeg, -180.0, 180.0, 10))

        self.transform_31370_to_4326 = QGisCore.QgsCoordinateTransform(
            QGisCore.QgsCoordinateReferenceSystem(
                31370, QGisCore.QgsCoordinateReferenceSystem.EpsgCrsId),
            QGisCore.QgsCoordinateReferenceSystem(
                4326, QGisCore.QgsCoordinateReferenceSystem.EpsgCrsId))

        self.transform_4326_to_31370 = QGisCore.QgsCoordinateTransform(
            QGisCore.QgsCoordinateReferenceSystem(
                4326, QGisCore.QgsCoordinateReferenceSystem.EpsgCrsId),
            QGisCore.QgsCoordinateReferenceSystem(
                31370, QGisCore.QgsCoordinateReferenceSystem.EpsgCrsId))

        point = self.main.iface.mapCanvas().extent().center()
        self.point = self.transform_31370_to_4326.transform(point)

        self.connectChangedSignals()

        QtCore.QObject.connect(self.btn_zoom, QtCore.SIGNAL('clicked(bool)'),
                               self.zoomTo)
        QtCore.QObject.connect(self.btn_zoom, QtCore.SIGNAL('clicked(bool)'),
                               self.hide)

        self.populate()

    def connectChangedSignals(self):
        """Connect the changed signals of the entry widgets."""
        for w in (self.sb_latDeg, self.sb_latMin, self.sb_latSec,
                  self.sb_lonDeg, self.sb_lonMin, self.sb_lonSec):
            QtCore.QObject.connect(w, QtCore.SIGNAL(
                'valueChanged(QString)'), self.updatePoint_dms)

        for w in (self.led_latDecDeg, self.led_lonDecDeg):
            QtCore.QObject.connect(w, QtCore.SIGNAL(
                'textChanged(QString)'), self.updatePoint_deg)

    def disconnectChangedSignals(self):
        """Disconnect the changed signals of the entry widgets."""
        for w in (self.sb_latDeg, self.sb_latMin, self.sb_latSec,
                  self.sb_lonDeg, self.sb_lonMin, self.sb_lonSec):
            QtCore.QObject.disconnect(w, QtCore.SIGNAL(
                'valueChanged(QString)'), self.updatePoint_dms)

        for w in (self.led_latDecDeg, self.led_lonDecDeg):
            QtCore.QObject.disconnect(w, QtCore.SIGNAL(
                'textChanged(QString)'), self.updatePoint_deg)

    def populate(self, disable=None):
        u"""Populate the entry fields with the coördinates of the stored point.

        Parameters
        ----------
        disable : str, optional
            Can be None, 'dms' or 'deg'. Used to optionally disable updating of
            the degree, minutes, seconds or decimal degree entry fields.

        """
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
        self.main.selectionManagerPoints.clearWithMode(0,
                                                       toggleRendering=False)
        self.main.selectionManagerPoints.selectGeometry(
            QGisCore.QgsGeometry.fromPoint(p))

        self.connectChangedSignals()

    def updatePoint_dms(self):
        """Update the stored point based on the dms fields.

        Update the location of the stored point based on the values of the
        degrees, minutes and seconds fields and update the value of the
        decimal degrees fields accordingly.
        """
        lat = self.sb_latDeg.value() + (self.sb_latMin.value()/60.0) + (
            self.sb_latSec.value()/6000.0)
        lon = self.sb_lonDeg.value() + (self.sb_lonMin.value()/60.0) + (
            self.sb_lonSec.value()/6000.0)
        self.point.setY(lat)
        self.point.setX(lon)

        self.populate(disable='dms')

    def updatePoint_deg(self):
        """Update the stored point based on the deg fields.

        Update the location of the stored point based on the values of the
        decimal degrees fields and update the value of the degrees, minutes and
        seconds fields accordingly.
        """
        lat = float(self.led_latDecDeg.text())
        lon = float(self.led_lonDecDeg.text())
        self.point.setY(lat)
        self.point.setX(lon)

        self.populate(disable='deg')

    def zoomTo(self):
        """Zoom the map canvas to the stored point.

        Zoom the map to a scale of 1:5000 and pan to the location of the
        stored point.
        """
        p = self.transform_4326_to_31370.transform(self.point)

        self.main.iface.mapCanvas().zoomScale(5000)
        self.main.iface.mapCanvas().zoomByFactor(1, p)
