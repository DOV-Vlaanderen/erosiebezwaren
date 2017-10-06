# -*- coding: utf-8 -*-
"""Module containing the SelectionManager class."""

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
import qgis.core as QGisCore


class SelectionManager(object):
    """Class to manage selection of features or geometries.

    Copies to geometry (of features) to a seperate layer to make them stand
    out on the map.
    """

    def __init__(self, main, tempLayerName):
        """Initialisation.

        Parameters
        ----------
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.
        tempLayerName : str
            Name of the layer to use as a temporary layer to copy the
            geometries into.

        """
        self.main = main
        self.utils = self.main.utils
        self.layerName = tempLayerName
        self.layer = None
        self.__getLayer()

    def __getLayer(self):
        """Find the QgsVectorLayer based on its name and add two attributes.

        Adds two attributes 'mode' (int) and 'label' (str). Mode is to
        differentiate between various selection modes (f. ex. using a different
        style). Label is to be able to show a label for selected features.
        """
        if not self.layer:
            self.layer = self.utils.getLayerByName(self.layerName)
            if self.layer:
                self.layer.startEditing()
                self.layer.addAttribute(QGisCore.QgsField(
                    'mode', QtCore.QVariant.Int, 'int', 1, 0))
                self.layer.addAttribute(QGisCore.QgsField(
                    'label', QtCore.QVariant.String, 'string', 1, 0))
                self.layer.commitChanges()
                self.layer.endEditCommand()
        return self.layer

    def activate(self):
        """Enable selection by enabling edit mode on the tempLayer."""
        if not self.__getLayer():
            return
        if not self.layer.isEditable():
            self.layer.startEditing()

    def deactivate(self):
        """Disable selection by disabling edit mode on the tempLayer."""
        if not self.__getLayer():
            return

        if self.layer.isEditable():
            self.layer.commitChanges()
            self.layer.endEditCommand()

    def clear(self, toggleRendering=True):
        """Clear the selection by removing all features from the tempLayer.

        Parameters
        ----------
        toggleRendering : boolean, optional
            Redraw the map after changing the tempLayer. Defaults to True.
            When making multiple changes to the selection set only the last
            change to toggleRendering=`True` for improved performance.

        """
        if not self.__getLayer():
            return
        self.main.iface.mapCanvas().setRenderFlag(False)
        self.layer.selectAll()
        self.layer.deleteSelectedFeatures()
        if toggleRendering:
            self.main.iface.mapCanvas().setRenderFlag(True)

    def selectGeometry(self, geometry, mode=0, label="", toggleRendering=True):
        """Add the given geometry to the selection.

        Parameters
        ----------
        geometry : QGisCore.QgsGeometry
            Geometry to add to the selection.
        mode : int, optional
            Mode to use for the selected geometry. Defaults to 0.
        label : str, optional
            Label to use for the selected geometry. Defaults to an empty label.
        toggleRendering : boolean, optional
            Redraw the map after changing the tempLayer. Defaults to True.
            When making multiple changes to the selection set only the last
            change to toggleRendering=`True` for improved performance.

        """
        if not self.__getLayer():
            return
        f = QGisCore.QgsFeature()
        f.fields().append(QGisCore.QgsField(
            'mode', QtCore.QVariant.Int, 'int', 1, 0))
        f.fields().append(QGisCore.QgsField(
            'label', QtCore.QVariant.String, 'string', 1, 0))
        f.setGeometry(geometry)
        f.setAttributes([mode, label])
        self.main.iface.mapCanvas().setRenderFlag(False)
        self.layer.addFeature(f)
        if toggleRendering:
            self.main.iface.mapCanvas().setRenderFlag(True)

    def select(self, feature, mode=0, label="", toggleRendering=True):
        """Add the geometry of the given feature to the selection.

        Parameters
        ----------
        feature : QGisCore.QgsFeature
            Add the geometry of this feature to add to the selection.
        mode : int, optional
            Mode to use for the selected geometry. Defaults to 0.
        label : str, optional
            Label to use for the selected geometry. Defaults to an empty label.
        toggleRendering : boolean, optional
            Redraw the map after changing the tempLayer. Defaults to True.
            When making multiple changes to the selection set only the last
            change to toggleRendering=`True` for improved performance.

        """
        self.selectGeometry(feature.geometry(), mode=mode, label=label,
                            toggleRendering=toggleRendering)

    def clearWithMode(self, mode, toggleRendering=True):
        """Clear the selected geometry that have the given mode.

        Parameters
        ----------
        mode : int
            Clear the geometries that have been selected using this mode.
        toggleRendering : boolean, optional
            Redraw the map after changing the tempLayer. Defaults to True.
            When making multiple changes to the selection set only the last
            change to toggleRendering=`True` for improved performance.

        """
        if not self.__getLayer():
            return
        self.main.iface.mapCanvas().setRenderFlag(False)
        for feature in self.layer.getFeatures(QGisCore.QgsFeatureRequest(
                QGisCore.QgsExpression('mode = %i' % mode))):
            self.layer.deleteFeature(feature.id())
        if toggleRendering:
            self.main.iface.mapCanvas().setRenderFlag(True)
