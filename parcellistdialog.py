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

from ui_parcellistdialog import Ui_ParcelListDialog
from widgets import valuelabel
from qgsutils import SpatialiteIterator

class ParcelListWidget(QWidget):
    def __init__(self, parent, parcelListDialog):
        self.parcelListDialog = parcelListDialog
        self.main = self.parcelListDialog.main
        self.layer = self.main.utils.getLayerByName(self.main.settings.getValue('layers/bezwaren'))
        QWidget.__init__(self, parent)

        self.horMaxSizePolicy = QSizePolicy()
        self.horMaxSizePolicy.setHorizontalPolicy(QSizePolicy.Maximum)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.parcelList = []

    def populate(self, producentnr_zo, onlyObjections=False):
        parcelList = []
        stmt = "producentnr_zo = '%s'" % producentnr_zo
        if onlyObjections:
            stmt +=  " AND datum_bezwaar IS NOT NULL"
        s = SpatialiteIterator(self.layer)

        parcelList = s.queryExpression(stmt)
        for p in sorted(parcelList, key = lambda x: int(x.attribute('perceelsnr_va_2017'))):
            p.layer = self.layer
            self.addParcel(p)

    def goToParcel(self, parcel):
        self.parcelListDialog.parcelInfoWidget.setLayer(parcel.layer)
        self.parcelListDialog.parcelInfoWidget.setFeature(parcel)
        self.parcelListDialog.parcelInfoWidget.parent.show()

    def zoomExtent(self):
        if len(self.parcelList) < 1:
            return
        extent = QgsRectangle(self.parcelList[0].geometry().boundingBox())
        for p in self.parcelList[1:]:
            extent.combineExtentWith(p.geometry().boundingBox())
        self.main.iface.mapCanvas().setExtent(extent.buffer(10))
        self.main.iface.mapCanvas().refresh()

    def addParcel(self, parcel):
        row = self.layout.rowCount()
        self.parcelList.append(parcel)
        self.main.selectionManagerPolygons.select(parcel, mode=1)

        btn = QPushButton(str(parcel.attribute('perceelsnr_va_2017')), self)
        btn.setSizePolicy(self.horMaxSizePolicy)
        QObject.connect(btn, SIGNAL('clicked(bool)'), lambda: self.goToParcel(parcel))
        self.layout.addWidget(btn, row, 0)

        lb1 = QLabel(self)
        if parcel.attribute('advies_behandeld'):
            lb1.setText(parcel.attribute('advies_behandeld'))
        else:
            lb1.setText('Geen bezwaar')
        self.layout.addWidget(lb1, row, 1)

        lb2 = valuelabel.SensitivityColorLabel(self)
        lb2.setSizePolicy(self.horMaxSizePolicy)
        lb2.setText('2017')
        lb2.setText(parcel.attribute('kleur_2017'))
        self.layout.addWidget(lb2, row, 2)

class ParcelListDialog(QDialog, Ui_ParcelListDialog):
    def __init__(self, parcelInfoWidget):
        self.parcelInfoWidget = parcelInfoWidget
        self.main = self.parcelInfoWidget.main
        self.main.selectionManagerPolygons.activate()
        QDialog.__init__(self, self.main.iface.mainWindow())
        self.setupUi(self)

        QObject.connect(self, SIGNAL('finished(int)'), self.__clearSelection)

    def populate(self, bezwaren, naam, producentnr_zo):
        self.listWidget = ParcelListWidget(self.scrollAreaContents, self)
        if bezwaren:
            self.lbv_bezwaren_van.setText('Bezwaren van %s' % naam)
            self.setWindowTitle('Bezwarenlijst')
        else:
            self.lbv_bezwaren_van.setText('Percelen van %s' % naam)
            self.setWindowTitle('Percelenlijst')

        QObject.connect(self.btn_zoomExtent, SIGNAL('clicked(bool)'), self.listWidget.zoomExtent)
        self.scrollAreaLayout.insertWidget(0, self.listWidget)
        self.listWidget.populate(producentnr_zo, bezwaren)

    def __clearSelection(self):
        if not self.parcelInfoWidget.feature:
            self.main.selectionManagerPolygons.clear()
