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

        QObject.connect(self.btn_routekaart, SIGNAL('clicked(bool)'), self.toMapRoutekaart)
        QObject.connect(self.btn_orthofoto, SIGNAL('clicked(bool)'), self.toMapOrthofoto)
        QObject.connect(self.btn_erosie2013, SIGNAL('clicked(bool)'), self.toMapErosie2013)
        QObject.connect(self.btn_erosie2014, SIGNAL('clicked(bool)'), self.toMapErosie2014)
        QObject.connect(self.btn_erosie2015, SIGNAL('clicked(bool)'), self.toMapErosie2015)
        QObject.connect(self.btn_watererosie, SIGNAL('clicked(bool)'), self.toMapWatererosie)
        QObject.connect(self.btn_bewerkingserosie, SIGNAL('clicked(bool)'), self.toMapBewerkingserosie)
        QObject.connect(self.btn_afstromingskaart, SIGNAL('clicked(bool)'), self.toMapAfstromingskaart)
        QObject.connect(self.btn_corr_dem, SIGNAL('clicked(bool)'), self.toMapCorrectiesDEM)

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

    def toMapView(self, mapView):
        self.toggleLayersGroups(enable=mapView['enabledLayers'], disable=mapView['disabledLayers'])
        self.action.setText(mapView['label'])
        self.hide()

    def toMapRoutekaart(self):
        self.toMapView({
            'enabledLayers': ['Overzichtskaart', 'bezwarenkaart', 'percelenkaart', 'Topokaart'],
            'disabledLayers': ['Orthofoto', 'Afstromingskaart', '2015 potentiele bodemerosie', '2014 potentiele bodemerosie', '2013 potentiele bodemerosie', 'watererosie', 'bewerkingserosie', 'correcties_dem'],
            'label': 'Routekaart'
        })

    def toMapOrthofoto(self):
        self.toMapView({
            'enabledLayers': ['Overzichtskaart', 'bezwarenkaart', 'percelenkaart', 'Orthofoto'],
            'disabledLayers': ['Topokaart', 'Afstromingskaart', '2015 potentiele bodemerosie', '2014 potentiele bodemerosie', '2013 potentiele bodemerosie', 'watererosie', 'bewerkingserosie', 'correcties_dem'],
            'label': 'Orthofoto'
        })

    def toMapErosie2013(self):
        self.toMapView({
            'enabledLayers': ['Overzichtskaart', 'bezwarenkaart', 'percelenkaart', 'Topokaart', '2013 potentiele bodemerosie'],
            'disabledLayers': ['Orthofoto', '2014 potentiele bodemerosie', '2015 potentiele bodemerosie', 'Afstromingskaart', 'watererosie', 'bewerkingserosie', 'correcties_dem'],
            'label': 'Erosiekaart 2013'
        })

    def toMapErosie2014(self):
        self.toMapView({
            'enabledLayers': ['Overzichtskaart', 'bezwarenkaart', 'percelenkaart', 'Topokaart', '2014 potentiele bodemerosie'],
            'disabledLayers': ['Orthofoto', '2013 potentiele bodemerosie', '2015 potentiele bodemerosie', 'Afstromingskaart', 'watererosie', 'bewerkingserosie', 'correcties_dem'],
            'label': 'Erosiekaart 2014'
        })

    def toMapErosie2015(self):
        self.toMapView({
            'enabledLayers': ['Overzichtskaart', 'bezwarenkaart', 'percelenkaart', 'Topokaart', '2015 potentiele bodemerosie'],
            'disabledLayers': ['Orthofoto', '2014 potentiele bodemerosie', '2013 potentiele bodemerosie', 'Afstromingskaart', 'watererosie', 'bewerkingserosie', 'correcties_dem'],
            'label': 'Erosiekaart 2015'
        })

    def toMapWatererosie(self):
        self.toMapView({
            'enabledLayers': ['Overzichtskaart', 'bezwarenkaart', 'percelenkaart', 'Topokaart', 'watererosie'],
            'disabledLayers': ['Afstromingskaart', 'Orthofoto', '2015 potentiele bodemerosie', '2014 potentiele bodemerosie', '2013 potentiele bodemerosie', 'bewerkingserosie', 'correcties_dem'],
            'label': 'Watererosie'
        })

    def toMapBewerkingserosie(self):
        self.toMapView({
            'enabledLayers': ['Overzichtskaart', 'bezwarenkaart', 'percelenkaart', 'Topokaart', 'bewerkingserosie'],
            'disabledLayers': ['Orthofoto', '2015 potentiele bodemerosie', '2014 potentiele bodemerosie', '2013 potentiele bodemerosie', 'watererosie', 'Afstromingskaart', 'correcties_dem'],
            'label': 'Bewerkingserosie'
        })

    def toMapAfstromingskaart(self):
        self.toMapView({
            'enabledLayers': ['Afstromingskaart', 'Topokaart'],
            'disabledLayers': ['Orthofoto', '2015 potentiele bodemerosie', '2014 potentiele bodemerosie', '2013 potentiele bodemerosie', 'watererosie', 'bewerkingserosie', 'bezwarenkaart', 'percelenkaart', 'Overzichtskaart', 'correcties_dem'],
            'label': 'Afstromingskaart'
        })

    def toMapCorrectiesDEM(self):
        self.toMapView({
            'enabledLayers': ['Overzichtskaart', 'bezwarenkaart', 'percelenkaart', 'Topokaart', 'correcties_dem'],
            'disabledLayers': ['Orthofoto', '2015 potentiele bodemerosie', '2014 potentiele bodemerosie', '2013 potentiele bodemerosie', 'bewerkingserosie', 'watererosie', 'Afstromingskaart'],
            'label': 'Correcties DEM'
        })

class MapSwitchButton(QToolButton):
    def __init__(self, main, parent):
        self.main = main
        QToolButton.__init__(self, parent)
        self.dialog = MapSwitchDialog(self)

        self.setText('Kies kaartbeeld')
        self.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(), QSizePolicy.Fixed)
        self.setMinimumHeight(64)

        QObject.connect(self, SIGNAL('clicked(bool)'), self.showDialog)

    def showDialog(self):
        self.dialog.move(0, 0)
        self.dialog.show()
