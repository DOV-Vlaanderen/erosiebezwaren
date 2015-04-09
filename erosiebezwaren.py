# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc

from erosiebezwarenwidget import ErosiebezwarenWidget
import actions
import utils

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
        QObject.connect(self.action, SIGNAL('triggered()'), self.showHideDock)

        # Add toolbar and menu item
        self.toolbar = self.iface.addToolBar('DOV')
        self.iface.addPluginToMenu('DOV - Erosiebezwaren', self.action)

        self.utils = utils.Utils(self)
        self.actions = actions.Actions(self, self.iface.mainWindow())
        self.actions.addToToolbar(self.toolbar)

        # create the loop widget
        self.erosiebezwarenWidget = ErosiebezwarenWidget(self.iface)
        settings = QSettings()
        if not settings.value('/Qgis/enable_render_caching', False, type=bool):
            self.erosiebezwarenWidget.setStatus( 'Enable render caching to improve performance' )

        # create and show the dock
        self.dockWidget = QDockWidget('DOV - Erosiebezwaren', self.iface.mainWindow() )
        self.dockWidget.setObjectName('DOV - Erosiebezwaren')
        QObject.connect(self.dockWidget, SIGNAL('topLevelChanged ( bool )'), self.resizeDock)
        QObject.connect(self.dockWidget, SIGNAL('visibilityChanged ( bool )'), self.erosiebezwarenWidget.onVisibilityChanged)
        self.dockWidget.setWidget(self.erosiebezwarenWidget)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)

    def showHideDock(self):
        if not self.dockWidget.isVisible():
            self.dockWidget.setVisible( True )
        else:
            self.dockWidget.setVisible( False )

    #resize dock to minimum size if it is floating
    def resizeDock(self, topLevel):
        if topLevel:
            self.dockWidget.resize( self.dockWidget.minimumSize() )

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu('DOV - Erosiebezwaren', self.action)
        #self.iface.removeToolBarIcon(self.action)
        #remove the dock
        self.iface.removeDockWidget(self.dockWidget)
        self.dockWidget.close()
