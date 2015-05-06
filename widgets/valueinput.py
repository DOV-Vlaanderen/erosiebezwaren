# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

class DefaultValueDateEdit(QDateEdit):
    def __init__(self, parent, defaultDate=QDate.currentDate()):
        QDateEdit.__init__(self, parent)
        self.setDate(defaultDate)
        self.format = 'dd/MM/yyyy'

    def setValue(self, date):
        if date:
            self.setDate(QDate.fromString(date, self.format))
        else:
            self.setDate(QDate.currentDate())

    def getValue(self):
        return self.date().toString(self.format)

class ValueLineEdit(QLineEdit):
    def setText(self, text):
        if text:
            QLineEdit.setText(self, text)
        else:
            self.clear()

class ValueComboBox(QComboBox):
    def __init__(self, parent):
        QComboBox.__init__(self, parent)
        self.initialValues = ['']
        self.values = []

    def setValues(self, values):
        self.values = self.initialValues
        self.values.extend(values)
        self.clear()
        self.addItems(self.values)

    def setValue(self, value):
        if value and value in self.values:
            self.setCurrentIndex(self.values.index(value))
        else:
            self.setCurrentIndex(-1)

    def getValue(self):
        if self.currentText():
            return self.currentText()
        return None

class ValueMappedComboBox(QComboBox):
    def __init__(self, parent):
        QComboBox.__init__(self, parent)
        self.values = []
        self.textValueMap = {}
        self.valueTextMap = {}

    def setValues(self, values):
        self.textValueMap = {}
        self.valueTextMap = {}
        newValues = [('', None)]
        newValues.extend(values)
        self.clear()
        for v in newValues:
            self.addItem(v[0])
            self.values.append(v[0])
            self.textValueMap[v[0]] = v[1]
            self.valueTextMap[v[1]] = v[0]

    def setValue(self, value):
        if value in self.valueTextMap:
            self.setCurrentIndex(self.values.index(self.valueTextMap[value]))
        else:
            self.setCurrentIndex(0)

    def getValue(self):
        if self.currentText() in self.textValueMap:
            return self.textValueMap[self.currentText()]
        return None
