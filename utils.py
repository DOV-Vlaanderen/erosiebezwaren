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
from qgis.gui import *

class Utils(object):
    def __init__(self, main):
        self.main = main

    def getLayerByName(self, name):
        for layer in self.main.iface.legendInterface().layers():
            if layer.name() == name:
                return layer

    def editInLayer(self, name):
        layer = self.getLayerByName(name)
        if layer:
            self.main.iface.setActiveLayer(layer)
            self.main.iface.actionToggleEditing().trigger()
            self.main.iface.actionAddFeature().trigger()

    def stopEditInLayer(self, name):
        layer = self.getLayerByName(name)
        if layer:
            layer.commitChanges()
            layer.endEditCommand()

    def toggleLayersGroups(self, enable, disable):
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
