# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os
import re
import socket
import subprocess
import time

from ui_parcelinfowidget import Ui_ParcelInfoWidget
from ui_parcelinfocontentwidget import Ui_ParcelInfoContentWidget

from widgets import valuelabel
from widgets.elevatedfeaturewidget import ElevatedFeatureWidget
from parcelwindow import ParcelWindow
from photodialog import PhotoDialog
from parcellistdialog import ParcelListDialog
from previousobjectionsdialog import PreviousObjectionsDialog
from qgsutils import SpatialiteIterator

class ParcelButtonBar(QWidget):
    def __init__(self, parent, main, layer=None, parcel=None):
        QWidget.__init__(self)
        self.parent = parent
        self.main = main
        self.layer = layer
        self.feature = parcel

        self.editWindows = {}

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(-1, 6, -1, 6)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.btn_photo = QPushButton()
        self.btn_photo.setIcon(QIcon(":/icons/icons/photo.png"))
        self.btn_photo.setIconSize(QSize(64, 64))
        self.btn_photo.setSizePolicy(sizePolicy)

        self.btn_zoomto = QPushButton()
        self.btn_zoomto.setIcon(QIcon(":/icons/icons/zoomto.png"))
        self.btn_zoomto.setIconSize(QSize(64, 64))
        self.btn_zoomto.setSizePolicy(sizePolicy)

        self.btn_bezwaarformulier = QPushButton()
        self.btn_bezwaarformulier.setIcon(QIcon(":/icons/icons/pdf.png"))
        self.btn_bezwaarformulier.setIconSize(QSize(64, 64))
        self.btn_bezwaarformulier.setSizePolicy(sizePolicy)

        self.btn_edit = QPushButton()
        self.btn_edit.setIcon(QIcon(":/icons/icons/edit.png"))
        self.btn_edit.setIconSize(QSize(64, 64))
        self.btn_edit.setSizePolicy(sizePolicy)

        self.layout.addWidget(self.btn_photo)
        self.layout.addWidget(self.btn_zoomto)
        self.layout.addWidget(self.btn_bezwaarformulier)
        self.layout.addWidget(self.btn_edit)

        QObject.connect(self.btn_photo, SIGNAL('clicked(bool)'), self.takePhotos)
        QObject.connect(self.btn_edit, SIGNAL('clicked(bool)'), self.showEditWindow)

        self.populate()

    def isEditable(self):
        if self.feature:
            if self.feature.attribute('uniek_id') and \
               self.feature.attribute('datum_uit') == None:
               return True
        return False

    def setLayer(self, layer):
        self.layer = layer

    def setFeature(self, feature):
        self.feature = feature
        self.populate()

    def populate(self):
        self.populateTakePhotos()
        self.populateObjectionForm()
        self.populateEditButton()

    def populateTakePhotos(self):
        def takePhotos(enabled):
            self.btn_photo.setEnabled(enabled)
            self.btn_photo.setFlat(not enabled)

        if self.isEditable():
            takePhotos(socket.gethostname().startswith('toughpad')) # only enable taking photo's on tablets
        else:
            takePhotos(False)

    def populateObjectionForm(self):
        if self.feature:
            try:
                cmdShow = os.environ['COMSPEC'] + ' /c start "" "%s"'
                cmdExplore = os.path.join(os.environ['SYSTEMROOT'], 'explorer.exe') + ' "%s"'
            except KeyError:
                self.btn_bezwaarformulier.setEnabled(False)
                self.btn_bezwaarformulier.setFlat(True)
                return

            objectionPath = '/'.join([os.path.dirname(QgsProject.instance().fileName()), self.main.settings.getValue('paths/bezwaren'), str(self.feature.attribute('producentnr'))])
            objectionPath = objectionPath.replace('/', '\\')
            self.parent.objectionPath = []
            if os.path.exists(objectionPath):
                fileList = [i.lower() for i in os.listdir(objectionPath)]
                exts = set([f[f.rfind('.')+1:] for f in fileList])
                if len(exts) == 1 and 'pdf' in exts:
                    # only pdfs
                    for f in fileList:
                        self.parent.objectionPath.append(cmdShow % (objectionPath + '/' + f))
                elif len(exts) > 0:
                    # other thing(s)
                    self.parent.objectionPath.append(cmdExplore % objectionPath)
                self.btn_bezwaarformulier.setEnabled(True)
                self.btn_bezwaarformulier.setFlat(False)
                return
        self.btn_bezwaarformulier.setEnabled(False)
        self.btn_bezwaarformulier.setFlat(True)

    def populateEditButton(self):
        def editing(enabled):
            self.btn_edit.setEnabled(enabled)
            self.btn_edit.setFlat(not enabled)

        self.btn_edit.setIcon(QIcon(':/icons/icons/edit.png'))

        if not self.isEditable():
            editing(False)
            return

        editing(True)

        fid = self.feature.attribute('uniek_id')
        if fid in self.editWindows:
            if self.editWindows[fid].isMinimized():
                self.btn_edit.setIcon(QIcon(':/icons/icons/maximize.png'))

    def takePhotos(self):
        d = PhotoDialog(self.main.iface, str(self.feature.attribute('uniek_id')))
        QObject.connect(d, SIGNAL('saved()'), self.parent.contentWidget.populateShowPhotos)
        d.show()

    def showEditWindow(self):
        def clearEditWindow(fid):
            QObject.disconnect(w, SIGNAL('saved(QgsVectorLayer, QgsFeature)'), reloadFeature)
            QObject.disconnect(w, SIGNAL('closed()'), lambda: clearEditWindow(fid))
            QObject.disconnect(w, SIGNAL('windowStateChanged()'), self.populateEditButton)
            del(self.editWindows[fid])
            self.populateEditButton()

        def reloadFeature(layer, uniek_id):
            self.parent.setLayer(layer)
            s = SpatialiteIterator(layer)
            fts = s.queryExpression("uniek_id = '%s'" % uniek_id)
            if len(fts) > 0:
                self.parent.setFeature(fts[0])
            tableLayer = self.main.utils.getLayerByName('percelenkaart_table')
            tableLayer.triggerRepaint()

        if not self.feature:
            return

        fid = self.feature.attribute('uniek_id')
        if not fid:
            return

        if fid not in self.editWindows:
            w = ParcelWindow(self.main, self.layer, self.feature)
            QObject.connect(w, SIGNAL('saved(QgsVectorLayer, QString)'), reloadFeature)
            QObject.connect(w, SIGNAL('closed()'), lambda: clearEditWindow(fid))
            QObject.connect(w, SIGNAL('windowStateChanged()'), self.populateEditButton)
            self.editWindows[fid] = w

        self.btn_edit.setIcon(QIcon(':/icons/icons/edit.png'))
        self.editWindows[fid].setWindowState(Qt.WindowActive)
        self.editWindows[fid].show()

