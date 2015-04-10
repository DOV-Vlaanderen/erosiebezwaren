# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_parceldialog import Ui_ParcelDialog

class AttributeModel(QAbstractItemModel):
    def __init__(self, parent, layer, attributeName):
        self.layer = layer
        self.attributeName = attributeName
        QAbstractItemModel.__init__(self, parent)

        self.values = []
        self.updateValues()

    def updateValues(self):
        values = [''] #FIXME
        for feature in self.layer.getFeatures():
            v = feature.attribute(self.attributeName)
            if v not in values:
                values.append(v)
        self.values = values

    def columnCount(self, parent):
        return 1

    def rowCount(self, parent):
        return len(self.values)

    def index(self, row, col, parent):
        return self.createIndex(row, col, None)

    def parent(self, index):
        return QModelIndex()

    def data(self, index, role):
        return self.values[index.row()]

class ParcelDialog(QDialog, Ui_ParcelDialog):
    def __init__(self, main, layer, parcel):
        QDialog.__init__(self, main.iface.mainWindow())
        self.main = main
        self.layer = layer
        self.parcel = parcel
        self.setupUi(self)

        QObject.connect(self, SIGNAL('finished(int)'), self.finished)

        self.led_gewas.setText(self.parcel.attribute('GWS_NAAM'))
        self.btn_advBehandeld.setState(self.parcel.attribute('advBehandeld')==1)
        
        gewasModel = AttributeModel(self.cmb_gewasBezoek, self.layer, 'GWS_NAAM')
        self.cmb_gewasBezoek.setModel(gewasModel)

    def finished(self, result):
        if result == self.Accepted:
            print "SAVED"
        elif result == self.Rejected:
            print "NOT SAVED"
