# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class SelectionManager(object):
    def __init__(self, main, tempLayerName):
        self.main = main
        self.utils = self.main.utils
        self.layerName = tempLayerName
        self.layer = None
        self.__getLayer()

    def __getLayer(self):
        if not self.layer:
            self.layer = self.utils.getLayerByName(self.layerName)
            if self.layer:
                self.layer.startEditing()
                self.layer.addAttribute(QgsField('mode', QVariant.Int, 'int', 1, 0))
                self.layer.commitChanges()
                self.layer.endEditCommand()
        return self.layer

    def activate(self):
        if not self.__getLayer():
            return
        if not self.layer.isEditable():
            self.layer.startEditing()

    def deactivate(self):
        if not self.__getLayer():
            return

        if self.layer.isEditable():
            self.layer.commitChanges()
            self.layer.endEditCommand()

    def clear(self, toggleRendering=True):
        if not self.__getLayer():
            return
        self.main.iface.mapCanvas().setRenderFlag(False)
        self.layer.selectAll()
        self.layer.deleteSelectedFeatures()
        if toggleRendering:
            self.main.iface.mapCanvas().setRenderFlag(True)

    def select(self, feature, mode=0, toggleRendering=True):
        if not self.__getLayer():
            return
        f = QgsFeature()
        f.fields().append(QgsField('mode', QVariant.Int, 'int', 1, 0))
        f.setGeometry(feature.geometry())
        f.setAttributes([mode])
        self.main.iface.mapCanvas().setRenderFlag(False)
        self.layer.addFeature(f)
        if toggleRendering:
            self.main.iface.mapCanvas().setRenderFlag(True)

    def clearWithMode(self, mode, toggleRendering=True):
        if not self.__getLayer():
            return
        self.main.iface.mapCanvas().setRenderFlag(False)
        for feature in self.layer.getFeatures(QgsFeatureRequest(QgsExpression('mode = %i' % mode))):
            self.layer.deleteFeature(feature.id())
        if toggleRendering:
            self.main.iface.mapCanvas().setRenderFlag(True)
