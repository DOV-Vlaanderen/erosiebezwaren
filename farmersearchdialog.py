# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import difflib
import re

from ui_farmersearchdialog import Ui_FarmerSearchDialog
from parcellistdialog import ParcelListDialog
from widgets import valuelabel

class FarmerResultWidget(QWidget):
    featuresAdded = pyqtSignal()

    def __init__(self, parent, farmerSearchDialog):
        self.farmerSearchDialog = farmerSearchDialog
        self.main = self.farmerSearchDialog.main
        QWidget.__init__(self, parent)

        self.horMaxSizePolicy = QSizePolicy()
        self.horMaxSizePolicy.setHorizontalPolicy(QSizePolicy.Maximum)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.resultSet = set()

    def addFromFeatureIterator(self, iterator):
        for feature in iterator:
            self.addResult(feature)
        self.featuresAdded.emit()

    def clear(self):
        self.resultSet.clear()
        while self.layout.count():
            self.layout.takeAt(0).widget().deleteLater()

    def showParcelList(self, naam, producentnr):
        if not self.main.parcelInfoWidget:
            return

        d = ParcelListDialog(self.main.parcelInfoWidget)
        d.setWindowTitle('Bezwarenlijst %s' % naam)
        d.populate(self.farmerSearchDialog.layer, producentnr)
        d.show()

    def addResult(self, feature):
        farmer = (feature.attribute('producentnr'),
                  feature.attribute('naam'),
                  feature.attribute('straat_met_nr'),
                  feature.attribute('postcode'),
                  feature.attribute('gemeente'))

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
        self.reNumber = re.compile(r'^[0-9]+$')
        self.layer = self.main.utils.getLayerByName('bezwarenkaart')
        QDialog.__init__(self, self.main.iface.mainWindow())
        self.setupUi(self)

        self.farmerResultWidget = FarmerResultWidget(self.scrollAreaContents, self)
        self.scrollAreaLayout.insertWidget(0, self.farmerResultWidget)

        QObject.connect(self.btn_search, SIGNAL('clicked(bool)'), self.search)
        QObject.connect(self.farmerResultWidget, SIGNAL('featuresAdded()'), lambda: self.btn_search.setEnabled(True))

    def search(self):
        self.btn_search.setEnabled(False)
        self.farmerResultWidget.clear()

        if not self.layer:
            self.layer = self.main.utils.getLayerByName('bezwarenkaart')
            if not self.layer:
                self.btn_search.setEnabled(True)
                return

        searchText = self.ldt_searchfield.text()
        if not searchText:
            self.btn_search.setEnabled(True)
            return

        if self.reNumber.match(searchText):
            expr = '"producentnr" = \'%s\'' % searchText
            self.farmerResultWidget.addFromFeatureIterator(self.layer.getFeatures(QgsFeatureRequest(QgsExpression(expr))))
        else:
            for f in self.layer.getFeatures(QgsFeatureRequest(QgsExpression('"naam" is not null'))):
                if ' ' in searchText:
                    nl = set([f.attribute('naam').lower().strip()])
                else:
                    nl = set(f.attribute('naam').lower().strip().split(' '))
                    nl = nl - set(['van', 'de', 'der', 'en', 'vande'])

                if searchText.startswith('"') and searchText.endswith('"'):
                    if searchText.strip('"') in nl:
                        self.farmerResultWidget.addResult(f)
                elif len(difflib.get_close_matches(searchText, nl, cutoff=0.75)) > 0:
                    self.farmerResultWidget.addResult(f)
            self.farmerResultWidget.featuresAdded.emit()
