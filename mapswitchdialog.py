# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_mapswitchdialog import Ui_MapSwitchDialog

class MapSwitchDialog(QDialog, Ui_MapSwitchDialog):
    def __init__(self, action):
        self.action = action
        self.main = self.action.main
        QDialog.__init__(self)
        self.setupUi(self)

        self.visibleBase = set(['Overzichtskaart', 'percelenkaart_table', 'Topokaart'])
        self.allLayers = set(['Orthofoto', 'Afstromingskaart', '2017 potentiele bodemerosie',
                              '2016 potentiele bodemerosie', '2015 potentiele bodemerosie',
                              '2014 potentiele bodemerosie', 'watererosie30', 'dem_kul', 'dem_agiv', 'Overzichtskaart',
                              'percelenkaart_table', 'Topokaart', 'Bodemkaart', 'Erosiebestrijdingswerken'])
        self.activeDem = None

        QObject.connect(self.btn_routekaart, SIGNAL('clicked(bool)'), self.toMapRoutekaart)
        QObject.connect(self.btn_orthofoto, SIGNAL('clicked(bool)'), self.toMapOrthofoto)
        QObject.connect(self.btn_erosie2014, SIGNAL('clicked(bool)'), self.toMapErosie2014)
        QObject.connect(self.btn_erosie2015, SIGNAL('clicked(bool)'), self.toMapErosie2015)
        QObject.connect(self.btn_erosie2016, SIGNAL('clicked(bool)'), self.toMapErosie2016)
        QObject.connect(self.btn_erosie2017, SIGNAL('clicked(bool)'), self.toMapErosie2017)
        QObject.connect(self.btn_watererosie_30, SIGNAL('clicked(bool)'), self.toMapWatererosie30)
        QObject.connect(self.btn_afstromingskaart, SIGNAL('clicked(bool)'), self.toMapAfstromingskaart)
        QObject.connect(self.btn_dem_kul, SIGNAL('clicked(bool)'), self.toMapDEMKul)
        QObject.connect(self.btn_dem_agiv, SIGNAL('clicked(bool)'), self.toMapDEMAgiv)
        QObject.connect(self.btn_bodemkaart, SIGNAL('clicked(bool)'), self.toMapBodemkaart)
        QObject.connect(self.btn_erosiebestrijding, SIGNAL('clicked(bool)'), self.toMapErosiebestrijding)

        self.populate()

    def show(self):
        self.populate()
        QDialog.show(self)

    def populate(self):
        showOldAnnotations = self.main.qsettings.value('/Qgis/plugins/Erosiebezwaren/map/oldAnnotations', '1')
        self.lbv_showOldAnnotations.setValue(int(showOldAnnotations))

    def toggleLayersGroups(self, enable=[], disable=[]):
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

    def toMapView(self, mapView):
        QObject.disconnect(self.main.iface.mapCanvas(), SIGNAL('extentsChanged()'), self.updateRasterColors)

        if mapView['autoDisable'] == True:
            mapView['disabledLayers'] = self.allLayers - mapView['enabledLayers']
        self.toggleLayersGroups(enable=mapView['enabledLayers'], disable=mapView['disabledLayers'])
        self.action.setText(mapView['label'])

        if mapView['label'] == 'Watererosie 30':
            self.main.actions.pixelMeasureAction.setRasterLayerActive(True)
        else:
            self.main.actions.pixelMeasureAction.setRasterLayerActive(False)
            self.main.actions.pixelMeasureAction.stopMeasure()

        self.accept()

    def toMapRoutekaart(self):
        self.toMapView({
            'enabledLayers': self.visibleBase,
            'autoDisable': True,
            'label': 'Routekaart'
        })

    def toMapOrthofoto(self):
        self.toMapView({
            'enabledLayers': (self.visibleBase - set(['Topokaart'])).union(['Orthofoto']),
            'autoDisable': True,
            'label': 'Orthofoto'
        })

    def toMapErosie2014(self):
        self.toMapView({
            'enabledLayers': self.visibleBase.union(['2014 potentiele bodemerosie']),
            'autoDisable': True,
            'label': 'Erosiekaart 2014'
        })

    def toMapErosie2015(self):
        self.toMapView({
            'enabledLayers': self.visibleBase.union(['2015 potentiele bodemerosie']),
            'autoDisable': True,
            'label': 'Erosiekaart 2015'
        })

    def toMapErosie2016(self):
        self.toMapView({
            'enabledLayers': self.visibleBase.union(['2016 potentiele bodemerosie']),
            'autoDisable': True,
            'label': 'Erosiekaart 2016'
        })

    def toMapErosie2017(self):
        self.toMapView({
            'enabledLayers': self.visibleBase.union(['2017 potentiele bodemerosie']),
            'autoDisable': True,
            'label': 'Erosiekaart 2017'
        })

    def toMapWatererosie30(self):
        self.toMapView({
            'enabledLayers': self.visibleBase.union(['watererosie30']),
            'autoDisable': True,
            'label': 'Watererosie 30'
        })

    def toMapAfstromingskaart(self):
        self.toMapView({
            'enabledLayers': (self.visibleBase - set(['percelenkaart_table', 'Overzichtskaart'])).union(['Afstromingskaart']),
            'autoDisable': True,
            'label': 'Afstromingskaart'
        })

    def toMapDEMKul(self):
        self.activeDem = self.main.utils.getLayerByName('dem_kul')
        self.updateRasterColors()

        self.toMapView({
            'enabledLayers': self.visibleBase.union(['dem_kul']),
            'autoDisable': True,
            'label': 'DEM KULeuven'
        })

        QObject.connect(self.main.iface.mapCanvas(), SIGNAL('extentsChanged()'), self.updateRasterColors)

    def toMapDEMAgiv(self):
        self.activeDem = self.main.utils.getLayerByName('dem_agiv')
        self.updateRasterColors()

        self.toMapView({
            'enabledLayers': self.visibleBase.union(['dem_agiv']),
            'autoDisable': True,
            'label': 'DEM AGIV'
        })

        QObject.connect(self.main.iface.mapCanvas(), SIGNAL('extentsChanged()'), self.updateRasterColors)

    def toMapBodemkaart(self):
        self.toMapView({
            'enabledLayers': (self.visibleBase - set(['Topokaart'])).union(['Bodemkaart']),
            'autoDisable': True,
            'label': 'Bodemkaart'
        })

    def toMapErosiebestrijding(self):
        self.toMapView({
            'enabledLayers': self.visibleBase.union(['Erosiebestrijdingswerken']),
            'autoDisable': True,
            'label': 'Erosiebestrijdingswerken'
        })

    def updateRasterColors(self):
        if not self.activeDem:
            return

        currentExtent = self.main.iface.mapCanvas().extent()
        bandStats = self.activeDem.dataProvider().bandStatistics(1, QgsRasterBandStats.Max | QgsRasterBandStats.Min,
                                                                 currentExtent, 1000)
        vmax = bandStats.maximumValue
        vmin = bandStats.minimumValue

        colorList = [QgsColorRampShader.ColorRampItem(((vmax-vmin)/4.0)*0+vmin, QColor('#2b83ba')),
                     QgsColorRampShader.ColorRampItem(((vmax-vmin)/4.0)*1+vmin, QColor('#abdda4')),
                     QgsColorRampShader.ColorRampItem(((vmax-vmin)/4.0)*2+vmin, QColor('#ffffbf')),
                     QgsColorRampShader.ColorRampItem(((vmax-vmin)/4.0)*3+vmin, QColor('#fdae61')),
                     QgsColorRampShader.ColorRampItem(((vmax-vmin)/4.0)*4+vmin, QColor('#d7191c'))]

        rasterShader = QgsRasterShader()
        colorRampShader = QgsColorRampShader()
        colorRampShader.setColorRampItemList(colorList)
        colorRampShader.setColorRampType(QgsColorRampShader.INTERPOLATED)
        rasterShader.setRasterShaderFunction(colorRampShader)
        pseudoColorRenderer = QgsSingleBandPseudoColorRenderer(self.activeDem.dataProvider(), self.activeDem.type(),
                                                               rasterShader)
        self.activeDem.setRenderer(pseudoColorRenderer)
        self.activeDem.triggerRepaint()

