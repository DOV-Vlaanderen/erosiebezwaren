# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

class SensitivityButton(QPushButton):
    def __init__(self, parent, value, label, bgcolor, textcolor):
        QPushButton.__init__(self, label, parent)
        self.value = value
        self.label = label
        self.bgcolor = bgcolor
        self.textcolor = textcolor
        self.parent = parent

        self.setContentsMargins(4, 4, 4, 4)
        self.setMinimumHeight(32)
        self.setCheckable(True)
        self.__setStyleSheet()

        QObject.connect(self, SIGNAL('clicked(bool)'), self.updateParent)

    def updateParent(self, checked):
        if checked:
            self.parent.setCheckedButton(self)
        else:
            self.parent.setUnchecked()

    def __setStyleSheet(self):
        style = "QPushButton {"
        style += "border: 2px solid white;"
        style += "border-radius: 4px;"
        style += "padding: 2px;"
        style += "background-color: #C6C6C6;"
        style += "color: #000000;"
        style += "}"

        style += "QPushButton:checked {"
        style += "background-color: %s;" % self.bgcolor
        style += "color: %s;" % self.textcolor
        style += "}"
        self.setStyleSheet(style)

class SensitivityButtonBox(QWidget):
    VERWAARLOOSBAAR, ZEERLAAG, LAAG, MEDIUM, HOOG, ZEERHOOG = range(6)
    valueChanged = pyqtSignal(str)

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.buttons = [SensitivityButton(self, 'verwaarloosbaar', 'Verwaarloosbaar', '#38a800', '#000000'),
                        SensitivityButton(self, 'zeer laag', 'Zeer laag', '#8ff041', '#000000'),
                        SensitivityButton(self, 'laag', 'Laag', '#ffff00', '#000000'),
                        SensitivityButton(self, 'medium', 'Medium', '#ffaa00', '#000000'),
                        SensitivityButton(self, 'hoog', 'Hoog', '#ff0000', '#ffffff'),
                        SensitivityButton(self, 'zeer hoog', 'Zeer hoog', '#a800e6', '#ffffff')]

        for i in range(len(self.buttons)):
            self.layout.addWidget(self.buttons[i], i/3, i%3)

    def setUnchecked(self):
        for btn in self.buttons:
            btn.setChecked(False)
        self.valueChanged.emit(None)

    def setCheckedButton(self, btn):
        for i in range(len(self.buttons)):
            if self.buttons[i] != btn:
                self.buttons[i].setChecked(False)
        self.valueChanged.emit(btn.value)

    def getCheckedButton(self):
        for btn in self.buttons:
            if btn.isChecked():
                return btn
        return None

    def getValue(self):
        btn = self.getCheckedButton()
        if btn:
            return btn.value
        return None

    def setValue(self, value):
        if value == None:
            self.setUnchecked()
        else:
            for btn in self.buttons:
                if btn.value == value:
                    btn.setChecked(True)
                    self.valueChanged.emit(value)
                    break
