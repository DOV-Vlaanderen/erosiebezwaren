# -*- coding: utf-8 -*-
"""Module containing the ElevatedFeatureWidget class."""

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

import PyQt4.QtGui as QtGui

import re
import uuid

from attributecombobox import AttributeFilledCombobox
from monitoringwidgets import MonitoringItemWidget
from sensitivitybuttonbox import SensitivityButtonBox
from valueinput import DefaultValueDateEdit
from valueinput import ValueBooleanButton
from valueinput import ValueCheckBox
from valueinput import ValueComboBox
from valueinput import ValueMappedComboBox
from valueinput import ValueTextEdit
from valuelabel import EnabledBooleanButton
from valuelabel import EnabledFlatBooleanButton
from valuelabel import VisibilityBooleanButton


def _s(widget, parentclass):
    """Check if the widget is a subclass of the given parent class.

    Parameters
    ----------
    widget : Object
        Instance to check.
    parentclass : class
        Check if type(widget) is a subclass of this class.

    Returns
    -------
    boolean
        'True' if the type of the widget is a subclass of the parentclass,
        'False' otherwise.

    """
    return issubclass(type(widget), parentclass)


class ElevatedFeatureWidget(QtGui.QWidget):
    """Class that maps a widget to a feature.

    This allows automatic mapping of subwidgets to fields of the feature. Which
    allows the values of the subwidgets to be set to the values of the
    corresponding fields of the widget on initialisation. It also allows the
    values of the fields of the feature to be updated to the values of the
    corresponding widgets upon saving.

    For it to work, the names (variables) of the subwidgets of this widget must
    start with 'efw' and end with '_fieldname' where fieldname should be
    replaced with the name of the attribute field of the feature. Note that
    you can map multiple widgets to one attribute.
    """

    UNDEFINED = str(uuid.uuid4())

    def __init__(self, parent, feature=None):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget of this widget.
        feature : QGisCore.QgsFeature, optional
            The subwidgets of this widget will be mapped to the attributes of
            this feature.

        """
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.layer = None
        self.feature = feature
        self.fieldMap = {}

    def _setValue(self, widget, value):
        """Set the value of a certain widget to the given value.

        Parameters
        ----------
        widget : QtGui.QWidget
            The widget to set the value of.
        value : str or int or float
            The value to set. This value is passed as parameter of the setText
            or setValue functions of the widget.

        """
        fnSetValue = None

        if _s(widget, QtGui.QLabel) or \
           _s(widget, QtGui.QLineEdit):
            fnSetValue = widget.setText
        elif _s(widget, EnabledBooleanButton) or \
                _s(widget, EnabledFlatBooleanButton) or \
                _s(widget, VisibilityBooleanButton) or \
                _s(widget, SensitivityButtonBox) or \
                _s(widget, DefaultValueDateEdit) or \
                _s(widget, ValueCheckBox) or \
                _s(widget, AttributeFilledCombobox) or \
                _s(widget, ValueComboBox) or \
                _s(widget, ValueBooleanButton) or \
                _s(widget, ValueMappedComboBox) or \
                _s(widget, ValueTextEdit) or \
                _s(widget, MonitoringItemWidget):
            fnSetValue = widget.setValue

        if fnSetValue:
            fnSetValue(value)

    def _getValue(self, widget):
        """Get the value of the given widget.

        Parameters
        ----------
        widget : QtGui.QWidget
            The widget to get the value of.

        Returns
        -------
        str or int or float
            The value of the widget. This is the result of the text() or
            getValue() functions of the widget.
            Returns the ElevatedFeatureWidget.UNDEFINED constant if the widget
            is not a known widget.

        """
        fnGetValue = None

        if _s(widget, QtGui.QLineEdit):
            fnGetValue = widget.text
        elif _s(widget, SensitivityButtonBox) or \
                _s(widget, DefaultValueDateEdit) or \
                _s(widget, ValueCheckBox) or \
                _s(widget, AttributeFilledCombobox) or \
                _s(widget, ValueComboBox) or \
                _s(widget, ValueBooleanButton) or \
                _s(widget, ValueMappedComboBox) or \
                _s(widget, ValueTextEdit) or \
                _s(widget, MonitoringItemWidget):
            fnGetValue = widget.getValue

        if fnGetValue:
            return fnGetValue()
        return ElevatedFeatureWidget.UNDEFINED

    def _mapWidgets(self, fields):
        """Build the mapping between the subwidgets and the fields.

        Parameters
        ----------
        fields : QGisCore.QgsFields
            The attribute fields of the feature to use for mapping.

        """
        self.fieldMap = {}

        for dictfield in self.__dict__:
            if re.match(r'^efw[^_]*_.*$', dictfield):
                self.__dict__[dictfield].mapped = False

        for i in range(fields.size()):
            field = fields.at(i)
            field.index = i
            regex = re.compile(r'^efw[^_]*_%s$' % field.name(), re.I)
            for dictfield in self.__dict__:
                if regex.match(dictfield):
                    if field not in self.fieldMap:
                        self.fieldMap[field] = set()
                    self.fieldMap[field].add(self.__dict__[dictfield])
                    self.__dict__[dictfield].mapped = True

        for dictfield in self.__dict__:
            if re.match(r'^efw[^_]*_.*$', dictfield):
                if not self.__dict__[dictfield].mapped:
                    try:
                        self.__dict__[dictfield].hide()
                    except AttributeError:
                        continue

    def _getField(self, name):
        """Get the field with a given name.

        Parameters
        ----------
        name : str
            The name of the field.

        Returns
        -------
        QgisCore.QgsField
            The field with the given name.

        """
        for field in self.fieldMap:
            if field.name() == name:
                return field

    def populate(self):
        """Populate the subwidget.

        Set the values of the subwidgets to the values of the corresponding
        attributes of the feature.
        """
        if self.feature:
            if len(self.fieldMap) < 1:
                self._mapWidgets(self.feature.fields())

            for field in self.feature.fields():
                widgets = self.fieldMap.get(self._getField(field.name()), [])
                for w in widgets:
                    self._setValue(w, self.feature.attribute(field.name()))

    def setLayer(self, layer):
        """Set the layer to be used to save the feature.

        Parameters
        ----------
        layer : QGisCore.QgsVectorLayer
            The layer to be used to save to feature to.

        """
        if layer != self.layer:
            self.layer = layer

    def setFeature(self, feature):
        """Set the feature and populate the subwidgets.

        Parameters
        ----------
        feature : QgisCore.QgsFeature
            The feature to use.

        """
        self.feature = feature
        self.populate()

    def _getAttrMap(self):
        """Get the map with the new attribute values of the feature.

        Build the map with the new attribute values of the feature baes of the
        values of the corresponding subwidgets.

        Returns
        -------
        dict
            Attribute map mapping the indexes of the fields to their new value.

        """
        attrMap = {}
        for field in self.fieldMap:
            for widget in self.fieldMap[field]:
                value = self._getValue(widget)
                if value != ElevatedFeatureWidget.UNDEFINED:
                    self.feature.setAttribute(field.name(), value)
                    attrMap[field.index] = value
        return attrMap

    def saveFeature(self, attrMap=None):
        """Save the new values of the feature to the layer set by setLayer.

        Parameters
        ----------
        attrMap : dict, optional
            Attribute map mapping the indexes of the field to their new value.
            If missing, it will be built by calling _getAttrMap.

        Returns
        -------
        boolean
            True if the save was successful, False otherwise.

        """
        if not self.feature:
            return

        if not attrMap:
            attrMap = self._getAttrMap()

        r = self.layer.dataProvider().changeAttributeValues(
            {self.feature.id(): attrMap})
        return r
