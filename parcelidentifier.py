from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from parcelinfowidget import ParcelInfoDock, ParcelInfoWidget

class MapToolParcelIdentifier(QgsMapToolIdentify):
    def __init__(self, main, layer=None):
        self.main = main
        self.layer = layer
        QgsMapToolIdentify.__init__(self, self.main.iface.mapCanvas())
        self.previousActiveLayer = None

        self.parcelInfoDock = ParcelInfoDock(self.main.iface.mainWindow())
        self.parcelInfoWidget = ParcelInfoWidget(self.parcelInfoDock)
        self.parcelInfoDock.setWidget(self.parcelInfoWidget)

    def setLayerByName(self, layerName):
        layer = self.main.utils.getLayerByName(layerName)
        if not layer:
            raise AttributeError("Layer %s not found." % layerName)
        self.layer = layer

    def setLayer(self, layer):
        if layer:
            self.layer = layer

    def activate(self):
        self.previousActiveLayer = self.main.iface.activeLayer()
        self.main.iface.setActiveLayer(self.layer)
        QgsMapToolIdentify.activate(self)

    def deactivate(self):
        if self.previousActiveLayer:
            self.main.iface.setActiveLayer(self.previousActiveLayer)
        QgsMapToolIdentify.deactivate(self)

    def canvasReleaseEvent(self, mouseEvent):
        results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
        if results:
            print [i.mFeature.attribute("GWS_NAAM") for i in results]
            #parcelDialog = ParcelWindow(self.main, self.layer, results[0].mFeature)
            #FIXME: wat bij meerdere resultaten
            self.parcelInfoWidget.setParcel(results[0].mFeature)
            self.parcelInfoDock.show()
        else:
            self.parcelInfoWidget.clear()

class ParcelIdentifyAction(QAction):
    def __init__(self, main, parent, layerName):
        self.main = main
        self.layerName = layerName
        QAction.__init__(self, 'IFY', parent)

        self.mapCanvas = self.main.iface.mapCanvas()
        self.previousMapTool = None
        self.parcelMapTool = MapToolParcelIdentifier(self.main)

        self.setCheckable(True)
        QObject.connect(self, SIGNAL('triggered(bool)'), self.identifyParcel)

    def mapToolChanged(self, mt):
        QObject.disconnect(self.main.iface.mapCanvas(), SIGNAL('mapToolSet(QgsMapTool*)'), self.mapToolChanged)
        self.setChecked(False)

    def identifyParcel(self, start):
        if start:
            try:
                self.parcelMapTool.setLayerByName(self.layerName)
            except AttributeError:
                self.setChecked(False)
                return
            self.previousMapTool = self.mapCanvas.mapTool()
            self.mapCanvas.setMapTool(self.parcelMapTool)
            QObject.connect(self.mapCanvas, SIGNAL('mapToolSet(QgsMapTool*)'), self.mapToolChanged)
        else:
            QObject.disconnect(self.mapCanvas, SIGNAL('mapToolSet(QgsMapTool*)'), self.mapToolChanged)
            if self.previousMapTool:
                self.mapCanvas.setMapTool(self.previousMapTool)
