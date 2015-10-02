#-*- coding: utf-8 -*-

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os
import subprocess
import time

from parcelidentifier import ParcelIdentifyAction
from mapswitchdialog import MapSwitchButton
from farmersearchdialog import FarmerSearchDialog
from gpszoomdialog import GpsZoomDialog

class Actions(object):
    def __init__(self, main, parent):
        self.main = main
        self.parent = parent

    def showKeyboard(self):
        cmd = os.path.join(os.environ['COMMONPROGRAMFILES'], 'microsoft shared', 'ink', 'TabTip.exe')
        sp = subprocess.Popen(cmd, env=os.environ, shell=True)

    def toggleFullscreen(self, t):
        self.main.iface.actionToggleFullScreen().trigger()
        mB = self.main.iface.mainWindow().menuBar()
        mB.setVisible(not mB.isVisible())

    def searchFarmer(self):
        d = FarmerSearchDialog(self.main)
        d.show()

    def zoomToGps(self):
        d = GpsZoomDialog(self.main)
        d.show()

    def addToToolbar(self, toolbar):
        exitAction = QAction(QIcon(':/icons/icons/exit.png'), 'Applicatie afsluiten', self.parent)
        QObject.connect(exitAction, SIGNAL('triggered(bool)'), lambda: self.main.iface.actionExit().trigger())
        toolbar.addAction(exitAction)
        toolbar.addSeparator()

        toolbar.addWidget(MapSwitchButton(self.main, self.parent))
        toolbar.addSeparator()
        self.main.annotationManager.addActionsToToolbar(toolbar)
        toolbar.addSeparator()

        farmerSearchAction = QAction(QIcon(':/icons/icons/searchfarmer.png'), "Landbouwer opzoeken", self.parent)
        QObject.connect(farmerSearchAction, SIGNAL('triggered(bool)'), self.searchFarmer)
        toolbar.addAction(farmerSearchAction)
        toolbar.addSeparator()

        zoomInAction = QAction(QIcon(':/icons/icons/zoomin.png'), "Zoom in", self.parent)
        QObject.connect(zoomInAction, SIGNAL('triggered(bool)'), lambda: self.main.iface.mapCanvas().zoomIn())
        toolbar.addAction(zoomInAction)

        zoomOutAction = QAction(QIcon(':/icons/icons/zoomout.png'), "Zoom uit", self.parent)
        QObject.connect(zoomOutAction, SIGNAL('triggered(bool)'), lambda: self.main.iface.mapCanvas().zoomOut())
        toolbar.addAction(zoomOutAction)

        gpsAction = QAction(QIcon(':/icons/icons/zoomgps.png'), u"Zoom naar GPS coördinaten", self.parent)
        QObject.connect(gpsAction, SIGNAL('triggered(bool)'), self.zoomToGps)
        toolbar.addAction(gpsAction)

        toggleFullscreenAction = QAction(QIcon(':/icons/icons/fullscreen.png'), "Volledig scherm aan/uit", self.parent)
        QObject.connect(toggleFullscreenAction, SIGNAL('triggered(bool)'), self.toggleFullscreen)
        toggleFullscreenAction.setCheckable(True)
        toolbar.addAction(toggleFullscreenAction)

        toolbar.addSeparator()

        toolbar.addAction(ParcelIdentifyAction(self.main, self.parent))

        touchAction = self.main.iface.actionTouch()
        touchAction.setIcon(QIcon(':/icons/icons/movemap.png'))
        toolbar.addAction(touchAction)

        measureAction = self.main.iface.actionMeasure()
        measureAction.setIcon(QIcon(':/icons/icons/measure.png'))
        toolbar.addAction(measureAction)
