# -*- coding: utf-8 -*-
"""Module for a combobox that gets its values from a Spatialite table.

Contains the AttributeModel, SpatialiteAttributeModel and
AttributeFilledCombobox classes.
"""

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

import threading

from Erosiebezwaren.qgsutils import SpatialiteIterator


class AttributeModel(QtCore.QAbstractListModel):
    """A list model based on attribute values of a layer."""

    def __init__(self, parent, layer, attributeName):
        """Initialise and get the distinct values from the layer.

        Parameters
        ----------
        parent : QtCore.QObject
            Parent object for the list model.
        layer : QGisCore.QgsVectorLayer
            Layer to get the attribute values from.
        attributeName : str
            Get the distinct values from the attribute with this name.

        """
        self.layer = layer
        self.attributeName = attributeName
        QtCore.QAbstractListModel.__init__(self, parent)
        self.updateValues()

    def updateValues(self):
        """Get the distinct values from attribute of the layer."""
        values = ['']  # FIXME
        for feature in self.layer.getFeatures():
            v = feature.attribute(self.attributeName)
            if v and v not in values:
                values.append(v)
        self.values = values

    def rowCount(self, parent):
        """Get the number of values in the model.

        Parameters
        ----------
        parent : QtCore.QModelIndex
            The parent QModelIndex.

        Returns
        -------
        int
            The number of values in the model.

        """
        return len(self.values)

    def data(self, index, role):
        """Get a specific item from the model.

        Parameters
        ----------
        index : QtCore.QModelIndex
            The model index locating the datavalue to get.
        role : int
            Codelist value specifying which role is to use the data. Defaults
            to Qt.DisplayRole.

        Returns
        -------
        QtCore.QVariant
            The value of the model at the requested location.

        """
        if index.row() < len(self.values):
            return self.values[index.row()]
        return QtCore.QVariant()


class SpatialiteAttributeModel(AttributeModel):
    """Subclass of the AttributeModel that gets the values from Spatialite."""

    def __init__(self, parent, layer, attributeName):
        """Initialise and get the distinct values from the layer.

        Parameters
        ----------
        parent : QtCore.QObject
            Parent object for the list model.
        layer : QGisCore.QgsVectorLayer
            Layer to get the attribute values from.
        attributeName : str
            Get the distinct values from the attribute with this name.

        """
        AttributeModel.__init__(self, parent, layer, attributeName)

    def updateValues(self):
        """Get the distinct values from attribute of the layer."""
        s = SpatialiteIterator(self.layer)
        sql = "SELECT DISTINCT %s FROM %s ORDER BY %s" % (self.attributeName,
                                                          s.ds.table(),
                                                          self.attributeName)
        self.values = ['']  # FIXME
        self.values.extend([i[0] for i in s.rawQuery(sql) if i[0]])


class AttributeFilledCombobox(QtGui.QComboBox):
    """Subclass of QComboBox that uses values from a layer attribute."""

    def __init__(self, parent, layer=None, attributename=None):
        """Initialise the QComboBox and set the source.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to be used as parent widget of this combobox.
        layer : QGisCore.QgsVectorLayer, optional
            Layer to get the attribute values from.
        attributeName : str, optional
            Get the distinct values from the attribute with this name.

        """
        QtGui.QComboBox.__init__(self, parent)
        self.setEditable(True)
        self.parent = parent
        self.layer = layer
        self.attributename = attributename
        self.t = None
        self.setSource(self.layer, self.attributename)

    def setSource(self, layer, attributename):
        """Set the source layer and attribute name for the datamodel.

        Set the type of model to SpatialiteAttributeModel if the dataprodivider
        is 'spatialite' and to AttributeModel otherwise.

        Parameters
        ----------
        layer : QGisCore.QgsVectorLayer
            Layer to get the attribute values from.
        attributeName : str
            Get the distinct values from the attribute with this name.

        """
        self.layer = layer
        self.attributename = attributename
        if not (self.layer and self.attributename):
            return

        if self.layer.dataProvider().name() == 'spatialite':
            model = SpatialiteAttributeModel(self.parent, self.layer,
                                             self.attributename)
        else:
            model = AttributeModel(self.parent, self.layer, self.attributename)
        self.setModel(model)

    def updateValues(self):
        """Update the values from the datamodel."""
        def prcs(cmb):
            cmb.model().updateValues()

        self.t = threading.Thread(target=prcs, args=(self,))
        self.t.start()

    def setValue(self, value):
        """Set the current value of the combobox.

        Parameters
        ----------
        value : str
            The new value for the combobox. Clear the value if 'None'.

        """
        if value:
            self.lineEdit().setText(value)
        else:
            self.lineEdit().clear()

    def getValue(self):
        """Return the current value of the combobox.

        Returns
        -------
        str
            The current value of the combobox.

        """
        return self.lineEdit().text()
