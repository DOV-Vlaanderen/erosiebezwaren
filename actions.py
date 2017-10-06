# -*- coding: utf-8 -*-
"""Module containing the Actions class."""

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

import os
import subprocess

from farmersearchdialog import FarmerSearchDialog
from gpszoomdialog import GpsZoomDialog
from mapswitchdialog import MapSwitchButton
from parcelidentifier import ParcelIdentifyAction
from pixelmeasure import PixelMeasureAction


class Actions(object):
    """Class defining all actions and a method to add them to the toolbar."""

    def __init__(self, main, parent, toolbar):
        """Initialisation.

        Initialise instance and add all actions to the toolbar.

        Parameters
        ----------
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.
        parent : QtGui.QWidget
            Widget used as parent widget for the actions.
        toolbar : QtGui.QToolBar
            Toolbar to add the actions to.

        """
        self.main = main
        self.parent = parent
        self.toolbar = toolbar

        self.gpsDialog = None

        self.addAllActionsToToolbar()

    def showKeyboard(self):
        """Open up the Windows on screen keyboard."""
        cmd = os.path.join(os.environ['COMMONPROGRAMFILES'],
                           'microsoft shared', 'ink', 'TabTip.exe')
        subprocess.Popen(cmd, env=os.environ, shell=True)

    def toggleFullscreen(self, checked=True):
        """Toggle fullscreen mode on the QGis window.

        Parameters
        ----------
        checked : boolean, optional
            Current state of the toggle action.

        """
        self.main.iface.actionToggleFullScreen().trigger()
        mB = self.main.iface.mainWindow().menuBar()
        mB.setVisible(not mB.isVisible())

    def searchFarmer(self):
        """Open the dialog to search for a farmer."""
        d = FarmerSearchDialog(self.main)
        d.show()

    def zoomToGps(self, checked):
        u"""Open the dialog to zoom to GPS coördinates or clear the marker.

        Parameters
        ----------
        checked : boolean
            Currect state of the toggle action.

        """
        if checked:
            self.gpsDialog = GpsZoomDialog(self.main)
            self.gpsDialog.show()
        else:
            if self.gpsDialog:
                self.gpsDialog.hide()
            self.main.selectionManagerPoints.clearWithMode(0)

    def addAllActionsToToolbar(self):
        """Initialise all actions and add them to the toolbar."""
        exitAction = QtGui.QAction(QtGui.QIcon(':/icons/icons/exit.png'),
                                   'Applicatie afsluiten', self.parent)
        QtCore.QObject.connect(exitAction, QtCore.SIGNAL('triggered(bool)'),
                               lambda: self.main.iface.actionExit().trigger())
        self.toolbar.addAction(exitAction)
        self.toolbar.addSeparator()

        self.mapSwitchButton = MapSwitchButton(self.main, self.parent)
        self.toolbar.addWidget(self.mapSwitchButton)
        self.toolbar.addSeparator()
        for action in self.main.annotationManager.getActions():
            self.toolbar.addAction(action)
        self.toolbar.addSeparator()

        farmerSearchAction = QtGui.QAction(
            QtGui.QIcon(':/icons/icons/searchfarmer.png'),
            "Landbouwer opzoeken", self.parent)
        QtCore.QObject.connect(farmerSearchAction,
                               QtCore.SIGNAL('triggered(bool)'),
                               self.searchFarmer)
        self.toolbar.addAction(farmerSearchAction)
        self.toolbar.addSeparator()

        zoomInAction = QtGui.QAction(
            QtGui.QIcon(':/icons/icons/zoomin.png'), "Zoom in", self.parent)
        QtCore.QObject.connect(zoomInAction, QtCore.SIGNAL('triggered(bool)'),
                               lambda: self.main.iface.mapCanvas().zoomIn())
        self.toolbar.addAction(zoomInAction)

        zoomOutAction = QtGui.QAction(QtGui.QIcon(':/icons/icons/zoomout.png'),
                                      "Zoom uit", self.parent)
        QtCore.QObject.connect(zoomOutAction, QtCore.SIGNAL('triggered(bool)'),
                               lambda: self.main.iface.mapCanvas().zoomOut())
        self.toolbar.addAction(zoomOutAction)

        gpsAction = QtGui.QAction(QtGui.QIcon(':/icons/icons/zoomgps.png'),
                                  u"Zoom naar GPS coördinaten", self.parent)
        gpsAction.setCheckable(True)
        QtCore.QObject.connect(gpsAction, QtCore.SIGNAL('triggered(bool)'),
                               self.zoomToGps)
        self.toolbar.addAction(gpsAction)

        toggleFullscreenAction = QtGui.QAction(
            QtGui.QIcon(':/icons/icons/fullscreen.png'),
            "Volledig scherm aan/uit", self.parent)
        QtCore.QObject.connect(toggleFullscreenAction,
                               QtCore.SIGNAL('triggered(bool)'),
                               self.toggleFullscreen)
        toggleFullscreenAction.setCheckable(True)
        self.toolbar.addAction(toggleFullscreenAction)

        self.toolbar.addSeparator()

        self.parcelIdentifyAction = ParcelIdentifyAction(self.main,
                                                         self.parent)
        self.toolbar.addAction(self.parcelIdentifyAction)

        touchAction = self.main.iface.actionTouch()
        touchAction.setIcon(QtGui.QIcon(':/icons/icons/movemap.png'))
        self.toolbar.addAction(touchAction)

        measureAction = self.main.iface.actionMeasure()
        measureAction.setIcon(QtGui.QIcon(':/icons/icons/measure.png'))
        self.toolbar.addAction(measureAction)

        self.pixelMeasureAction = PixelMeasureAction(self.main, self.parent,
                                                     'watererosie30')
        self.pixelMeasureAction.setVisible(False)
        self.toolbar.addAction(self.pixelMeasureAction)

    def deactivate(self):
        """Deactivate actions that need it and delete the toolbar."""
        self.parcelIdentifyAction.deactivate()
        self.mapSwitchButton.deactivate()
        self.pixelMeasureAction.deactivate()
        del(self.toolbar)
