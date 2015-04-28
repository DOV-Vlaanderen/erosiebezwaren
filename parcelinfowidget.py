# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os
import re
import subprocess

from ui_parcelinfowidget import Ui_ParcelInfoWidget
from widgets import valuelabel
from widgets.elevatedfeaturewidget import ElevatedFeatureWidget
from parcelwindow import ParcelWindow
from photodialog import PhotoDialog
from parcellistdialog import ParcelListDialog

class ParcelInfoWidget(ElevatedFeatureWidget, Ui_ParcelInfoWidget):
    def __init__(self, parent, main, layer=None, parcel=None):
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.main = main
        self.layer = layer
        self.setupUi(self)

        QObject.connect(self.efwBtn_bezwaarformulier, SIGNAL('clicked(bool)'), self.showPdf_mock)
        QObject.connect(self.btn_edit, SIGNAL('clicked(bool)'), self.showEditWindow)
        QObject.connect(self.btn_zoomto, SIGNAL('clicked(bool)'), self.zoomTo)
        QObject.connect(self.btn_photo, SIGNAL('clicked(bool)'), self.takePhotos)
        QObject.connect(self.btn_anderePercelen, SIGNAL('clicked(bool)'), self.showParcelList)

        self.populate()

    def populate(self):
        ElevatedFeatureWidget.populate(self)
        if self.feature:
            self.showInfo()
            self.main.selectionManager.clearWithMode(mode=0, toggleRendering=False)
            self.main.selectionManager.select(self.feature, mode=0, toggleRendering=True)
        else:
            self.clear()

    def clear(self):
        self.lb_geenselectie.show()
        self.infoWidget.hide()
        self.main.selectionManager.clear()

    def showInfo(self):
        self.infoWidget.show()
        self.lb_geenselectie.hide()

    def showPdf(self):
        if self.feature.attribute('bezwaarformulier'):
            cmd = os.environ['COMSPEC'] + ' /c "start %s"'
            sp = subprocess.Popen(cmd % self.feature.attribute('bezwaarformulier'))

    def showPdf_mock(self):
        cmd = os.environ['COMSPEC'] + ' /c "start %s"'
        path = "C:\\Users\\Elke\\Documents\\qgis\\testpdf.pdf"
        sp = subprocess.Popen(cmd % path)

    def showEditWindow(self):
        p = ParcelWindow(self.main, self.layer, self.feature)
        QObject.connect(p, SIGNAL('saved(QgsFeature)'), self.setFeature)
        p.showMaximized()

    def zoomTo(self):
        self.layer.removeSelection()
        self.layer.select(self.feature.id())
        self.main.iface.mapCanvas().zoomToSelected(self.layer)
        self.layer.removeSelection()

    def takePhotos(self):
        #cmd = "C:\\Windows\\explorer.exe shell:AppsFolder\\Panasonic.CameraPlus_ehmb8xpdwb7p4!App"
        cmd = os.path.join(os.environ['SYSTEMROOT'], 'explorer.exe')
        cmd += " shell:AppsFolder\\Microsoft.MoCamera_cw5n1h2txyewy!Microsoft.Camera"
        photoPath = os.path.join(os.environ['USERPROFILE'], 'Pictures', 'Camera Roll')

        d = PhotoDialog(self.main.iface, photoPath)

        sp = subprocess.Popen(cmd)
        d.show()

    def showParcelList(self):
        d = ParcelListDialog(self, self.layer, self.feature)
        d.show()

class ParcelInfoDock(QDockWidget):
    def __init__(self, parent):
        QDockWidget.__init__(self, "Bezwaren bodemerosie", parent)
        self.setObjectName("Bezwaren bodemerosie")
        parent.addDockWidget(Qt.RightDockWidgetArea, self)

        QObject.connect(self, SIGNAL('topLevelChanged(bool)'), self.resizeToMinimum)

    def resizeToMinimum(self):
        self.resize(self.minimumSize())

    def toggleVisibility(self):
        self.setVisible(not self.isVisible())
