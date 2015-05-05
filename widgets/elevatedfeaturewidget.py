# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import re
import uuid

from valuelabel import EnabledBooleanButton
from sensitivitybuttonbox import SensitivityButtonBox
from valueinput import DefaultValueDateEdit, ValueComboBox
from attributecombobox import AttributeFilledCombobox
from titledtextedit import TitledTextEdit

def _s(widget, parentclass):
    return issubclass(type(widget), parentclass)

class ElevatedFeatureWidget(QWidget):
    UNDEFINED = str(uuid.uuid4())

    def __init__(self, parent, feature=None):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.layer = None
        self.feature = feature
        self.fieldMap = {}

    def _setValue(self, widget, value):
        fnSetValue = None

        if _s(widget, QLabel) or \
           _s(widget, QLineEdit) or \
           _s(widget, TitledTextEdit):
            fnSetValue = widget.setText
        elif _s(widget, EnabledBooleanButton) or \
             _s(widget, SensitivityButtonBox) or \
             _s(widget, DefaultValueDateEdit) or \
             _s(widget, AttributeFilledCombobox) or \
             _s(widget, ValueComboBox):
            fnSetValue = widget.setValue

        if fnSetValue:
            fnSetValue(value)

    def _getValue(self, widget):
        fnGetValue = None

        if _s(widget, QLineEdit) or \
           _s(widget, TitledTextEdit):
            fnGetValue = widget.text
        elif _s(widget, SensitivityButtonBox) or \
             _s(widget, DefaultValueDateEdit) or \
             _s(widget, AttributeFilledCombobox) or \
             _s(widget, ValueComboBox):
            fnGetValue = widget.getValue

        if fnGetValue:
            return fnGetValue()
        return ElevatedFeatureWidget.UNDEFINED

    def _mapWidgets(self, fields):
        self.fieldMap = {}
        for i in range(fields.size()):
            field = fields.at(i)
            field.index = i
            regex = re.compile(r'^efw[^_]*_%s$' % field.name(), re.I)
            for dictfield in self.__dict__:
                if regex.match(dictfield):
                    if field not in self.fieldMap:
                        self.fieldMap[field] = set()
                    self.fieldMap[field].add(self.__dict__[dictfield])

    def _getField(self, name):
        for field in self.fieldMap:
            if field.name() == name:
                return field

    def populate(self):
        if self.feature:
            if len(self.fieldMap) < 1:
                self._mapWidgets(self.feature.fields())

            for field in self.feature.fields():
                widgets = self.fieldMap.get(self._getField(field.name()), [])
                for w in widgets:
                    self._setValue(w, self.feature.attribute(field.name()))

    def setLayer(self, layer):
        if layer != self.layer:
            self.layer = layer

    def setFeature(self, feature):
        self.feature = feature
        self.populate()

    def _saveFeature(self):
        if not self.feature:
            return

        attrMap = {}
        for field in self.fieldMap:
            for widget in self.fieldMap[field]:
                value = self._getValue(widget)
                if value != ElevatedFeatureWidget.UNDEFINED:
                    self.feature.setAttribute(field.name(), value)
                    attrMap[field.index] = value

        self.layer.dataProvider().changeAttributeValues({self.feature.id(): attrMap})

    def saveFeature(self):
        if not self.feature:
            return

        self.layer.beginEditCommand("Update perceel %s" % self.feature.attribute('uniek_id'))
        self._saveFeature()
        self.layer.commitChanges()
        self.layer.endEditCommand()
