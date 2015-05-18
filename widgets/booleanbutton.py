# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

class BooleanButton(QPushButton):
    def __init__(self, parent, initialState=None):
        self.state = initialState
        QPushButton.__init__(self, parent)
        self.setCheckable(True)
        self.stringDict = {True: 'Ja', False: 'Nee', None: ''}
        self.__update()

        QObject.connect(self, SIGNAL('toggled(bool)'), self.setState)

    def setState(self, state):
        if state != self.state:
            self.state = state
            self.__update()

    def __update(self):
        if self.state:
            self.setChecked(True)
        else:
            self.setChecked(False)
        self.setText(self.stringDict[self.state])
