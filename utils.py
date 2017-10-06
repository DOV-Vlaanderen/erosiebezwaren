# -*- coding: utf-8 -*-
"""Module containing the Utils class."""

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


class Utils(object):
    """General utility methods used in the application."""

    def __init__(self, main):
        """Initialisation.

        Parameters
        ----------
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.

        """
        self.main = main

    def getLayerByName(self, name):
        """Find a layer by name.

        Parameters
        ----------
        name : str
            Name of the layer.

        Returns
        -------
        QgsMapLayer
            The first maplayer with the given name, or `None` if no layer with
            the given name exists.

        """
        for layer in self.main.iface.legendInterface().layers():
            if layer.name() == name:
                return layer
        return None

    def editInLayer(self, name):
        """Start drawing a new feature in the layer with the given name.

        Sets the layer as the active layer, enables edit mode and start the
        'add feature' action.

        Parameters
        ----------
        name : str
            The name of the layer.

        """
        layer = self.getLayerByName(name)
        if layer:
            self.main.iface.setActiveLayer(layer)
            self.main.iface.actionToggleEditing().trigger()
            self.main.iface.actionAddFeature().trigger()

    def stopEditInLayer(self, name):
        """Stop editing in lthe layer with the given name.

        Commit pending changes and end the edit command.

        Parameters
        ----------
        name : str
            The name of the layer.

        """
        layer = self.getLayerByName(name)
        if layer:
            layer.commitChanges()
            layer.endEditCommand()

    def toggleLayersGroups(self, enable, disable):
        """Toggle the visibility of the given layers or layergroups.

        Parameters
        ----------
        enable : list of str
            List of the names of layers or layergroups to enable (set visible).
        disable : list of str
            List of the names of layers or layergroups to disable (set
            invisible.)

        """
        legendInterface = self.main.iface.legendInterface()

        groups = legendInterface.groups()
        for i in range(0, len(groups)):
            if groups[i] in enable:
                legendInterface.setGroupVisible(i, True)
            if groups[i] in disable:
                legendInterface.setGroupVisible(i, False)

        for l in legendInterface.layers():
            if l.name() in enable:
                legendInterface.setLayerVisible(l, True)
            if l.name() in disable:
                legendInterface.setLayerVisible(l, False)