class MapSwitchButton(QToolButton):
    def __init__(self, main, parent):
        self.main = main
        QToolButton.__init__(self, parent)
        self.dialog = MapSwitchDialog(self)

        self.setText('Kies kaartbeeld')
        self.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(), QSizePolicy.Fixed)
        self.setMinimumHeight(self.main.iface.mainWindow().iconSize().height())

        QObject.connect(self, SIGNAL('clicked(bool)'), self.showDialog)
        QObject.connect(self.dialog, SIGNAL('finished(int)'), self.dialogClosed)

    def showDialog(self):
        self.dialog.move(0, 0)
        self.dialog.show()

    def dialogClosed(self, result):
        if result == 1:
            self.main.qsettings.setValue('/Qgis/plugins/Erosiebezwaren/map/oldAnnotations', str(self.dialog.lbv_showOldAnnotations.getValue()))
            oldAnnotations = ['Pijlen 2015', 'Polygonen 2015']
            if self.dialog.lbv_showOldAnnotations.getValue() == 1:
                self.dialog.toggleLayersGroups(enable=oldAnnotations)
            else:
                self.dialog.toggleLayersGroups(disable=oldAnnotations)

    def deactivate(self):
        self.main.qsettings.setValue('/Qgis/plugins/Erosiebezwaren/map/oldAnnotations', '1')
