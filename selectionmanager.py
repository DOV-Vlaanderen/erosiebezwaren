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

class SelectionManager(object):
    def __init__(self, main, tempLayerName):
        self.main = main
        self.utils = self.main.utils
        self.layerName = tempLayerName
        self.layer = None
        self.__getLayer()

    def __getLayer(self):
        if not self.layer:
            self.layer = self.utils.getLayerByName(self.layerName)
            if self.layer:
                self.layer.startEditing()
                self.layer.addAttribute(QgsField('mode', QVariant.Int, 'int', 1, 0))
                self.layer.addAttribute(QgsField('label', QVariant.String, 'string', 1, 0))
                self.layer.commitChanges()
                self.layer.endEditCommand()
        return self.layer

    def activate(self):
        if not self.__getLayer():
            return
        if not self.layer.isEditable():
            self.layer.startEditing()

    def deactivate(self):
        if not self.__getLayer():
            return

        if self.layer.isEditable():
            self.layer.commitChanges()
            self.layer.endEditCommand()

    def clear(self, toggleRendering=True):
        if not self.__getLayer():
            return
        self.main.iface.mapCanvas().setRenderFlag(False)
        self.layer.selectAll()
        self.layer.deleteSelectedFeatures()
        if toggleRendering:
            self.main.iface.mapCanvas().setRenderFlag(True)

    def selectGeometry(self, geometry, mode=0, label="", toggleRendering=True):
        if not self.__getLayer():
            return
        f = QgsFeature()
        f.fields().append(QgsField('mode', QVariant.Int, 'int', 1, 0))
        f.fields().append(QgsField('label', QVariant.String, 'string', 1, 0))
        f.setGeometry(geometry)
        f.setAttributes([mode, label])
        self.main.iface.mapCanvas().setRenderFlag(False)
        self.layer.addFeature(f)
        if toggleRendering:
            self.main.iface.mapCanvas().setRenderFlag(True)

    def select(self, feature, mode=0, label="", toggleRendering=True):
        self.selectGeometry(feature.geometry(), mode=mode, label=label, toggleRendering=toggleRendering)

    def clearWithMode(self, mode, toggleRendering=True):
        if not self.__getLayer():
            return
        self.main.iface.mapCanvas().setRenderFlag(False)
        for feature in self.layer.getFeatures(QgsFeatureRequest(QgsExpression('mode = %i' % mode))):
            self.layer.deleteFeature(feature.id())
        if toggleRendering:
            self.main.iface.mapCanvas().setRenderFlag(True)
