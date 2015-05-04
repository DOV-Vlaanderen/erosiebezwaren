# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os
import re
import subprocess
import time

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

        self.btn_gpsDms.setChecked(self.main.settings.value('/Qgis/plugins/Erosiebezwaren/gps_dms', 'false') == 'true')
        QObject.connect(self.btn_gpsDms, SIGNAL('clicked(bool)'), self.toggleGpsDms)

        self.efw_advies_behandeld.setColorMap(
            {'te behandelen': ('#00ffee', '#000000')})

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
            self.populateGps()
        else:
            self.clear()

    def populateGps(self):
        if self.feature:
            gpsGeom = QgsGeometry(self.feature.geometry().centroid())
            gpsGeom.transform(QgsCoordinateTransform(
                QgsCoordinateReferenceSystem(31370, QgsCoordinateReferenceSystem.EpsgCrsId),
                QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)))
            dms = self.main.settings.value('/Qgis/plugins/Erosiebezwaren/gps_dms', 'false')
            if dms == 'true':
                self.lbv_gps.setText(gpsGeom.asPoint().toDegreesMinutesSeconds(0))
            else:
                self.lbv_gps.setText(gpsGeom.asPoint().toDegreesMinutes(3))
        else:
            self.lbv_gps.clear()

    def toggleGpsDms(self, checked):
        switch = {'true': 'false', 'false': 'true'}
        self.main.settings.setValue('/Qgis/plugins/Erosiebezwaren/gps_dms',
            switch[self.main.settings.value('/Qgis/plugins/Erosiebezwaren/gps_dms', 'true')])
        self.btn_gpsDms.setChecked(self.main.settings.value('/Qgis/plugins/Erosiebezwaren/gps_dms') == 'true')
        self.populateGps()

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
        d = PhotoDialog(self.main.iface, self.feature.attribute('uniek_id'))
        d.show()

    def showParcelList(self):
        self.btn_anderePercelen.setEnabled(False)
        QCoreApplication.processEvents()
        self.btn_anderePercelen.repaint()
        d = ParcelListDialog(self)
        QObject.connect(d, SIGNAL('finished(int)'), lambda x: self.btn_anderePercelen.setEnabled(True))
        d.populate(self.layer, self.feature)
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
