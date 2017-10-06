# -*- coding: utf-8 -*-
"""Module containing the AnnotationManager class."""

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


class AnnotationManager(object):
    """Class defining the annotation actions and their behaviour.

    Annotations include drawing lines and polygons in their respective layers
    and adding a comment in the relevant attribute field.
    """

    def __init__(self, main):
        """Initialisation.

        Initialise the two actions and define their callback functions.

        Parameters
        ----------
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.

        """
        def drawArrow(start):
            if start:
                if self.currentlyEditing:
                    QtCore.QObject.disconnect(
                        self.main.iface.mapCanvas(),
                        QtCore.SIGNAL('mapToolSet(QgsMapTool*)'),
                        self.mapToolChanged)
                    self.main.utils.stopEditInLayer(self.currentlyEditing[0])
                    self.currentlyEditing[1].setChecked(False)
                self.currentlyEditing = (self.main.settings.getValue(
                    'layers/pijlen'), self.annotateArrow)
                self.main.utils.editInLayer(self.main.settings.getValue(
                    'layers/pijlen'))
                QtCore.QObject.connect(
                    self.main.iface.mapCanvas(),
                    QtCore.SIGNAL('mapToolSet(QgsMapTool*)'),
                    self.mapToolChanged)
            else:
                QtCore.QObject.disconnect(
                    self.main.iface.mapCanvas(),
                    QtCore.SIGNAL('mapToolSet(QgsMapTool*)'),
                    self.mapToolChanged)
                if self.currentlyEditing:
                    self.main.utils.stopEditInLayer(self.currentlyEditing[0])
                self.currentlyEditing = None

        def drawPolygon(start):
            if start:
                if self.currentlyEditing:
                    QtCore.QObject.disconnect(
                        self.main.iface.mapCanvas(),
                        QtCore.SIGNAL('mapToolSet(QgsMapTool*)'),
                        self.mapToolChanged)
                    self.main.utils.stopEditInLayer(self.currentlyEditing[0])
                    self.currentlyEditing[1].setChecked(False)
                self.currentlyEditing = (self.main.settings.getValue(
                    'layers/polygonen'), self.annotatePolygon)
                self.main.utils.editInLayer(self.main.settings.getValue(
                    'layers/polygonen'))
                QtCore.QObject.connect(
                    self.main.iface.mapCanvas(),
                    QtCore.SIGNAL('mapToolSet(QgsMapTool*)'),
                    self.mapToolChanged)
            else:
                QtCore.QObject.disconnect(
                    self.main.iface.mapCanvas(),
                    QtCore.SIGNAL('mapToolSet(QgsMapTool*)'),
                    self.mapToolChanged)
                if self.currentlyEditing:
                    self.main.utils.stopEditInLayer(self.currentlyEditing[0])
                self.currentlyEditing = None

        self.main = main
        self.currentlyEditing = None

        self.annotateArrow = QtGui.QAction(QtGui.QIcon(
            ':/icons/icons/pijlen.png'), 'Teken een pijl', self.main.iface)
        self.annotateArrow.setCheckable(True)
        QtCore.QObject.connect(self.annotateArrow,
                               QtCore.SIGNAL('triggered(bool)'), drawArrow)

        self.annotatePolygon = QtGui.QAction(
            QtGui.QIcon(':/icons/icons/polygonen.png'), 'Teken een polygoon',
            self.main.iface)
        self.annotatePolygon.setCheckable(True)
        QtCore.QObject.connect(self.annotatePolygon,
                               QtCore.SIGNAL('triggered(bool)'), drawPolygon)

    def getActions(self):
        """Return the two annotation actions, to add them to the toolbar.

        Returns
        -------
        (drawArrow, drawPolygon) : tuple
            Tuple containing pointers to the actions to draw an arrow and
            draw a polygon, respectively.

        """
        return (self.annotateArrow, self.annotatePolygon)

    def mapToolChanged(self, mt=None):
        """Stop editing if the user changes the mapTool.

        Listener for the `mapToolSet` signal.

        Parameters
        ----------
        mt : QGisGui.QgsMapTool, optional
            Current mapTool.

        """
        QtCore.QObject.disconnect(self.main.iface.mapCanvas(),
                                  QtCore.SIGNAL('mapToolSet(QgsMapTool*)'),
                                  self.mapToolChanged)
        if self.currentlyEditing:
            self.main.utils.stopEditInLayer(self.currentlyEditing[0])
            self.currentlyEditing[1].setChecked(False)
            self.currentlyEditing = None

    def deactivate(self):
        """Stop editing if currently in edit mode."""
        if self.currentlyEditing:
            # triggers mapToolChanged
            self.main.utils.stopEditInLayer(self.currentlyEditing[0])
