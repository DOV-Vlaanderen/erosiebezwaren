from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from parcelinfowidget import ParcelInfoDock, ParcelInfoWidget
from qgsutils import SpatialiteIterator

class MapToolParcelIdentifier(QgsMapToolIdentify):
    def __init__(self, main):
        self.main = main
        QgsMapToolIdentify.__init__(self, self.main.iface.mapCanvas())
        self.previousActiveLayer = None

        self.parcelInfoDock = ParcelInfoDock(self.main.iface.mainWindow())
        self.parcelInfoWidget = ParcelInfoWidget(self.parcelInfoDock, self.main)
        self.main.parcelInfoWidget = self.parcelInfoWidget
        self.parcelInfoDock.setWidget(self.parcelInfoWidget)

    def activate(self):
        self.main.selectionManager.activate()
        QgsMapToolIdentify.activate(self)

    def canvasReleaseEvent(self, mouseEvent):
        table = self.main.utils.getLayerByName('percelenkaart_table')
        view = self.main.utils.getLayerByName('percelenkaart_view')
        if table and view:
            self.main.iface.setActiveLayer(table)
            results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
            if results:
                fr = QgsFeatureRequest()
                fr.setFilterFids([results[0].mFeature.id()])
                viewFeats = [i for i in view.getFeatures(fr)]
                self.parcelInfoWidget.setLayer(view)
                self.parcelInfoWidget.setFeature(viewFeats[0])
                self.parcelInfoDock.show()
            else:
                self.parcelInfoWidget.clear()

        if self.previousActiveLayer:
            self.main.iface.setActiveLayer(self.previousActiveLayer)

class ParcelIdentifyAction(QAction):
    def __init__(self, main, parent):
        self.main = main
        QAction.__init__(self, QIcon(':/icons/icons/identify.png'), 'Identificeer perceel', parent)

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
            self.previousMapTool = self.mapCanvas.mapTool()
            self.mapCanvas.setMapTool(self.parcelMapTool)
            QObject.connect(self.mapCanvas, SIGNAL('mapToolSet(QgsMapTool*)'), self.mapToolChanged)
        else:
            QObject.disconnect(self.mapCanvas, SIGNAL('mapToolSet(QgsMapTool*)'), self.mapToolChanged)
            if self.previousMapTool:
                self.mapCanvas.setMapTool(self.previousMapTool)
