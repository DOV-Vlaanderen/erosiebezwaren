# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class FeatureIdentifier(QgsMapToolIdentify):
    def canvasReleaseEvent(self, mouseEvent):
        results = self.identify(mouseEvent.x(),mouseEvent.y(), self.TopDownStopAtFirst, self.VectorLayer)
        if len(results) > 0:
            self.emit( SIGNAL( "geomIdentified" ), results[0].mLayer, results[0].mFeature)

class Utils(object):
    def __init__(self, main):
        self.main = main

    def getLayerByName(self, name):
        mapCanvas = self.main.iface.mapCanvas()
        for i in range(0, mapCanvas.layerCount()):
            if mapCanvas.layer(i).name() == name:
                return mapCanvas.layer(i)

    def editInLayer(self, name):
        layer = self.getLayerByName(name)
        if layer:
            self.main.iface.setActiveLayer(layer)
            layer.startEditing()
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

    def identifyFeature(self, layerName=None):
        def showDialog(layer, feature):
            print 'LAYER:', layer
            print 'FEATURE:', feature

        canvas = self.main.iface.mapCanvas()
        self.mapTool = FeatureIdentifier(canvas)
        canvas.setMapTool(self.mapTool)
        QObject.connect(self.mapTool , SIGNAL("geomIdentified") , showDialog )
        #canvas.unsetMapTool(self.mapTool)
        
