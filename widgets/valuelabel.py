# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

class ValueLabel(QLabel):
    def setText(self, text):
        if text:
            QLabel.setText(self, text)
        else:
            self.clear()

class AutohideValueLabel(ValueLabel):
    def setText(self, text):
        ValueLabel.setText(self, text)
        if text:
            self.show()

    def clear(self):
        self.hide()
        ValueLabel.clear(self)

    def hide(self):
        if self.buddy():
            self.buddy().hide()
        ValueLabel.hide(self)

    def show(self):
        if self.buddy():
            self.buddy().show()
        ValueLabel.show(self)
