# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_parcelwindow import Ui_ParcelWindow
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
        self.setupUi(self)

        if parcel:
            self.populate()

class QuickEdit(ElevatedFeatureWidget, Ui_QuickEdit):
    def __init__(self, parent, main, parcel=None):
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.setupUi(self)

        if parcel:
            self.populate()

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
    def __init__(self, parent, main, layer=None, parcel=None):
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.main = main
        self.layer = layer
        self.setupUi(self)

        self.header = Header(self, self.main, self.feature)
        self.verticalLayout.insertWidget(0, self.header)

        self.quickedit = QuickEdit(self, self.main, self.feature)
        self.quickedit.efwCmb_gewas.setSource(self.layer, 'erosie_tot')
        self.verticalLayout_3.insertWidget(0, self.quickedit)

        self.edt_watererosie.setTitle('Observaties watererosie')
        self.edt_bewerkingserosie.setTitle('Observaties bewerkingserosie')
        self.edt_andereobs.setTitle('Andere observaties')
        self.edt_opmerkingen.setTitle('Opmerkingen veldbezoek')

        self.detailsObjection = DetailsObjection(self, self.main, self.feature)
        self.detailsFarmer = DetailsFarmer(self, self.main, self.feature)
        self.detailsParcel = DetailsParcel(self, self.main, self.feature)
        self.verticalLayout_4.addWidget(self.detailsObjection)
        self.verticalLayout_4.addWidget(self.detailsFarmer)
        self.verticalLayout_5.addWidget(self.detailsParcel)

        QObject.connect(self.btn_save, SIGNAL('clicked()'), self.save)
        QObject.connect(self.btn_cancel, SIGNAL('clicked()'), self.cancel)
 
        self.populate()

    def save(self):
        self.saveFeature()
        self.parent.close()

    def cancel(self):
        self.parent.close()

class ParcelWindow(QMainWindow):
    def __init__(self, main, layer, parcel):
        QMainWindow.__init__(self, main.iface.mainWindow())
        self.main = main
        self.layer = layer
        self.parcel = parcel

        self.parcelEditWidget = ParcelEditWidget(self, self.main, self.layer, self.parcel)
        self.setCentralWidget(self.parcelEditWidget)
        self.setWindowTitle("Behandel perceel")

        #self.led_gewas.setText(self.parcel.attribute('klasse_VA'))
        #self.btn_advBehandeld.setState(self.parcel.attribute('aanpassing')=='A')

        #gewasModel = AttributeModel(self.cmb_gewasBezoek, self.layer, 'klasse_VA')
        #self.cmb_gewasBezoek.setModel(gewasModel)  

    #def resizeEvent(self, event):
    #    self.label_3.setText("%ix%i" % (event.size().width(), event.size().height()))
