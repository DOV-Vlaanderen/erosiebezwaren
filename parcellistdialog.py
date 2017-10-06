# -*- coding: utf-8 -*-
"""Module containing the ParcelListWidget and ParcelListDialog classes."""

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

from ui_parcellistdialog import Ui_ParcelListDialog

from qgsutils import SpatialiteIterator
from widgets import valuelabel


class ParcelListWidget(QtGui.QWidget):
    """Widget showing a list of parcels of a given farmer."""

    def __init__(self, parent, parcelListDialog):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to be used as parent widget.
        parcelListDialog : ParcelListDialog
            Instance of ParcelListDialog this widget belongs to.

        """
        self.parcelListDialog = parcelListDialog
        self.main = self.parcelListDialog.main
        self.layer = self.main.utils.getLayerByName(
            self.main.settings.getValue('layers/bezwaren'))
        QtGui.QWidget.__init__(self, parent)

        self.horMaxSizePolicy = QtGui.QSizePolicy()
        self.horMaxSizePolicy.setHorizontalPolicy(QtGui.QSizePolicy.Maximum)
        self.layout = QtGui.QGridLayout(self)
        self.setLayout(self.layout)

        self.parcelList = []

    def populate(self, producentnr_zo, onlyObjections=False):
        """Populate the list of parcels based on a database search.

        Parameters
        ----------
        producentnr_zo : str
            Producentnr_zo of the farmer who's parcels to add to the list.
        onlyObjections : boolean, optional, defaults to `False`
            When `True` only list the parcels that have an objection, when
            `False` list all the parcels of the farmer. Defaults to `False`.

        """
        parcelList = []
        stmt = "producentnr_zo = '%s'" % producentnr_zo
        if onlyObjections:
            stmt += " AND datum_bezwaar IS NOT NULL"
        s = SpatialiteIterator(self.layer)

        parcelList = s.queryExpression(stmt)
        for p in sorted(parcelList,
                        key=lambda x: int(x.attribute('perceelsnr_va_2017'))):
            p.layer = self.layer
            self._addParcel(p)

    def goToParcel(self, parcel):
        """Show the information of this parcel in the parcelInfoWidget.

        Parameters
        ----------
        parcel : QGisCore.QgsFeature
            Feature of the parcel to show the info of.

        """
        self.parcelListDialog.parcelInfoWidget.setLayer(parcel.layer)
        self.parcelListDialog.parcelInfoWidget.setFeature(parcel)
        self.parcelListDialog.parcelInfoWidget.parent.show()

    def zoomExtent(self):
        """Zoom the map canvas to the extent of the listed parcels."""
        if len(self.parcelList) < 1:
            return
        extent = QGisCore.QgsRectangle(
            self.parcelList[0].geometry().boundingBox())
        for p in self.parcelList[1:]:
            extent.combineExtentWith(p.geometry().boundingBox())
        self.main.iface.mapCanvas().setExtent(extent.buffer(10))
        self.main.iface.mapCanvas().refresh()

    def _addParcel(self, parcel):
        """Add the parcel to the list of parcels.

        Parameters
        ----------
        parcel : QGisCore.QgsFeature
            Feature of the parcel to add.
        """
        row = self.layout.rowCount()
        self.parcelList.append(parcel)
        self.main.selectionManagerPolygons.select(parcel, mode=1)

        btn = QtGui.QPushButton(str(parcel.attribute('perceelsnr_va_2017')),
                                self)
        btn.setSizePolicy(self.horMaxSizePolicy)
        QtCore.QObject.connect(btn, QtCore.SIGNAL('clicked(bool)'),
                               lambda: self.goToParcel(parcel))
        self.layout.addWidget(btn, row, 0)

        lb1 = QtGui.QLabel(self)
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


class ParcelListDialog(QtGui.QDialog, Ui_ParcelListDialog):
    """Dialog showing a list of parcels."""

    def __init__(self, parcelInfoWidget):
        """Initialisation.

        Parameters
        ----------
        parcelInfoWidget : parcelinfowidget.ParcelInfoWidget
            The main parcelInfoWidget instance.

        """
        self.parcelInfoWidget = parcelInfoWidget
        self.main = self.parcelInfoWidget.main
        self.main.selectionManagerPolygons.activate()
        QtGui.QDialog.__init__(self, self.main.iface.mainWindow())
        self.setupUi(self)

        QtCore.QObject.connect(self, QtCore.SIGNAL('finished(int)'),
                               self.__clearSelection)

    def populate(self, bezwaren, naam, producentnr_zo):
        """Show the parcels of this specific farmer.

        Populate the contents of this widget and child widgets.

        Parameters
        ----------
        bezwaren : boolean
            Whether to show only the objections or all the parcels. Show only
            the parcels with an objection when this is True, all parcels when
            False.
        naam : str
            Name of the farmer, only used in the label.
        producentnr_zo : str
            The 'producentnr_zo' of the farmer, used to find the parcels.

        """
        self.listWidget = ParcelListWidget(self.scrollAreaContents, self)
        if bezwaren:
            self.lbv_bezwaren_van.setText('Bezwaren van %s' % naam)
            self.setWindowTitle('Bezwarenlijst')
        else:
            self.lbv_bezwaren_van.setText('Percelen van %s' % naam)
            self.setWindowTitle('Percelenlijst')

        QtCore.QObject.connect(self.btn_zoomExtent,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.listWidget.zoomExtent)
        self.scrollAreaLayout.insertWidget(0, self.listWidget)
        self.listWidget.populate(producentnr_zo, bezwaren)

    def __clearSelection(self):
        if not self.parcelInfoWidget.feature:
            self.main.selectionManagerPolygons.clear()
