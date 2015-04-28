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

        if fnGetValue:
            return fnGetValue()

    def _mapWidgets(self, fields):
        for field in fields:
            fieldName = field.name()
            regex = re.compile(r'^efw[^_]*_%s$' % fieldName, re.I)
            for dictfield in self.__dict__:
                if regex.match(dictfield):
                    if fieldName not in self.fieldMap:
                        self.fieldMap[fieldName] = set()
                    self.fieldMap[fieldName].add(self.__dict__[dictfield])

    def populate(self):
        if self.feature:
            if len(self.fieldMap) < 1:
                self._mapWidgets(self.feature.fields())

            for field in self.feature.fields():
                widgets = self.fieldMap.get(field.name(), [])
                for w in widgets:
                    self._setValue(w, self.feature.attribute(field.name()))

    def setFeature(self, feature):
        self.feature = feature
        self.populate()

    def saveFeature(self):
        if not self.feature:
            return

        for field in self.fieldMap:
            value = self._getValue(self.fieldMap[field])
            if value:
                self.feature.setAttribute(field, value)
