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

        self.values = []

    def setValues(self, values):
        self.values = ['']
        self.values.extend(values)
        self.clear()
        self.addItems(self.values)

    def setValue(self, value):
        if value and value in self.values:
            self.setCurrentIndex(self.values.index(value))
        else:
            self.setCurrentIndex(0)

    def getValue(self):
        if self.currentText():
            return self.currentText()
        return None
