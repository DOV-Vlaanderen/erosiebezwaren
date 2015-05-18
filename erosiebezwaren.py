# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc

import actions
import utils
import parcelinfowidget

from settingsmanager import SettingsManager
from selectionmanager import SelectionManager
from annotate import AnnotationManager

class Erosiebezwaren(object):
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.parcelInfoWidget = None
        self.dockWidget = None
        self.qsettings = QSettings()
        self.settings = SettingsManager(self)

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction('DOV - Erosiebezwaren', self.iface.mainWindow())
        # connect the action

        # Add toolbar and menu item
        self.toolbar = self.iface.addToolBar('DOV')
        self.iface.addPluginToMenu('DOV - Erosiebezwaren', self.action)

        self.utils = utils.Utils(self)
        self.selectionManager = SelectionManager(self, self.settings.getValue('layers/tempSelection'))
        self.annotationManager = AnnotationManager(self)
        self.actions = actions.Actions(self, self.iface.mainWindow())
        self.actions.addToToolbar(self.toolbar)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu('DOV - Erosiebezwaren', self.action)
        self.selectionManager.deactivate()
        self.annotationManager.deactivate()
        #self.iface.removeToolBarIcon(self.action)
        #remove the dock
        #self.iface.removeDockWidget(self.dockWidget)
        #self.dockWidget.close()
