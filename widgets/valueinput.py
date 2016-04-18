# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

class ValueDateEdit(QDateEdit):
    def __init__(self, parent):
        QDateEdit.__init__(self, parent)
        self.format = 'dd/MM/yyyy'

    def setValue(self, date):
        if date:
            self.setDate(QDate.fromString(date, self.format))
        else:
            self.clear()

    def getValue(self):
        return self.date().toString(self.format)

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

class ValueCheckBox(QCheckBox):
    def setValue(self, value):
        self.setChecked(value == 1)

    def getValue(self):
        if self.isChecked():
            return 1
        return 0

class ValueBooleanButton(QPushButton):
    def __init__(self, parent):
        QPushButton.__init__(self, parent)
        self.setContentsMargins(4, 4, 4, 4)
        self.setMinimumHeight(32)
        self.setCheckable(True)
        self.text = None
        self.__setStyleSheet()
        QObject.connect(self, SIGNAL('clicked()'), self.__updateValue)

    def setText(self, text):
        if not self.text:
            self.text = text
        QPushButton.setText(self, self.text)

    def setValue(self, value):
        if value == 1:
            QPushButton.setText(self, self.text + ': Ja')
            self.setChecked(True)
        else:
            QPushButton.setText(self, self.text + ': Nee')
            self.setChecked(False)

    def getValue(self):
        if self.isChecked():
            return 1
        return 0

    def __updateValue(self):
        if self.isChecked():
            self.setValue(1)
        else:
            self.setValue(0)

    def __setStyleSheet(self):
        style = "QPushButton {"
        style += "border: 2px solid white;"
        style += "border-radius: 4px;"
        style += "padding: 2px;"
        style += "background-color: #C6C6C6;"
        style += "color: #000000;"
        style += "}"

        style += "QPushButton:checked {"
        style += "background-color: #CBE195;"
        style += "color: #000000;"
        style += "}"

        style += "QPushButton:disabled {"
        style += "color: #909090;"
        style += "}"
        self.setStyleSheet(style)

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

class ValueTextEdit(QPlainTextEdit):
    def __init__(self, parent):
        QPlainTextEdit.__init__(self, parent)

    def setValue(self, value):
        if value:
            self.setPlainText(value)
        else:
            self.clear()

    def getValue(self):
        return self.toPlainText()
