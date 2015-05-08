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
        self.writeLayer = self.main.utils.getLayerByName('bezwarenkaart')
        self.setupUi(self)

        self.btn_gpsDms.setChecked(self.main.settings.value('/Qgis/plugins/Erosiebezwaren/gps_dms', 'false') == 'true')
        QObject.connect(self.btn_gpsDms, SIGNAL('clicked(bool)'), self.toggleGpsDms)

        self.efw_advies_behandeld.defaultColors = ('#5d5d5d', '#ffffff')
        self.efw_advies_behandeld.setColorMap({
            'Te behandelen': ('#00ffee', '#000000'),
            'Veldcontrole gebeurd': ('#00aca1', '#000000')
        })

        self.efw_advies_aanvaarding.setValues([
            ('Aanvaard', 1),
            ('Niet aanvaard', 0)
        ])

        QObject.connect(self.efwBtn_bezwaarformulier, SIGNAL('clicked(bool)'), self.showPdf_mock)
        QObject.connect(self.btn_edit, SIGNAL('clicked(bool)'), self.showEditWindow)
        QObject.connect(self.btn_zoomto, SIGNAL('clicked(bool)'), self.zoomTo)
        QObject.connect(self.btn_photo, SIGNAL('clicked(bool)'), self.takePhotos)
        QObject.connect(self.btn_showPhotos, SIGNAL('clicked(bool)'), self.showPhotos)
        QObject.connect(self.efwBtnAndereBezwaren_advies_behandeld, SIGNAL('clicked(bool)'), self.showParcelList)

        self.populate()

    def populate(self):
        ElevatedFeatureWidget.populate(self)
        if self.feature:
            self.showInfo()
            self.main.selectionManager.clear()
            if self.feature.attribute('advies_behandeld'):
                for f in self.layer.getFeatures(QgsFeatureRequest(QgsExpression(
                    '"producentnr" = \'%s\'' % str(self.feature.attribute('producentnr'))))):
                    self.main.selectionManager.select(f, mode=1, toggleRendering=False)
            self.main.selectionManager.select(self.feature, mode=0, toggleRendering=True)
            self.populateGps()
            self.populatePhotos()
        else:
            self.populateGps()
            self.populatePhotos()
            self.clear()

    def populateGps(self):
        if self.feature:
            gpsGeom = QgsGeometry(self.feature.geometry().centroid())
            gpsGeom.transform(QgsCoordinateTransform(
                QgsCoordinateReferenceSystem(31370, QgsCoordinateReferenceSystem.EpsgCrsId),
                QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)))
            dms = self.main.settings.value('/Qgis/plugins/Erosiebezwaren/gps_dms', 'false')
            if dms == 'true':
                self.lbv_gps.setText(gpsGeom.asPoint().toDegreesMinutesSeconds(2))
            else:
                self.lbv_gps.setText(gpsGeom.asPoint().toDegreesMinutes(3))
        else:
            self.lbv_gps.clear()

    def populatePhotos(self):
        if self.feature:
            # QgsProject.instance().fileName() returns path with forward slashes, even on Windows. Append subdirectories with forward slashed too
            # and replace all of them afterwards with backward slashes.
            photoPath = '/'.join([os.path.dirname(QgsProject.instance().fileName()), 'fotos', str(self.feature.attribute('uniek_id'))])
            photoPath = photoPath.replace('/', '\\')
            if os.path.exists(photoPath) and len(os.listdir(photoPath)) > 0:
                self.photoPath = photoPath
                self.btn_showPhotos.show()
                return
        self.photoPath = None
        self.btn_showPhotos.hide()

    def showPhotos(self):
        if not self.photoPath:
            return

        cmd = os.path.join(os.environ['SYSTEMROOT'], 'explorer.exe')
        cmd += ' "%s"' % self.photoPath
        subprocess.Popen(cmd)

    def toggleGpsDms(self, checked):
        switch = {'true': 'false', 'false': 'true'}
        self.main.settings.setValue('/Qgis/plugins/Erosiebezwaren/gps_dms',
            switch[self.main.settings.value('/Qgis/plugins/Erosiebezwaren/gps_dms', 'true')])
        self.btn_gpsDms.setChecked(self.main.settings.value('/Qgis/plugins/Erosiebezwaren/gps_dms') == 'true')
        self.populateGps()

    def clear(self):
        self.feature = None
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
        if not self.writeLayer:
            self.writeLayer = self.main.utils.getLayerByName("bezwarenkaart")
        p = ParcelWindow(self.main, self.layer, self.writeLayer, self.feature)
        QObject.connect(p, SIGNAL('saved(QgsFeature)'), self.setFeature)
        p.show()

    def zoomTo(self):
        self.layer.removeSelection()
        self.layer.select(self.feature.id())
        self.main.iface.mapCanvas().zoomToSelected(self.layer)
        self.layer.removeSelection()

    def takePhotos(self):
        d = PhotoDialog(self.main.iface, str(self.feature.attribute('uniek_id')))
        d.show()

    def showParcelList(self):
        self.efwBtnAndereBezwaren_advies_behandeld.setEnabled(False)
        QCoreApplication.processEvents()
        self.efwBtnAndereBezwaren_advies_behandeld.repaint()
        d = ParcelListDialog(self)
        d.lbv_bezwaren_van.setText('Bezwaren van %s' % str(self.feature.attribute('naam')))
        QObject.connect(d, SIGNAL('finished(int)'), lambda x: self.efwBtnAndereBezwaren_advies_behandeld.setEnabled(True))
        d.populate(self.layer, self.feature.attribute('producentnr'))
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
