# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class Utils(object):
    def __init__(self, main):
        self.main = main

    def getLayerByName(self, name):
        for layer in self.main.iface.legendInterface().layers():
            if layer.name() == name:
                return layer

    def editInLayer(self, name):
        layer = self.getLayerByName(name)
        if layer:
            self.main.iface.setActiveLayer(layer)
            self.main.iface.actionToggleEditing().trigger()
            self.main.iface.actionAddFeature().trigger()

    def stopEditInLayer(self, name):
        layer = self.getLayerByName(name)
        if layer:
            layer.commitChanges()
            layer.endEditCommand()

    def toggleLayersGroups(self, enable, disable):
        legendInterface = self.main.iface.legendInterface()

        groups = legendInterface.groups()
        for i in range(0, len(groups)):
            if groups[i] in enable:
                legendInterface.setGroupVisible(i, True)
            if groups[i] in disable:
                legendInterface.setGroupVisible(i, False)

        for l in legendInterface.layers():
            if l.name() in enable:
                legendInterface.setLayerVisible(l, True)
            if l.name() in disable:
                legendInterface.setLayerVisible(l, False)
