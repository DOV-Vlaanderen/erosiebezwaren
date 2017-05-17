# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc

import actions
import utils

from annotate import AnnotationManager
from parcelinfowidget import ParcelInfoDock, ParcelInfoWidget
from selectionmanager import SelectionManager
from settingsmanager import SettingsManager

class Erosiebezwaren(object):
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        self.qsettings = QSettings()
        self.settings = SettingsManager(self)

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction('DOV - Erosiebezwaren', self.iface.mainWindow())

        # Add toolbar and menu item
        self.toolbar = self.iface.addToolBar('Erosiebezwaren toolbar')
        self.toolbar.setObjectName('ErosiebezwarenToolbar')
        self.iface.addPluginToMenu('DOV - Erosiebezwaren', self.action)

        self.utils = utils.Utils(self)
        self.selectionManagerPolygons = SelectionManager(self, self.settings.getValue('layers/tempSelectionPolygons'))
        self.selectionManagerPoints = SelectionManager(self, self.settings.getValue('layers/tempSelectionPoints'))
        self.annotationManager = AnnotationManager(self)
        self.actions = actions.Actions(self, self.iface.mainWindow(), self.toolbar)

        self.parcelInfoDock = ParcelInfoDock(self.iface.mainWindow())
        self.parcelInfoWidget = ParcelInfoWidget(self.parcelInfoDock, self)
        self.parcelInfoDock.setWidget(self.parcelInfoWidget)

    def unload(self):
        self.iface.removePluginMenu('DOV - Erosiebezwaren', self.action)

        # FIXME: commented out to prevent segfault on QGis exit..?
        #self.selectionManagerPolygons.deactivate()
        #self.selectionManagerPoints.deactivate()
        #self.annotationManager.deactivate()
        self.actions.deactivate()
        self.iface.removeDockWidget(self.parcelInfoDock)

        del(self.actions)
        del(self.toolbar)
        del(self.parcelInfoWidget)
        del(self.parcelInfoDock)
        del(self.selectionManagerPolygons)
        del(self.selectionManagerPoints)
        del(self.annotationManager)
