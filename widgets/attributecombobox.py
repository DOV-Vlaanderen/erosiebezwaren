# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgsutils import SpatialiteIterator

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
            if v and v not in values:
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
        if index.row() < len(self.values):
            return self.values[index.row()]
        return None

class SpatialiteAttributeModel(AttributeModel):
    def __init__(self, parent, layer, attributeName):
        AttributeModel.__init__(self, parent, layer, attributeName)

    def updateValues(self):
        s = SpatialiteIterator(self.layer)
        self.values = s.rawQuery("SELECT DISTINCT %s FROM %s" % (self.attributeName, s.ds.table()))

class AttributeFilledCombobox(QComboBox):
    def __init__(self, parent, layer=None, attributename=None):
        QComboBox.__init__(self, parent)
        self.setEditable(True)
        self.parent = parent
        self.layer = layer
        self.attributename = attributename

        if not (self.layer and self.attributename):
            return

        if self.layer.dataProvider().name() == 'spatialite':
            self.model = SpatialiteAttributeModel(self.parent, self.layer, self.attributename)
        else:
            self.model = AttributeModel(self.parent, self.layer, self.attributename)
        self.setModel(self.model)

    def setSource(self, layer, attributename):
        self.layer = layer
        self.attributename = attributename

        if layer and attributename:
            self.model = AttributeModel(self.parent, self.layer, self.attributename)
            self.setModel(self.model)

    def setValue(self, value):
        if value:
            self.lineEdit().setText(value)
        else:
            self.lineEdit().clear()

    def getValue(self):
        return self.lineEdit().text()
