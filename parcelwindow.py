# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_parceleditwidget import Ui_ParcelEditWidget
from widgets.elevatedfeaturewidget import ElevatedFeatureWidget

class ParcelEditWidget(ElevatedFeatureWidget, Ui_ParcelEditWidget):
    def __init__(self, parent, main, layer, parcel):
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.main = main
        self.layer = layer
        self.setupUi(self)

        self.efwCmb_advies_behandeld.initialValues = []
        self.efwCmb_advies_behandeld.setValues([
            'Te behandelen',
            'Veldcontrole gebeurd',
            'Conform eerder advies',
            'Beslist zonder veldcontrole',
            'Herberekening afwachten'
        ])

        self.efwCmb_advies_aanvaarding.setValues([
            ('Aanvaard', 1),
            ('Niet aanvaard', 0)
        ])

        self.efwCmb_veldcontrole_door.initialValues = []
        self.efwCmb_veldcontrole_door.setValues([
            'Jan Vermang',
            'Martien Swerts',
            'Petra Deproost',
            'Joost Salomez',
            'Liesbeth Vandekerckhove',
            'Katrien Oorts'
        ])

        self.efwCmb_advies_aanvaarding.setEnabled(self.feature.attribute('datum_bezwaar') != None)

        QObject.connect(self.btn_setToday, SIGNAL('clicked(bool)'), self.setToday)
        QObject.connect(self.btn_minimize, SIGNAL('clicked()'), self.minimize)
        QObject.connect(self.btn_save, SIGNAL('clicked()'), self.save)
        QObject.connect(self.btn_cancel, SIGNAL('clicked()'), self.cancel)
 
        self.populate()

    def minimize(self):
        self.parent.showMinimized()

    def stop(self):
        self.btn_save.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        QCoreApplication.processEvents()
        self.btn_save.repaint()
        self.btn_cancel.repaint()

    def save(self):
        success = self.saveFeature()

        if not success:
            return

        editor = self.efwCmb_veldcontrole_door.getValue()
        if editor and (editor != self.initialEditor):
            self.main.qsettings.setValue('/Qgis/plugins/Erosiebezwaren/editor', editor)
        self.main.iface.mapCanvas().refresh()
        self.stop()
        self.parent.saved.emit(self.layer, self.feature.attribute('uniek_id'))
        self.parent.close()

    def cancel(self):
        self.stop()
        self.parent.close()

    def setToday(self):
        self.efw_datum_veldbezoek.setDate(QDate.currentDate())

    def populate(self):
        ElevatedFeatureWidget.populate(self)
        self.lbv_header.setText('Bewerk advies voor perceel %s\n  van %s' % (self.feature.attribute('uniek_id'), self.feature.attribute('naam')))
        self.parent.setWindowTitle('Bewerk advies %s' % self.feature.attribute('uniek_id'))

        if not self.efwCmb_veldcontrole_door.getValue():
            self.efwCmb_veldcontrole_door.setValue(self.main.qsettings.value('/Qgis/plugins/Erosiebezwaren/editor', None))

        self.initialEditor = self.efwCmb_veldcontrole_door.getValue()

class ParcelWindow(QMainWindow):
    saved = pyqtSignal('QgsVectorLayer', 'QString')
    closed = pyqtSignal()
    windowStateChanged = pyqtSignal()

    def __init__(self, main, layer, parcel):
        QMainWindow.__init__(self, main.iface.mainWindow())
        self.main = main
        self.layer = layer
        self.parcel = parcel

        self.parcelEditWidget = ParcelEditWidget(self, self.main, self.layer, self.parcel)
        self.setCentralWidget(self.parcelEditWidget)

    def closeEvent(self, event):
        self.parcelEditWidget.stop()
        self.closed.emit()

    def changeEvent(self, event):
        if type(event) is QWindowStateChangeEvent:
            self.windowStateChanged.emit()
