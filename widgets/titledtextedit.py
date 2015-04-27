# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_titledtextedit import Ui_TitledTextEdit

class TitledTextEdit(QWidget, Ui_TitledTextEdit):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        if title:
            self.lb_title.setText(title)
        else:
            self.lb_title.setText("")
            self.lb_title.hide()

    def title(self):
        return self.lb_title.text()

    def setText(self, text):
        self.plaintextedit.setPlainText(text)

    def text(self):
        return self.plaintextedit.toPlainText()
