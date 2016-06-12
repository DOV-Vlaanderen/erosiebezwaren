# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_monitoringwidget import Ui_MonitoringWidget
from widgets.monitoringwidgets import BasisPakketWidget, BufferStrookHellingWidget, TeeltTechnischWidget
from widgets.elevatedfeaturewidget import ElevatedFeatureWidget
from widgets.valueinput import ValueComboBox, ValueTextEdit

class MonitoringWidget(ElevatedFeatureWidget, Ui_MonitoringWidget):
    def __init__(self, parent, main, feature, layer):
        ElevatedFeatureWidget.__init__(self, parent)
        self.main = main
        self.feature = feature
        self.layer = layer
        self.setupUi(self)

        QObject.connect(self.btn_save, SIGNAL('clicked()'), self.save)
        QObject.connect(self.btn_cancel, SIGNAL('clicked()'), self.stop)

        self.lbv_header.setText('Bewerk monitoring voor perceel %s\n  van %s' % (self.feature.attribute('uniek_id'), self.feature.attribute('naam')))

        self.efw_basispakket = BasisPakketWidget(self)
        self.efw_basispakket.setGeenMtrglEnabled(self.feature.attribute('landbouwer_aanwezig') == 1)
        self.lyt_basispakket.addWidget(self.efw_basispakket)

        self.efw_bufferstrook_helling = BufferStrookHellingWidget(self)
        self.lyt_bufferstrook.addWidget(self.efw_bufferstrook_helling)

        self.efw_bufferstrook_mtrgl = ValueComboBox(self)
        self.efw_bufferstrook_mtrgl.initialValues = []
        self.efw_bufferstrook_mtrgl.setValues([
            'Standaardinvulling',
            'Attest',
            'Onvoldoende invulling',
            'Geen maatregel',
            'Geen info'
        ])
        self.lyt_bufferstrook.addWidget(self.efw_bufferstrook_mtrgl)

        self.efw_teelttechnisch = TeeltTechnischWidget(self)
        self.lyt_teelttechnisch.addWidget(self.efw_teelttechnisch)

        self.populate()
        self.connectValidators()

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

    def connectValidators(self):
        QObject.connect(self.efw_basispakket, SIGNAL('valueChanged()'), self._validate)
        QObject.connect(self.efw_bufferstrook_helling, SIGNAL('valueChanged()'), self._validate)
        QObject.connect(self.efw_bufferstrook_mtrgl, SIGNAL('valueChanged()'), self._validate)
        QObject.connect(self.efw_teelttechnisch, SIGNAL('valueChanged()'), self._validate)
        self._validate()

    def _validate(self, *args):
        disabledOptions = set()

        if 'voor_groen' not in self.efw_basispakket.getValue():
            disabledOptions |= set(['directinzaai', 'strip-till'])

        if 'voor_ploegen' in self.efw_basispakket.getValue():
            disabledOptions |= set(['nietkerend', 'directinzaai', 'strip-till'])

        self.efw_teelttechnisch.setDisabledOptions(disabledOptions)

        self._checkSaveable()

    def _checkSaveable(self, *args):
        self.btn_save.setEnabled(self._isSaveable())

    def _isSaveable(self):
        return \
            len(set([i.strip().split('_')[0] for i in self.efw_basispakket.getValue().split(';')])) == 2 and \
            self.efw_bufferstrook_helling.getValue() != None and \
            self.efw_bufferstrook_mtrgl.getValue() != None and \
            self.efw_teelttechnisch.getValue() != ''

class MonitoringWindow(QMainWindow):
    closed = pyqtSignal()

    def __init__(self, main, feature, layer):
        QMainWindow.__init__(self, main.iface.mainWindow())
        self.main = main
        self.feature = feature
        self.layer = layer

        self.setWindowTitle('Bewerk monitoring %s' % self.feature.attribute('uniek_id'))

        self.monitoringWidget = MonitoringWidget(self, self.main, self.feature, self.layer)
        self.setCentralWidget(self.monitoringWidget)

        self.setMinimumSize(800, 800)

    def closeEvent(self, event):
        self.closed.emit()
