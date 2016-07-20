from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class RasterBlockWrapper(QObject):
    def __init__(self, rasterLayer, band, geometry):
        self.rasterLayer = rasterLayer
        self.band = band
        self.geometry = geometry
        self.geomBbox = self.geometry.boundingBox()

        self.pixelSizeX = self.rasterLayer.rasterUnitsPerPixelX()
        self.pixelSizeY = self.rasterLayer.rasterUnitsPerPixelY()
        self.pixelArea = self.pixelSizeX*self.pixelSizeY

        self._buffer = max(self.pixelSizeX, self.pixelSizeY)
        self.geomBbox = self.geomBbox.buffer(self._buffer)

        self.blockBbox = self._alignRectangleToGrid(self.geomBbox)
        self.blockWidth = int(self.blockBbox.width()/self.pixelSizeX)
        self.blockHeight = int(self.blockBbox.height()/self.pixelSizeY)
        self.block = self.rasterLayer.dataProvider().block(self.band, self.blockBbox, self.blockWidth, self.blockHeight)

        self.newGeometry = None
        self.stats = {}

        self._process()

    def _alignRectangleToGrid(self, rect):
        rasterExtent = self.rasterLayer.extent()
        newRect = QgsRectangle()
        newRect.setXMinimum(rasterExtent.xMinimum() + (round((rect.xMinimum()-(rasterExtent.xMinimum()))/self.pixelSizeX)*self.pixelSizeX))
        newRect.setYMinimum(rasterExtent.yMinimum() + (round((rect.yMinimum()-rasterExtent.yMinimum())/self.pixelSizeY)*self.pixelSizeY))
        newRect.setXMaximum(newRect.xMinimum() + (int(rect.width()/self.pixelSizeX)*self.pixelSizeX))
        newRect.setYMaximum(newRect.yMinimum() + (int(rect.height()/self.pixelSizeY)*self.pixelSizeY))
        return newRect

    def _rasterCellMatchesGeometry(self, rect):
        # 50% overlap
        return self.geometry.intersection(QgsGeometry.fromRect(rect)).area() >= (self.pixelArea*0.5)

    def _process(self):
        valSum = 0
        valCnt = 0
        for r in range(self.blockHeight):
            for c in range(self.blockWidth):
                cellRect = QgsRectangle()
                cellRect.setXMinimum(self.blockBbox.xMinimum()+(c*self.pixelSizeX))
                cellRect.setYMinimum(self.blockBbox.yMaximum()-(r*self.pixelSizeY)-self.pixelSizeY)
                cellRect.setXMaximum(self.blockBbox.xMinimum()+(c*self.pixelSizeX)+self.pixelSizeX)
                cellRect.setYMaximum(self.blockBbox.yMaximum()-(r*self.pixelSizeY))
                if self._rasterCellMatchesGeometry(cellRect):
                    valSum += self.block.value(r, c)
                    valCnt += 1
                    if not self.newGeometry:
                        self.newGeometry = QgsGeometry.fromRect(cellRect)
                    else:
                        self.newGeometry = self.newGeometry.combine(QgsGeometry.fromRect(cellRect))

        if valCnt > 0:
            self.stats.clear()
            self.stats['sum'] = valSum
            self.stats['count'] = valCnt
            self.stats['avg'] = valSum/float(valCnt)

    def getRasterizedGeometry(self):
        return self.newGeometry

    def getStats(self):
        return self.stats

    def isEmpty(self):
        return self.newGeometry == None