class ParcelInfoWidget(ElevatedFeatureWidget, Ui_ParcelInfoWidget):
    def __init__(self, parent, main, layer=None, parcel=None):
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.main = main
        self.layer = layer
        self.setupUi(self)

        self.objectionPath = []

        self.buttonBar = ParcelButtonBar(self, self.main, self.layer, parcel)
        self.contentWidget = ParcelInfoContentWidget(self, self.main, parcel)
        self.layout().addWidget(self.buttonBar)
        self.layout().addWidget(self.contentWidget)

        self.populate()

        QObject.connect(self.buttonBar.btn_bezwaarformulier, SIGNAL('clicked(bool)'), self.showObjection)
        QObject.connect(self.buttonBar.btn_zoomto, SIGNAL('clicked(bool)'), self.zoomTo)

    def setLayer(self, layer):
        self.layer = layer

    def populate(self):
        ElevatedFeatureWidget.populate(self)
        if self.feature:
            self.showInfo()
            self.main.selectionManager.clear()
            if self.feature.attribute('advies_behandeld'):
                s = SpatialiteIterator(self.layer)
                fts = s.queryExpression("producentnr_zo = '%s' and datum_bezwaar is not null" % self.feature.attribute('producentnr_zo'), attributes=[])
                for f in fts:
                    self.main.selectionManager.select(f, mode=1, toggleRendering=False)
            self.main.selectionManager.select(self.feature, mode=0, toggleRendering=True)
        else:
            self.clear()

        self.buttonBar.setLayer(self.layer)
        self.buttonBar.setFeature(self.feature)

        self.contentWidget.setFeature(self.feature)

    def clear(self):
        self.feature = None
        self.lb_geenselectie.show()
        self.buttonBar.hide()
        self.contentWidget.hide()
        self.main.selectionManager.clear()

    def showInfo(self):
        self.buttonBar.show()
        self.contentWidget.show()
        self.lb_geenselectie.hide()

    def showObjection(self):
        for o in self.objectionPath:
            subprocess.Popen(o)

    def zoomTo(self):
        self.main.iface.mapCanvas().setExtent(self.feature.geometry().boundingBox().buffer(10))
        self.main.iface.mapCanvas().refresh()

