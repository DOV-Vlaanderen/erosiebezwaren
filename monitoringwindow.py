# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_monitoringwidget import Ui_MonitoringWidget
from widgets.monitoringwidgets import BasisPakketWidget, BufferStrookHellingWidget
from widgets.elevatedfeaturewidget import ElevatedFeatureWidget

class MonitoringWidget(ElevatedFeatureWidget, Ui_MonitoringWidget):
    def __init__(self, parent, main, feature, layer):
        ElevatedFeatureWidget.__init__(self, parent)
        self.main = main
        self.feature = feature
        self.layer = layer
        self.setupUi(self)

        QObject.connect(self.btn_save, SIGNAL('clicked()'), self.save)
        QObject.connect(self.btn_cancel, SIGNAL('clicked()'), self.stop)

        self.efw_basispakket = BasisPakketWidget(self)
        self.lyt_basispakket.addWidget(self.efw_basispakket)

        self.bufferStrookHellingWidget = BufferStrookHellingWidget(self)
        self.lyt_bufferstrook.addWidget(self.bufferStrookHellingWidget)

        self.populate()

    def save(self):
        if self.feature:
            success = self.saveFeature()
            if success:
                self.stop()

    def stop(self):
        self.btn_save.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        QCoreApplication.processEvents()
        self.btn_save.repaint()
        self.btn_cancel.repaint()
        self.parent.close()

class MonitoringWindow(QMainWindow):
    closed = pyqtSignal()

    def __init__(self, main, feature, layer):
        QMainWindow.__init__(self, main.iface.mainWindow())
        self.main = main
        self.feature = feature
        self.layer = layer

        self.monitoringWidget = MonitoringWidget(self, self.main, self.feature, self.layer)
        self.setCentralWidget(self.monitoringWidget)

        self.setMinimumSize(1200, 1000)

    def closeEvent(self, event):
        self.closed.emit()
