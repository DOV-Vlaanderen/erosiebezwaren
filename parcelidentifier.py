from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from qgsutils import SpatialiteIterator

class MapToolParcelIdentifier(QgsMapToolIdentify):
    def __init__(self, main):
        self.main = main
        QgsMapToolIdentify.__init__(self, self.main.iface.mapCanvas())
        self.previousActiveLayer = None

    def activate(self):
        self.main.selectionManager.activate()
        QgsMapToolIdentify.activate(self)

    def canvasReleaseEvent(self, mouseEvent):
        table = self.main.utils.getLayerByName('percelenkaart_table')
        view = self.main.utils.getLayerByName('percelenkaart_view')
        if table and view:
            self.main.iface.setActiveLayer(table)
            results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
            resultFid = None

            # Check for overlapping features:
            #   - if one of them is an objection, select that
            #   - if none of them is an objection, sort them to always select the same feature
            if len(results) == 1:
                resultFid = results[0].mFeature.id()
            elif len(results) > 1:
                fts = sorted([r.mFeature for r in results], key = lambda x: x.attribute('uniek_id'))
                fts_objections = [ft for ft in fts if ft.attribute('datum_bezwaar')]

                if len(fts_objections) == 1:
                    resultFid = fts_objections[0].id()
                elif len(fts_objections) == 0:
                    resultFid = fts[0].id()

            if resultFid:
                fr = QgsFeatureRequest()
                fr.setFilterFid(resultFid)
                feature = view.getFeatures(fr).next()
                self.main.parcelInfoWidget.setLayer(view)
                self.main.parcelInfoWidget.setFeature(feature)
                self.main.parcelInfoWidget.parent.show()
            else:
                self.main.parcelInfoWidget.clear()

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

    def deactivate(self):
        QObject.disconnect(self.main.iface.mapCanvas(), SIGNAL('mapToolSet(QgsMapTool*)'), self.mapToolChanged)
