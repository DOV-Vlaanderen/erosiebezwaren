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
