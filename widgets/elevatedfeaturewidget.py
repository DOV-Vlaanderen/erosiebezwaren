# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import re

from valuelabel import EnabledBooleanButton
from sensitivitybuttonbox import SensitivityButtonBox
from valueinput import DefaultValueDateEdit

def _s(widget, parentclass):
    return issubclass(type(widget), parentclass)

class ElevatedFeatureWidget(QWidget):
    def __init__(self, parent, feature=None):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.layer = None
        self.feature = feature
        self.fieldMap = {}

    def _setValue(self, widget, value):
        fnSetValue = None

        if _s(widget, QLabel) or \
           _s(widget, QLineEdit):
            fnSetValue = widget.setText
        elif _s(widget, EnabledBooleanButton) or \
             _s(widget, SensitivityButtonBox) or \
             _s(widget, DefaultValueDateEdit):
            fnSetValue = widget.setValue
        elif _s(widget, QComboBox):
            fnSetValue = widget.lineEdit().setText

        if fnSetValue:
            fnSetValue(value)

    def _getValue(self, widget):
        fnGetValue = None

        if _s(widget, QLineEdit):
            fnGetValue = widget.text
        elif _s(widget, SensitivityButtonBox) or \
             _s(widget, DefaultValueDateEdit):
            fnGetValue = widget.getValue
        elif _s(widget, QComboBox):
            fnGetValue = widget.lineEdit().text

        if fnGetValue:
            return fnGetValue()

    def _mapWidgets(self, fields):
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

    def saveFeature(self):
        if not self.feature:
            return

        if 'layer' not in self.feature.__dict__:
            return

        attrMap = {}
        for field in self.fieldMap:
            for widget in self.fieldMap[field]:
                value = self._getValue(widget)
                if value:
                    self.feature.setAttribute(field.name(), value)
                    attrMap[field.index] = value
        self.feature.layer.dataProvider().changeAttributeValues({self.feature.id(): attrMap})
