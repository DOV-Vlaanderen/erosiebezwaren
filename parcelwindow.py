# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_parceleditwidget import Ui_ParcelEditWidget
from widgets.elevatedfeaturewidget import ElevatedFeatureWidget

from parceleditwindow.ui_header import Ui_Header
from parceleditwindow.ui_quickedit import Ui_QuickEdit
from parceleditwindow.ui_detailsparcel import Ui_DetailsParcel
from parceleditwindow.ui_detailsfarmer import Ui_DetailsFarmer
from parceleditwindow.ui_detailsobjection import Ui_DetailsObjection

class Header(ElevatedFeatureWidget, Ui_Header):
    def __init__(self, parent, main, parcel=None):
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.main = main
        self.setupUi(self)

        QObject.connect(self.btn_minimize, SIGNAL('clicked()'), self.minimize)

        if parcel:
            self.populate()

    def minimize(self):
        self.parent.parent.showMinimized()
        #self.main.parcelInfoWidget.populateEditButton()

class QuickEdit(ElevatedFeatureWidget, Ui_QuickEdit):
    def __init__(self, parent, main, parcel=None):
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.main = main
        self.setupUi(self)

        self.efwCmb_advies_behandeld.initialValues = []
        self.efwCmb_advies_behandeld.setValues([
            'Te behandelen',
            'Veldcontrole gebeurd',
            'Afgehandeld ALBON'
        ])

        self.efwCmb_advies_aanvaarding.setValues([
            ('Aanvaard', 1),
            ('Niet aanvaard', 0)
        ])

        self.efwCmb_gewas_veldbezoek.setSource(
            self.main.utils.getLayerByName('bezwarenkaart'),
            'gewas_veldbezoek')

        self.efwCmb_advies_aanvaarding.setEnabled(self.feature.attribute('datum_bezwaar') != None)

        QObject.connect(self.btn_setToday, SIGNAL('clicked(bool)'), self.setToday)
        QObject.connect(self.btn_setLastEditor, SIGNAL('clicked(bool)'), self.setLastEditor)

        if parcel:
            self.populate()

    def setToday(self):
        self.efw_datum_veldbezoek.setDate(QDate.currentDate())

    def setLastEditor(self):
        lastEditor = self.main.qsettings.value('/Qgis/plugins/Erosiebezwaren/editor')
        if type(lastEditor) in [str, unicode]:
            self.efw_veldcontrole_door.setText(lastEditor)

class DetailsParcel(ElevatedFeatureWidget, Ui_DetailsParcel):
    def __init__(self, parent, main, parcel=None):
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.setupUi(self)

        if parcel:
            self.populate()

class DetailsObjection(ElevatedFeatureWidget, Ui_DetailsObjection):
    def __init__(self, parent, main, parcel=None):
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.setupUi(self)

        if parcel:
            self.populate()

class DetailsFarmer(ElevatedFeatureWidget, Ui_DetailsFarmer):
    def __init__(self, parent, main, parcel=None):
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.setupUi(self)

        if parcel:
            self.populate()

class ParcelEditWidget(ElevatedFeatureWidget, Ui_ParcelEditWidget):
    def __init__(self, parent, main, layer, writeLayer, parcel):
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.main = main
        self.layer = layer
        self.writeLayer = writeLayer
        self.setupUi(self)
        self.widgets = [self]

        self.header = Header(self, self.main, self.feature)
        self.widgets.append(self.header)
        self.verticalLayout.insertWidget(0, self.header)

        self.quickedit = QuickEdit(self, self.main, self.feature)
        self.widgets.append(self.quickedit)
        self.verticalLayout_3.insertWidget(0, self.quickedit)

        self.efwEdt_observaties_watererosie.setTitle('Observaties watererosie')
        self.efwEdt_observaties_bewerkingserosie.setTitle('Observaties bewerkingserosie')
        self.efwEdt_andere_observaties.setTitle('Andere observaties')
        self.efwEdt_opmerkingen_veldbezoek.setTitle('Opmerkingen veldbezoek')

        self.detailsObjection = DetailsObjection(self, self.main, self.feature)
        self.detailsFarmer = DetailsFarmer(self, self.main, self.feature)
        self.detailsParcel = DetailsParcel(self, self.main, self.feature)
        self.widgets.extend([self.detailsObjection, self.detailsFarmer, self.detailsParcel])
        self.verticalLayout_4.addWidget(self.detailsParcel)
        self.verticalLayout_4.addWidget(self.detailsObjection)
        self.verticalLayout_5.addWidget(self.detailsFarmer)

        for w in self.widgets:
            w.setLayer(self.layer)

        QObject.connect(self.btn_save, SIGNAL('clicked()'), self.save)
        QObject.connect(self.btn_cancel, SIGNAL('clicked()'), self.cancel)
 
        self.populate()

    def save(self):
        layer = self.layer
        if self.writeLayer and self.writeLayer != self.layer:
            layer = self.writeLayer
            success, addedFeatures = self.writeLayer.dataProvider().addFeatures([self.feature])
            if success:
                for w in self.widgets:
                    w.feature = addedFeatures[0]
                    w.layer = self.writeLayer
                    w._mapWidgets(w.feature.fields())
            else:
                # this shouldn't happen: failed to copy feature
                # return here so we don't save it in the wrong layer
                return

        attrMap = {}
        for w in self.widgets:
            attrMap.update(w._getAttrMap())
        success = self.saveFeature(attrMap)

        if not success:
            return

        editor = self.quickedit.efw_veldcontrole_door.text()
        if editor:
            self.main.qsettings.setValue('/Qgis/plugins/Erosiebezwaren/editor', editor)
        self.main.iface.mapCanvas().refresh()
        self.parent.saved.emit(layer, self.feature)
        self.parent.close()

    def cancel(self):
        self.parent.close()

class ParcelWindow(QMainWindow):
    saved = pyqtSignal('QgsVectorLayer', 'QgsFeature')
    closed = pyqtSignal()
    windowStateChanged = pyqtSignal()

    def __init__(self, main, layer, writeLayer, parcel):
        QMainWindow.__init__(self, main.iface.mainWindow())
        self.main = main
        self.layer = layer
        self.writeLayer = writeLayer
        self.parcel = parcel

        self.parcelEditWidget = ParcelEditWidget(self, self.main, self.layer, self.writeLayer, self.parcel)
        self.setCentralWidget(self.parcelEditWidget)
        self.setWindowTitle("Behandel perceel")

    def closeEvent(self, event):
        self.closed.emit()

    def changeEvent(self, event):
        if type(event) is QWindowStateChangeEvent:
            self.windowStateChanged.emit()
