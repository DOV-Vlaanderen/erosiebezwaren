# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_parcellistdialog import Ui_ParcelListDialog

class ParcelListWidget(QWidget):
    def __init__(self, parent, parcelListDialog, layer, feature):
        self.parcelListDialog = parcelListDialog
        self.main = self.parcelListDialog.main
        self.layer = layer
        self.feature = feature
        QWidget.__init__(self, parent)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.btnSizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.parcelList = []

        for p in self.__getParcelIterator():
            self.addParcel(p)

    def __getParcelIterator(self):
        expr = '"BEST" = \'%s\'' % self.feature.attribute('BEST')
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

        btn = QPushButton(parcel.attribute('OBJ_ID'), self)
        btn.setSizePolicy(self.btnSizePolicy)
        QObject.connect(btn, SIGNAL('clicked(bool)'), lambda: self.goToParcel(parcel))
        self.layout.addWidget(btn, row, 0)

        lb1 = QLabel(parcel.attribute('water'), self)
        self.layout.addWidget(lb1, row, 1)

        lb2 = QLabel(parcel.attribute('bewerking'), self)
        self.layout.addWidget(lb2, row, 2)

class ParcelListDialog(QDialog, Ui_ParcelListDialog):
    def __init__(self, parcelInfoWidget, layer, feature):
        self.parcelInfoWidget = parcelInfoWidget
        self.main = self.parcelInfoWidget.main
        self.layer = layer
        self.feature = feature
        QDialog.__init__(self, self.main.iface.mainWindow())
        self.setupUi(self)

        self.parcelListWidget = ParcelListWidget(self.scrollAreaContents, self, self.layer, self.feature)
        self.scrollAreaLayout.insertWidget(0, self.parcelListWidget)

        QObject.connect(self.btn_zoomExtent, SIGNAL('clicked(bool)'), self.parcelListWidget.zoomExtent)

