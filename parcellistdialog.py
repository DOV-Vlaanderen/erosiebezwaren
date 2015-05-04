# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_parcellistdialog import Ui_ParcelListDialog
from widgets import valuelabel

class ParcelListWidget(QWidget):
    def __init__(self, parent, parcelListDialog):
        self.parcelListDialog = parcelListDialog
        self.main = self.parcelListDialog.main
        QWidget.__init__(self, parent)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.horMaxSizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.parcelList = []

    def populate(self, layer, feature):
        self.layer = layer
        self.feature = feature
        for p in self.__getParcelIterator():
            self.addParcel(p)

    def __getParcelIterator(self):
        expr = '"producentnr" = \'%s\'' % self.feature.attribute('producentnr')
        return self.layer.getFeatures(QgsFeatureRequest(QgsExpression(expr)))

    def __getParcels(self):
        return [f for f in self.__getParcelIterator()]

    def goToParcel(self, parcel):
        self.parcelListDialog.parcelInfoWidget.setFeature(parcel)

    def zoomExtent(self):
        self.layer.removeSelection()
        self.layer.select([p.id() for p in self.parcelList])
        self.main.iface.mapCanvas().zoomToSelected(self.layer)
        self.layer.removeSelection()

    def addParcel(self, parcel):
        row = self.layout.rowCount()
        self.parcelList.append(parcel)
        self.main.selectionManager.select(parcel, mode=1)

        btn = QPushButton(str(parcel.attribute('perceelsnr_va2015')), self)
        btn.setSizePolicy(self.horMaxSizePolicy)
        QObject.connect(btn, SIGNAL('clicked(bool)'), lambda: self.goToParcel(parcel))
        self.layout.addWidget(btn, row, 0)

        lb1 = valuelabel.ValueLabel(self)
        lb1.setText(parcel.attribute('status'))
        self.layout.addWidget(lb1, row, 1)

        lb2 = valuelabel.DefaultColorValueLabel(self)
        lb2.setSizePolicy(self.horMaxSizePolicy)
        lb2.setText('2015')
        lb2.setText(parcel.attribute('kleur_2015'))
        self.layout.addWidget(lb2, row, 2)

        lb3 = valuelabel.ValueLabel(self)
        lb3.setText(parcel.attribute('perceelsnaam'))
        self.layout.addWidget(lb3, row, 3)

class ParcelListDialog(QDialog, Ui_ParcelListDialog):
    def __init__(self, parcelInfoWidget):
        self.parcelInfoWidget = parcelInfoWidget
        self.main = self.parcelInfoWidget.main
        QDialog.__init__(self, self.main.iface.mainWindow())
        self.setupUi(self)

        self.parcelListWidget = ParcelListWidget(self.scrollAreaContents, self)
        self.scrollAreaLayout.insertWidget(0, self.parcelListWidget)

        QObject.connect(self.btn_zoomExtent, SIGNAL('clicked(bool)'), self.parcelListWidget.zoomExtent)
        QObject.connect(self, SIGNAL('finished(int)'), self.__clearSelection)

    def populate(self, layer, feature):
        self.layer = layer
        self.feature = feature
        self.parcelListWidget.populate(self.layer, self.feature)

    def __clearSelection(self):
        self.main.selectionManager.clearWithMode(mode=1, toggleRendering=True)
