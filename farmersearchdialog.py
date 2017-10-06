# -*- coding: utf-8 -*-
"""Module containing the FarmerSearchDialog and FarmerResultWidget classes."""

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

import re

from parcellistdialog import ParcelListDialog
from qgsutils import SpatialiteIterator
from widgets import valuelabel

from ui_farmersearchdialog import Ui_FarmerSearchDialog


class FarmerResultWidget(QtGui.QWidget):
    """A widget to display results of a search for a farmer."""

    def __init__(self, parent, farmerSearchDialog):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Parent widget this widget will reside in.
        farmerSearchDialog : FarmerSearchDialog
            Instance of FarmerSearchDialog this widget will be used in.

        """
        self.farmerSearchDialog = farmerSearchDialog
        self.main = self.farmerSearchDialog.main
        QtGui.QWidget.__init__(self, parent)

        self.horMaxSizePolicy = QtGui.QSizePolicy()
        self.horMaxSizePolicy.setHorizontalPolicy(QtGui.QSizePolicy.Maximum)
        self.layout = QtGui.QGridLayout(self)
        self.setLayout(self.layout)

        self.layout.addWidget(QtGui.QLabel(
            '<i>Zoek landbouwer op basis van naam of, indien u<br>enkel ' +
            'cijfers invoert, op producentnummer.</i>'), 0, 0)

        self.resultSet = set()

    def addFromQuery(self, result):
        """Add all the farmers from the result.

        Parameters
        ----------
        result : list of list
            Result of the search query executed via
            qgsutils.SpatialiteIterator.rawQuery

        """
        for farmer in result:
            self.addResult(farmer)
        if len(self.resultSet) < 1:
            self.setNoResult()

    def clear(self):
        """Clear all previously added results."""
        self.resultSet.clear()
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        QtCore.QCoreApplication.processEvents()

    def setNoResult(self, clear=True):
        """Display a message to inform the query had no results.

        Parameters
        ----------
        clear : boolean, optional
            Clear the previously added results before adding the message.
            Default is `True`.

        """
        if clear:
            self.clear()
        self.layout.addWidget(QtGui.QLabel('Geen resultaat'), 0, 0)

    def showParcelList(self, naam, producentnr_zo):
        """Open the parcellist showing the parcels of a specific farmer.

        This opens a parcellistdialog.ParcelListDialog showing either all
        parcels for which the farmer filed a complaint, or all parcels of the
        given farmer (depending whether the users searched for )

        Parameters
        ----------
        naam : str
            Name of the farmer, to be used in the title of the parcellist
            dialog.
        producentnr_zo : str
            producentnr_zo of the farmer, used to find the parcels of this
            specific farmer.

        """
        def enableWidgets():
            for i in reversed(range(self.layout.count())):
                self.layout.itemAt(i).widget().setEnabled(True)

        if not self.main.parcelInfoWidget:
            return

        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setEnabled(False)

        QtCore.QCoreApplication.processEvents()
        d = ParcelListDialog(self.main.parcelInfoWidget)
        QtCore.QObject.connect(d, QtCore.SIGNAL('finished(int)'),
                               enableWidgets)
        d.populate(self.farmerSearchDialog.onlyObjections, naam,
                   producentnr_zo)
        d.show()

    def addResult(self, farmer):
        """Add a farmer the the result.

        Adds a new row for the farmer, including a button to open the parcel
        list, their producentnr_zo, naam, postcode and gemeente.

        Parameters
        ----------
        farmer : list
            A list of details about the farmer, with producentnr_zo, naam,
            postcode and gemeente.

        """
        if farmer not in self.resultSet:
            self.resultSet.add(farmer)
            row = self.layout.rowCount()

            btn = QtGui.QPushButton(str(farmer[0]), self)
            QtCore.QObject.connect(
                btn, QtCore.SIGNAL('clicked(bool)'),
                lambda: self.showParcelList(farmer[1], farmer[0]))
            self.layout.addWidget(btn, row, 0)

            lb0 = valuelabel.ValueLabel(self)
            lb0.setText(farmer[1])
            self.layout.addWidget(lb0, row, 1)

            lb1 = valuelabel.ValueLabel(self)
            lb1.setText(farmer[2])
            self.layout.addWidget(lb1, row, 2)

            lb2 = valuelabel.ValueLabel(self)
            lb2.setText(farmer[3])
            lb2.setSizePolicy(self.horMaxSizePolicy)
            self.layout.addWidget(lb2, row, 3)

            lb3 = valuelabel.ValueLabel(self)
            lb3.setText(farmer[4])
            self.layout.addWidget(lb3, row, 4)


class FarmerSearchDialog(QtGui.QDialog, Ui_FarmerSearchDialog):
    """Class describing the dialog to search for a farmer."""

    def __init__(self, main):
        """Initialise the dialog, without showing it yet.

        Parameters
        ----------
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.

        """
        self.main = main
        self.reNumber = re.compile(r'^[0-9\.-]+$')
        self.reProducentnr = re.compile(r'^[^1-9]*([1-9]+.*)$')
        QtGui.QDialog.__init__(self, self.main.iface.mainWindow())
        self.setupUi(self)

        self.withObjection = {'Met bezwaren': 1,
                              'Alle landbouwers': 0}
        self.onlyObjections = None

        self.farmerResultWidget = FarmerResultWidget(self.scrollAreaContents,
                                                     self)
        self.scrollAreaLayout.insertWidget(0, self.farmerResultWidget)

        QtCore.QObject.connect(self.btn_search, QtCore.SIGNAL('clicked(bool)'),
                               self.search)

    def _getRawProducentnr(self, string):
        return str(self.reProducentnr.match(
            string).group(1)).translate(None, '.-')

    def search(self):
        """Search for a farmer.

        Get the search query from the textedit, perform search in the database
        and populate the result widget with the results.
        """
        self.btn_search.setEnabled(False)
        self.farmerResultWidget.clear()
        QtCore.QCoreApplication.processEvents()
        self.btn_search.repaint()

        searchText = self.ldt_searchfield.text()
        if not searchText:
            self.btn_search.setEnabled(True)
            self.farmerResultWidget.setNoResult()
            return

        self.layer = self.main.utils.getLayerByName(
            self.main.settings.getValue('layers/bezwaren'))
        if not self.layer:
            self.btn_search.setEnabled(True)
            self.farmerResultWidget.setNoResult()
            return

        self.onlyObjections = self.withObjection[
            self.cmb_searchType.currentText()]
        if self.reNumber.match(searchText):
            stmt = ("SELECT producentnr_zo, naam, straat_met_nr, postcode, " +
                    "gemeente FROM fts_landbouwers WHERE bezwaren = %i AND " +
                    "producentnr_zo like '%%%s%%' LIMIT 500") % (
                    self.onlyObjections, self._getRawProducentnr(searchText))
        else:
            stmt = ("SELECT producentnr_zo, naam, straat_met_nr, postcode, " +
                    "gemeente FROM fts_landbouwers WHERE bezwaren = %i AND " +
                    "naam MATCH '%s' LIMIT 500") % (self.onlyObjections,
                                                    searchText)

        s = SpatialiteIterator(self.layer)
        self.farmerResultWidget.addFromQuery(s.rawQuery(stmt))

        if len(self.farmerResultWidget.resultSet) < 1:
            self.farmerResultWidget.setNoResult()

        self.btn_search.setEnabled(True)
