#-*- coding: utf-8 -*-

#  DOV Erosiebezwaren, QGis plugin to assess field erosion on tablets
#  Copyright (C) 2015-2017  Roel Huybrechts
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