class ParcelInfoContentWidget(ElevatedFeatureWidget, Ui_ParcelInfoContentWidget):
    def __init__(self, parent, main, parcel=None):
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.main = main

        self.photoPath = None

        self.setupUi(self)

        self.btn_gpsDms.setChecked(self.main.qsettings.value('/Qgis/plugins/Erosiebezwaren/gps_dms', 'false') == 'true')
        QObject.connect(self.btn_gpsDms, SIGNAL('clicked(bool)'), self.toggleGpsDms)

        self.efw_advies_behandeld.setColorMap({
            'Te behandelen': ('#00ffee', '#000000'),
            'Veldcontrole gebeurd': ('#00aca1', '#000000'),
            'Beslist zonder veldcontrole': ('#8D8900', '#ffffff'),
            'Conform eerder advies': ('#8D8900', '#ffffff'),
            'Herberekening afwachten': ('#8D8900', '#ffffff'),
            'Afgehandeld ALBON': ('#00857c', '#ffffff')
        })

        self.efw_advies_aanvaarding.setValues([
            ('Aanvaard', 1),
            ('Niet aanvaard', 0)
        ])

        jaNee = {0: 'Nee', 1: 'Ja'}
        self.efw_jaarlijks_herberekenen.setValueMap(jaNee)
        self.efw_landbouwer_aanwezig.setValueMap(jaNee)
        self.efw_gesplitst_perceel.setValueMap(jaNee)
        self.efw_samengevoegd_perceel.setValueMap(jaNee)

        self.populate()

        if type(parent) is ParcelInfoWidget:
            QObject.connect(self.btn_showPhotos, SIGNAL('clicked(bool)'), self.showPhotos)
            QObject.connect(self.efwBtnAndereBezwaren_datum_bezwaar, SIGNAL('clicked(bool)'), self.showParcelList)
            QObject.connect(self.efwBtn_herindiening_bezwaar, SIGNAL('clicked(bool)'), self.showPreviousObjections)
        else:
            self.btn_showPhotos.hide()
            self.efwBtnAndereBezwaren_datum_bezwaar.hide()
            self.efwBtn_herindiening_bezwaar.hide()

            self.lb_gps.hide()
            self.lbv_gps.hide()
            self.btn_gpsDms.hide()

    def populate(self):
        ElevatedFeatureWidget.populate(self)
        if not self.feature:
            self.clear()

        self.populateAdvies()
        self.populateGps()
        self.populateShowPhotos()
        self.populateArea()
        self.populateTabAdvies()

    def populateAdvies(self):
        style = "* {"
        style += "border-radius: 4px;"
        style += "padding: 4px;"
        style += "background-color: %s;"
        style += "color: %s;"
        style += "border: 2px solid %s;"
        style += "}"

        if self.feature:
            if self.feature.attribute('advies_aanvaarding') == 0:
                self.lbv_advies.setText("Niet aanvaard", forceText=True)
                color = self.lbv_advies.colorMap.get(self.feature.attribute('advies_nieuwe_kleur'), ('#5d5d5d',))[0]
                self.lbv_advies.setStyleSheet(style % ('#5d5d5d', '#ffffff', color))
            elif self.feature.attribute('advies_aanvaarding') == 1 or \
                (self.feature.attribute('advies_aanvaarding') == None and self.feature.attribute('datum_bezwaar') == None):
                color, textcolor = self.lbv_advies.colorMap.get(self.feature.attribute('advies_nieuwe_kleur'), ('#c6c6c6', '#000000'))
                self.lbv_advies.setText("Advies", forceText=True)
                self.lbv_advies.setStyleSheet(style % (color, textcolor, color))
            else:
                self.lbv_advies.setText("Advies")
                color = self.lbv_advies.colorMap.get(self.feature.attribute('advies_nieuwe_kleur'), ('#c6c6c6',))[0]
                self.lbv_advies.setStyleSheet(style % ('#c6c6c6', '#000000', color))
        else:
            self.lbv_advies.setText("Advies")
            self.lbv_advies.setStyleSheet(style % ('#c6c6c6', '#000000', '#c6c6c6'))

    def populateGps(self):
        def rewriteText(t):
            tl = [i for i in t.split(',')]
            r = tl[1] + '<br>' + tl[0]
            return r

        if self.feature:
            gpsGeom = QgsGeometry(self.feature.geometry().centroid())
            gpsGeom.transform(QgsCoordinateTransform(
                QgsCoordinateReferenceSystem(31370, QgsCoordinateReferenceSystem.EpsgCrsId),
                QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)))
            dms = self.main.qsettings.value('/Qgis/plugins/Erosiebezwaren/gps_dms', 'false')
            if dms == 'true':
                self.lbv_gps.setText(rewriteText(gpsGeom.asPoint().toDegreesMinutesSeconds(2)))
            else:
                self.lbv_gps.setText(rewriteText(gpsGeom.asPoint().toDegreesMinutes(3)))
        else:
            self.lbv_gps.clear()

    def populateArea(self):
        if self.feature:
            self.lbv_oppervlakte.setText('%0.3f ha' % (self.feature.geometry().area()/10000.0))
        else:
            self.lbv_oppervlakte.clear()

    def populateShowPhotos(self):
        def showPhotos(enabled):
            self.btn_showPhotos.show() if enabled else self.btn_showPhotos.hide()

        if self.feature:
            # QgsProject.instance().fileName() returns path with forward slashes, even on Windows. Append subdirectories with forward slashes too
            # and replace all of them afterwards with backward slashes.
            fid = self.feature.attribute('uniek_id')
            if fid:
                photoPath = '/'.join([os.path.dirname(QgsProject.instance().fileName()), 'fotos', str(fid)])
                photoPath = photoPath.replace('/', '\\')
                if os.path.exists(photoPath) and len(os.listdir(photoPath)) > 0:
                    self.photoPath = photoPath
                    showPhotos(True)
                else:
                    showPhotos(False)
            else:
                showPhotos(False)
                self.photoPath = None
        else:
            showPhotos(False)
            self.photoPath = None

    def populateTabAdvies(self):
        def enableTabAdvies(enabled):
            if enabled and self.tabWidget.count() == 3:
                self.tabWidget.insertTab(2, self.tabAdvies, 'Advies')

            if not enabled and self.tabWidget.count() == 4:
                if self.tabWidget.currentIndex() == 2:
                    self.tabWidget.setCurrentIndex(0)
                self.tabWidget.removeTab(2)

        if self.feature:
            if self.photoPath:
                enableTabAdvies(True)
                return

            for i in range(self.scrollContentsAdvies.layout().count()):
                w = self.scrollContentsAdvies.layout().itemAt(i).widget()
                if w:
                    m = re.match(r'^efw[^_]*_(.*)$', w.objectName())
                    if m:
                        if self.feature.attribute(m.group(1)):
                            enableTabAdvies(True)
                            return

        enableTabAdvies(False)

    def clear(self):
        self.feature = None

    def showPhotos(self):
        if not self.photoPath:
            return

        cmd = os.path.join(os.environ['SYSTEMROOT'], 'explorer.exe')
        cmd += ' "%s"' % self.photoPath
        subprocess.Popen(cmd)

    def toggleGpsDms(self, checked):
        switch = {'true': 'false', 'false': 'true'}
        self.main.qsettings.setValue('/Qgis/plugins/Erosiebezwaren/gps_dms',
            switch[self.main.qsettings.value('/Qgis/plugins/Erosiebezwaren/gps_dms', 'true')])
        self.btn_gpsDms.setChecked(self.main.qsettings.value('/Qgis/plugins/Erosiebezwaren/gps_dms') == 'true')
        self.populateGps()

    def showParcelList(self):
        self.efwBtnAndereBezwaren_datum_bezwaar.setEnabled(False)
        QCoreApplication.processEvents()
        self.efwBtnAndereBezwaren_datum_bezwaar.repaint()
        d = ParcelListDialog(self.parent)
        QObject.connect(d, SIGNAL('finished(int)'), lambda x: self.efwBtnAndereBezwaren_datum_bezwaar.setEnabled(True))
        d.populate(True, self.feature.attribute('naam'), self.feature.attribute('producentnr_zo'))
        d.show()

    def showPreviousObjections(self):
        self.efwBtn_herindiening_bezwaar.setEnabled(False)
        QCoreApplication.processEvents()
        self.efwBtn_herindiening_bezwaar.repaint()
        d = PreviousObjectionsDialog(self.main, self.feature.attribute('uniek_id'))
        if self.feature.attribute('naam'):
            d.lbv_naam.setText('van %s' % str(self.feature.attribute('naam')))
        else:
            d.lbv_naam.hide()
        QObject.connect(d, SIGNAL('finished(int)'), lambda x: self.efwBtn_herindiening_bezwaar.setEnabled(True))
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
