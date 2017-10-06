# -*- coding: utf-8 -*-
"""Module containing the Erosiebezwaren class."""

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

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui

import actions
import utils

from annotate import AnnotationManager
from parcelinfowidget import ParcelInfoDock
from parcelinfowidget import ParcelInfoWidget
from selectionmanager import SelectionManager
from settingsmanager import SettingsManager


class Erosiebezwaren(object):
    """Main class of the Erosiebezwaren plugin.

    Used to instanciate objects of the other classes and provide links between
    them.
    """

    def __init__(self, iface):
        """Initialisation.

        Parameters
        ----------
        iface : QGisGui.QGisInterface
            Instance of the QGis interface.

        """
        # Save reference to the QGIS interface
        self.iface = iface

        self.qsettings = QtCore.QSettings()
        self.settings = SettingsManager(self)

    def initGui(self):
        """Initialise the GUI of the plugin."""
        # Create action that will start plugin configuration
        self.action = QtGui.QAction('DOV - Erosiebezwaren',
                                    self.iface.mainWindow())

        # Add toolbar and menu item
        self.toolbar = self.iface.addToolBar('Erosiebezwaren toolbar')
        self.toolbar.setObjectName('ErosiebezwarenToolbar')
        self.iface.addPluginToMenu('DOV - Erosiebezwaren', self.action)

        self.utils = utils.Utils(self)
        self.selectionManagerPolygons = SelectionManager(
            self, self.settings.getValue('layers/tempSelectionPolygons'))
        self.selectionManagerPoints = SelectionManager(
            self, self.settings.getValue('layers/tempSelectionPoints'))
        self.annotationManager = AnnotationManager(self)
        self.actions = actions.Actions(self, self.iface.mainWindow(),
                                       self.toolbar)

        self.parcelInfoDock = ParcelInfoDock(self.iface.mainWindow())
        self.parcelInfoWidget = ParcelInfoWidget(self.parcelInfoDock, self)
        self.parcelInfoDock.setWidget(self.parcelInfoWidget)

    def unload(self):
        """Unload the plugin.

        Deactivate all loaded objectes in order to shut down properly.
        """
        self.iface.removePluginMenu('DOV - Erosiebezwaren', self.action)

        # FIXME: commented out to prevent segfault on QGis exit..?
        # self.selectionManagerPolygons.deactivate()
        # self.selectionManagerPoints.deactivate()
        # self.annotationManager.deactivate()
        self.actions.deactivate()
        self.iface.removeDockWidget(self.parcelInfoDock)

        del(self.actions)
        del(self.toolbar)
        del(self.parcelInfoWidget)
        del(self.parcelInfoDock)
        del(self.selectionManagerPolygons)
        del(self.selectionManagerPoints)
        del(self.annotationManager)
