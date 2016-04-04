# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import difflib
import re

from ui_farmersearchdialog import Ui_FarmerSearchDialog
from parcellistdialog import ParcelListDialog
from widgets import valuelabel
from qgsutils import SpatialiteIterator

class FarmerResultWidget(QWidget):
    def __init__(self, parent, farmerSearchDialog):
        self.farmerSearchDialog = farmerSearchDialog
        self.main = self.farmerSearchDialog.main
        QWidget.__init__(self, parent)

        self.horMaxSizePolicy = QSizePolicy()
        self.horMaxSizePolicy.setHorizontalPolicy(QSizePolicy.Maximum)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel('<i>Zoek landbouwer op basis van naam of, indien u<br>enkel cijfers invoert, op producentnummer.</i>'), 0, 0)

        self.resultSet = set()

    def addFromQuery(self, result):
        for farmer in result:
            self.addResult(farmer)
        if len(self.resultSet) < 1:
            self.setNoResult()

    def clear(self):
        self.resultSet.clear()
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        QCoreApplication.processEvents()

    def setNoResult(self, clear=True):
        if clear:
            self.clear()
        self.layout.addWidget(QLabel('Geen resultaat'), 0, 0)

    def showParcelList(self, naam, producentnr_zo):
        def enableWidgets():
            for i in reversed(range(self.layout.count())):
                self.layout.itemAt(i).widget().setEnabled(True)

        if not self.main.parcelInfoWidget:
            return

        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setEnabled(False)

        QCoreApplication.processEvents()
        d = ParcelListDialog(self.main.parcelInfoWidget)
        QObject.connect(d, SIGNAL('finished(int)'), enableWidgets)
        d.populate(self.farmerSearchDialog.onlyObjections, naam, producentnr_zo)
        d.show()

    def addResult(self, farmer):
        if farmer not in self.resultSet:
            self.resultSet.add(farmer)
            row = self.layout.rowCount()

            btn = QPushButton(str(farmer[0]), self)
            QObject.connect(btn, SIGNAL('clicked(bool)'), lambda: self.showParcelList(farmer[1], farmer[0]))
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

class FarmerSearchDialog(QDialog, Ui_FarmerSearchDialog):
    def __init__(self, main):
        self.main = main
        self.reNumber = re.compile(r'^[0-9\.-]+$')
        self.reProducentnr = re.compile(r'^[^1-9]*([1-9]+.*)$')
        QDialog.__init__(self, self.main.iface.mainWindow())
        self.setupUi(self)

        self.withObjection = {'Met bezwaren': 1,
                              'Alle landbouwers': 0}
        self.onlyObjections = None

        self.farmerResultWidget = FarmerResultWidget(self.scrollAreaContents, self)
        self.scrollAreaLayout.insertWidget(0, self.farmerResultWidget)

        QObject.connect(self.btn_search, SIGNAL('clicked(bool)'), self.search)

    def _getRawProducentnr(self, string):
        return str(self.reProducentnr.match(string).group(1)).translate(None, '.-')

    def search(self):
        self.btn_search.setEnabled(False)
        self.farmerResultWidget.clear()
        QCoreApplication.processEvents()
        self.btn_search.repaint()

        searchText = self.ldt_searchfield.text()
        if not searchText:
            self.btn_search.setEnabled(True)
            self.farmerResultWidget.setNoResult()
            return

        self.layer = self.main.utils.getLayerByName(self.main.settings.getValue('layers/bezwaren'))
        if not self.layer:
            self.btn_search.setEnabled(True)
            self.farmerResultWidget.setNoResult()
            return

        self.onlyObjections = self.withObjection[self.cmb_searchType.currentText()]
        if self.reNumber.match(searchText):
            stmt = "SELECT producentnr_zo, naam, straat_met_nr, postcode, gemeente FROM fts_landbouwers WHERE bezwaren = %i AND producentnr_zo like '%%%s%%' LIMIT 500" % (
                self.onlyObjections, self._getRawProducentnr(searchText))
        else:
            stmt = "SELECT producentnr_zo, naam, straat_met_nr, postcode, gemeente FROM fts_landbouwers WHERE bezwaren = %i AND naam MATCH '%s' LIMIT 500" % (
                self.onlyObjections, searchText)

        s = SpatialiteIterator(self.layer)
        self.farmerResultWidget.addFromQuery(s.rawQuery(stmt))

        if len(self.farmerResultWidget.resultSet) < 1:
            self.farmerResultWidget.setNoResult()

        self.btn_search.setEnabled(True)
