#-*- coding: utf-8 -*-

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os
import subprocess
import time

from parcelidentifier import ParcelIdentifyAction

class IconSize64Style(QCommonStyle):
    def pixelMetric(self, metric, option=0, widget=0):
        if metric == QStyle.PM_SmallIconSize:
            return 64
        else:
            return QCommonStyle.pixelMetric(self, metric, option, widget)

class MapViewGroup(QToolButton):
    def __init__(self, main, icon, text, parent):
        QToolButton.__init__(self, parent)
        self.main = main
        self.setText(text)
        self.setIcon(icon)
        self.setPopupMode(self.InstantPopup)
        self.menu = QMenu(self)
        #self.menu.setStyle(IconSize64Style())
        self.setMenu(self.menu)

    def addMapView(self, icon, name, layersEnabled, layersDisabled):
        action = QAction(icon, name, self.menu)
        QObject.connect(action, SIGNAL('triggered(bool)'),
            lambda x: self.main.utils.toggleLayersGroups(layersEnabled, layersDisabled))
        self.menu.addAction(action)

class Actions(object):
    def __init__(self, main, parent):
        self.main = main
        self.parent = parent

    def annotateArrow(self, start):
        if start:
            self.main.utils.editInLayer('Pijlen')
        else:
            self.main.utils.stopEditInLayer('Pijlen')

    def showKeyboard(self):
        cmd = os.path.join(os.environ['COMMONPROGRAMFILES'], 'microsoft shared', 'ink', 'TabTip.exe')
        sp = subprocess.Popen(cmd, env=os.environ, shell=True)

    def addToToolbar(self, toolbar):
        annotateArrow = QAction(QIcon(':/icons/icons/pijlen.png'), 'APY', self.parent)
        annotateArrow.setCheckable(True)
        QObject.connect(annotateArrow, SIGNAL('triggered(bool)'), self.annotateArrow)
        toolbar.addAction(annotateArrow)

        loketOverzichtskaart = MapViewGroup(self.main, QIcon(':/icons/icons/overzichtskaart.png'), 'OZK', toolbar)
        loketOverzichtskaart.addMapView(
            QIcon(':/icons/icons/routekaart.png'), 'Routekaart',
            layersEnabled=['Overzichtskaart', 'bezwarenkaart', 'Topokaart'],
            layersDisabled=['Afstromingskaart', '2015 potentiele bodemerosie', '2014 potentiele bodemerosie', '2013 potentiele bodemerosie', 'watererosie', 'bewerkingserosie'])
        loketOverzichtskaart.addMapView(
            QIcon(':/icons/icons/luchtfoto.png'), 'Luchtfoto',
            layersEnabled=['Overzichtskaart', 'bezwarenkaart', 'Topokaart', 'luchtfoto'],
            layersDisabled=['Afstromingskaart', '2015 potentiele bodemerosie', '2014 potentiele bodemerosie', '2013 potentiele bodemerosie', 'watererosie', 'bewerkingserosie'])
        toolbar.addWidget(loketOverzichtskaart)

        loketErosiekaart = MapViewGroup(self.main, QIcon(':/icons/icons/erosiekaart.png'), 'EZK', toolbar)
        loketErosiekaart.addMapView(
            QIcon(':/icons/icons/erosiekaart_2015.png'), 'Erosiekaart 2015',
            layersEnabled=['Overzichtskaart', 'bezwarenkaart', 'Topokaart', '2015 potentiele bodemerosie'],
            layersDisabled=['Afstromingskaart', '2014 potentiele bodemerosie', '2013 potentiele bodemerosie', 'watererosie', 'bewerkingserosie'])
        loketErosiekaart.addMapView(
            QIcon(':/icons/icons/erosiekaart_2014.png'), 'Erosiekaart 2014',
            layersEnabled=['Overzichtskaart', 'bezwarenkaart', 'Topokaart', '2014 potentiele bodemerosie'],
            layersDisabled=['Afstromingskaart', '2015 potentiele bodemerosie', '2013 potentiele bodemerosie', 'watererosie', 'bewerkingserosie'])
        loketErosiekaart.addMapView(
            QIcon(':/icons/icons/erosiekaart_2013.png'), 'Erosiekaart 2013',
            layersEnabled=['Overzichtskaart', 'bezwarenkaart', 'Topokaart', '2013 potentiele bodemerosie'],
            layersDisabled=['Afstromingskaart', '2014 potentiele bodemerosie', '2015 potentiele bodemerosie', 'watererosie', 'bewerkingserosie'])
        toolbar.addWidget(loketErosiekaart)

        loketPixelkaart = MapViewGroup(self.main, QIcon(':/icons/icons/pixelkaarten.png'), 'PXK', toolbar)
        loketPixelkaart.addMapView(
            QIcon(':/icons/icons/pixelkaart_watererosie.png'), 'Watererosie',
            layersEnabled=['Overzichtskaart', 'bezwarenkaart', 'Topokaart', 'watererosie', 'Afstromingskaart'],
            layersDisabled=['2015 potentiele bodemerosie', '2014 potentiele bodemerosie', '2013 potentiele bodemerosie', 'bewerkingserosie'])
        loketPixelkaart.addMapView(
            QIcon(':/icons/icons/pixelkaart_bewerkingserosie.png'), 'Bewerkingserosie',
            layersEnabled=['Overzichtskaart', 'bezwarenkaart', 'Topokaart', 'bewerkingserosie'],
            layersDisabled=['Afstromingskaart', '2015 potentiele bodemerosie', '2014 potentiele bodemerosie', '2013 potentiele bodemerosie', 'watererosie'])
        toolbar.addWidget(loketPixelkaart)

        toolbar.addAction(ParcelIdentifyAction(self.main, self.parent, 'bezwarenkaart'))


