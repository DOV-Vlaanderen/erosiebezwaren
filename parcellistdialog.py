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

        self.horMaxSizePolicy = QSizePolicy()
        self.horMaxSizePolicy.setHorizontalPolicy(QSizePolicy.Maximum)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.parcelList = []

    def populate(self, layer, producentnr):
        self.layer = layer
        for p in self.__getParcelIterator(producentnr):
            self.addParcel(p)

    def __getParcelIterator(self, producentnr):
        expr = '"producentnr" = \'%s\'' % producentnr
        return self.layer.getFeatures(QgsFeatureRequest(QgsExpression(expr)))

    def __getParcels(self):
        return [f for f in self.__getParcelIterator()]

    def goToParcel(self, parcel):
        self.parcelListDialog.parcelInfoWidget.setLayer(self.parcelListDialog.layer)
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

        btn = QPushButton(str(parcel.attribute('perceelsnr_va_2015')), self)
        btn.setSizePolicy(self.horMaxSizePolicy)
        QObject.connect(btn, SIGNAL('clicked(bool)'), lambda: self.goToParcel(parcel))
        self.layout.addWidget(btn, row, 0)

        lb1 = valuelabel.ValueLabel(self)
        lb1.setText(parcel.attribute('advies_behandeld'))
        self.layout.addWidget(lb1, row, 1)

        lb2 = valuelabel.DefaultColorValueLabel(self)
        lb2.setSizePolicy(self.horMaxSizePolicy)
        lb2.setText('2015')
        lb2.setText(parcel.attribute('kleur_2015'))
        self.layout.addWidget(lb2, row, 2)

class ParcelListDialog(QDialog, Ui_ParcelListDialog):
    def __init__(self, parcelInfoWidget):
        self.parcelInfoWidget = parcelInfoWidget
        self.main = self.parcelInfoWidget.main
        self.main.selectionManager.activate()
        QDialog.__init__(self, self.main.iface.mainWindow())
        self.setupUi(self)

        self.parcelListWidget = ParcelListWidget(self.scrollAreaContents, self)
        self.scrollAreaLayout.insertWidget(0, self.parcelListWidget)

        QObject.connect(self.btn_zoomExtent, SIGNAL('clicked(bool)'), self.parcelListWidget.zoomExtent)
        QObject.connect(self, SIGNAL('finished(int)'), self.__clearSelection)

    def populate(self, layer, producentnr):
        self.layer = layer
        self.parcelListWidget.populate(self.layer, producentnr)

    def __clearSelection(self):
        self.main.selectionManager.clearWithMode(mode=1, toggleRendering=True)
