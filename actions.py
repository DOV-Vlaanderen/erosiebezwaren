#-*- coding: utf-8 -*-

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os
import subprocess
import time

from parcelidentifier import ParcelIdentifyAction
from mapswitchdialog import MapSwitchAction

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
        toolbar.addAction(MapSwitchAction(self.main, self.parent))

        annotateArrow = QAction(QIcon(':/icons/icons/pijlen.png'), 'APY', self.parent)
        annotateArrow.setCheckable(True)
        QObject.connect(annotateArrow, SIGNAL('triggered(bool)'), self.annotateArrow)
        toolbar.addAction(annotateArrow)

        toolbar.addAction(ParcelIdentifyAction(self.main, self.parent, 'bezwarenkaart'))
