# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc

import actions
import utils
import parcelinfowidget

class Erosiebezwaren:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.erosiebezwarenWidget = None
        self.dockWidget = None

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction('DOV - Erosiebezwaren', self.iface.mainWindow())
        # connect the action

        # Add toolbar and menu item
        self.toolbar = self.iface.addToolBar('DOV')
        self.iface.addPluginToMenu('DOV - Erosiebezwaren', self.action)

        self.utils = utils.Utils(self)
        self.actions = actions.Actions(self, self.iface.mainWindow())
        self.actions.addToToolbar(self.toolbar)

        # create the loop widget

        settings = QSettings()
        if not settings.value('/Qgis/enable_render_caching', False, type=bool):
            self.erosiebezwarenWidget.setStatus( 'Enable render caching to improve performance' )

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu('DOV - Erosiebezwaren', self.action)
        #self.iface.removeToolBarIcon(self.action)
        #remove the dock
        #self.iface.removeDockWidget(self.dockWidget)
        #self.dockWidget.close()