class PixelisedVectorLayer(QgsVectorLayer):
    def __init__(self, main, path=None, baseName=None, providerLib=None, loadDefaultStyleFlag=True, rasterLayer=None):
        QgsVectorLayer.__init__(self, path, baseName, providerLib, loadDefaultStyleFlag)
        self.rasterLayer = rasterLayer
        self.main = main

        props = self.rendererV2().symbol().symbolLayer(0).properties()
        props['color'] = '255,255,255,64'
        props['outline_color'] = '0,0,0,255'
        props['outline_width'] = '1'
        self.rendererV2().setSymbol(QgsFillSymbolV2.createSimple(props))

        self.setCustomProperty("labeling", "pal")
        self.setCustomProperty("labeling/isExpression", True)
        self.setCustomProperty("labeling/enabled", True)
        self.setCustomProperty("labeling/fontSize", "12")
        self.setCustomProperty("labeling/fontWeight", "75")
        self.setCustomProperty("labeling/displayAll", True)
        self.setCustomProperty("labeling/bufferColorA", 255)
        self.setCustomProperty("labeling/bufferColorR", 255)
        self.setCustomProperty("labeling/bufferColorG", 255)
        self.setCustomProperty("labeling/bufferColorB", 255)
        self.setCustomProperty("labeling/bufferSize", "1.5")

        QObject.connect(self, SIGNAL('editingStarted()'), self.cb_editingStarted)
        QObject.connect(self, SIGNAL('beforeCommitChanges()'), self.cb_beforeCommitChanges)

    def cb_editingStarted(self):
        QObject.connect(self.editBuffer(), SIGNAL('featureAdded(QgsFeatureId)'), self.cb_featureAdded)

    def cb_beforeCommitChanges(self):
        QObject.disconnect(self.editBuffer(), SIGNAL('featureAdded(QgsFeatureId)'), self.cb_featureAdded)

    def cb_featureAdded(self, fid):
        ft = self.getFeatures(QgsFeatureRequest(fid)).next()
        block = RasterBlockWrapper(self.rasterLayer, 1, ft.geometry())

        if not block.isEmpty():
            self.changeGeometry(fid, block.getRasterizedGeometry())
            self.setCustomProperty("labeling/fieldName", "%0.2f" % block.getStats()['avg'])
        else:
            self.editBuffer().deleteFeature(fid)

        self.commitChanges()

class PixelMeasureAction(QAction):
    def __init__(self, main, parent):
        self.main = main
        QAction.__init__(self, QIcon(':/icons/icons/pixelmeasure.png'), 'Bereken pixelwaarden', parent)

        self.mapCanvas = self.main.iface.mapCanvas()
        QObject.connect(self.mapCanvas, SIGNAL('extentsChanged()'), self.populateVisible)

        self.rasterLayer = self.main.utils.getLayerByName('watererosie30')
        self.rasterLayerActive = False
        self.previousMapTool = None
        self.layer = None

        self.setCheckable(True)
        QObject.connect(self, SIGNAL('triggered(bool)'), self.activate)

    def populateVisible(self):
        if not self.rasterLayer:
            self.rasterLayer = self.main.utils.getLayerByName('watererosie30')

        if self.rasterLayer and self.rasterLayerActive and \
            ((self.rasterLayer.hasScaleBasedVisibility() and \
            self.rasterLayer.minimumScale() <= self.mapCanvas.scale() < self.rasterLayer.maximumScale()) or \
            (not self.rasterLayer.hasScaleBasedVisibility())):
            self.setVisible(True)
        else:
            self.setVisible(False)

    def setRasterLayerActive(self, active):
        self.rasterLayerActive = active
        self.populateVisible()

    def activate(self, checked):
        if checked:
            self.startMeasure()
        else:
            self.stopMeasure()

    def startMeasure(self):
        layer = PixelisedVectorLayer(self.main, path='Polygon?crs=epsg:31370', baseName='Pixelberekening', providerLib='memory', rasterLayer=self.rasterLayer)
        self.layer = QgsMapLayerRegistry.instance().addMapLayer(layer, False)
        QgsProject.instance().layerTreeRoot().insertLayer(0, layer)
        self.main.iface.setActiveLayer(self.layer)
        self.main.iface.actionToggleEditing().trigger()
        self.main.iface.actionAddFeature().trigger()

    def stopMeasure(self):
        self.setChecked(False)
        if self.layer:
            try:
                QgsMapLayerRegistry.instance().removeMapLayer(self.layer.id())
            except RuntimeError:
                pass
            self.layer = None

    def deactivate(self):
        QObject.disconnect(self, SIGNAL('triggered(bool)'), self.startMeasure)
        QObject.connect(self.mapCanvas, SIGNAL('extentsChanged()'), self.populateVisible)
        self.stopMeasure()
