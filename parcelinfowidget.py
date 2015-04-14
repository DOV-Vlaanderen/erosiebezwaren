# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_parcelinfowidget import Ui_ParcelInfoWidget

class ParcelInfoWidget(QWidget, Ui_ParcelInfoWidget):
    def __init__(self, parent, parcel=None):
        QWidget.__init__(self, parent)
        self.parcel = parcel
        self.setupUi(self)
        self.populate()

    def populate(self):
        if self.parcel:
            self.toolBox.show()
            self.lb_id.setText(self.parcel.attribute('obj_id'))
            self.lb_gps.setText('GPS: ')
        else:
            self.clear()

    def clear(self):
        self.lb_id.setText("Geen selectie")
        self.lb_gps.clear()
        self.toolBox.hide()

    def setParcel(self, parcel):
        if parcel != self.parcel:
            self.parcel = parcel
            self.populate()

class ParcelInfoDock(QDockWidget):
    def __init__(self, parent):
        QDockWidget.__init__(self, "Perceelsinformatie", parent)
        self.setObjectName("Perceelsinformatie")
        parent.addDockWidget(Qt.RightDockWidgetArea, self)

        QObject.connect(self, SIGNAL('topLevelChanged(bool)'), self.resizeToMinimum)

    def resizeToMinimum(self):
        self.resize(self.minimumSize())

    def toggleVisibility(self):
        self.setVisible(not self.isVisible())
