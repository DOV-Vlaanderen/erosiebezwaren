# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_parcellistdialog import Ui_ParcelListDialog
from widgets import valuelabel

class ObjectionListWidget(QWidget):
    def __init__(self, parent, parcelListDialog):
        self.parcelListDialog = parcelListDialog
        self.main = self.parcelListDialog.main
        QWidget.__init__(self, parent)

        self.horMaxSizePolicy = QSizePolicy()
        self.horMaxSizePolicy.setHorizontalPolicy(QSizePolicy.Maximum)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.parcelList = []

    def populate(self, layer, producentnr, producentnr_zo):
        self.layer = layer
        parcelList = []
        expr = '"datum_bezwaar" is not null and "producentnr" = \'%s\'' % producentnr
        for p in self.layer.getFeatures(QgsFeatureRequest(QgsExpression(expr))):
            parcelList.append(p)

        for p in sorted(parcelList, key = lambda x: int(x.attribute('perceelsnr_va_2015'))):
            p.layer = self.layer
            self.addParcel(p)

    def goToParcel(self, parcel):
        self.parcelListDialog.parcelInfoWidget.setLayer(parcel.layer)
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

        lb1 = QLabel(self)
        if parcel.attribute('advies_behandeld'):
            lb1.setText(parcel.attribute('advies_behandeld'))
        else:
            lb1.setText('Geen bezwaar')
        self.layout.addWidget(lb1, row, 1)

        lb2 = valuelabel.SensitivityColorLabel(self)
        lb2.setSizePolicy(self.horMaxSizePolicy)
        lb2.setText('2015')
        lb2.setText(parcel.attribute('kleur_2015'))
        self.layout.addWidget(lb2, row, 2)

class ParcelListWidget(ObjectionListWidget):
    def populate(self, layer, producentnr, producentnr_zo):
        self.layer = layer
        self.objectionLayer = self.main.utils.getLayerByName(self.main.settings.getValue('layers/bezwaren'))
        parcelList = []
        expr = '"producentnr_zo" = \'%s\'' % producentnr_zo
        for p in self.layer.getFeatures(QgsFeatureRequest(QgsExpression(expr))):
            parcelList.append(p)

        for p in sorted(parcelList, key = lambda x: int(x.attribute('perceelsnr_va_2015'))):
            self.addParcel(p)

    def addParcel(self, parcel):
        parcel.layer = self.layer
        if parcel.attribute('datum_bezwaar'):
            expr = '"producentnr_zo" = \'%s\' and "perceelsnr_va_2015" = \'%s\'' % (
                parcel.attribute('producentnr_zo'), parcel.attribute('perceelsnr_va_2015'))
            self.objectionLayer.getFeatures(QgsFeatureRequest(QgsExpression(expr))).nextFeature(parcel)
            parcel.layer = self.objectionLayer
        ObjectionListWidget.addParcel(self, parcel)

class ParcelListDialog(QDialog, Ui_ParcelListDialog):
    def __init__(self, parcelInfoWidget):
        self.parcelInfoWidget = parcelInfoWidget
        self.main = self.parcelInfoWidget.main
        self.main.selectionManager.activate()
        QDialog.__init__(self, self.main.iface.mainWindow())
        self.setupUi(self)

        QObject.connect(self, SIGNAL('finished(int)'), self.__clearSelection)

    def populate(self, layer, naam, producentnr, producentnr_zo):
        self.layer = layer

        if self.layer.name() == self.main.settings.getValue('layers/bezwaren'):
            self.listWidget = ObjectionListWidget(self.scrollAreaContents, self)
            self.lbv_bezwaren_van.setText('Bezwaren van %s' % naam)
            self.setWindowTitle('Bezwarenlijst')
        elif self.layer.name() == self.main.settings.getValue('layers/percelen'):
            self.listWidget = ParcelListWidget(self.scrollAreaContents, self)
            self.lbv_bezwaren_van.setText('Percelen van %s' % naam)
            self.setWindowTitle('Percelenlijst')

        QObject.connect(self.btn_zoomExtent, SIGNAL('clicked(bool)'), self.listWidget.zoomExtent)
        self.scrollAreaLayout.insertWidget(0, self.listWidget)
        self.listWidget.populate(self.layer, producentnr, producentnr_zo)

    def __clearSelection(self):
        if not self.parcelInfoWidget.feature:
            self.main.selectionManager.clear()
