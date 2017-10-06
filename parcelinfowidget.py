# -*- coding: utf-8 -*-
"""Module containing the classes to show information about a parcel.

It contains the classes ParcelInfoDock, ParcelInfoWidget, ParcelButtonBar and
ParcelInfoContentWidget.

ParcelInfoDock is the panel that contains a ParcelInfoWidget. This in turn
consists of a ParcelButtonBar at the top and a ParcelInfoContentWidget at
the bottom.
"""

#  DOV Erosiebezwaren, QGis plugin to assess field erosion on tablets
#  Copyright (C) 2015-2017  Roel Huybrechts
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import PyQt4.Qt as Qt
import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
import qgis.core as QGisCore

import os
import re
import socket
import subprocess

from ui_parcelinfowidget import Ui_ParcelInfoWidget
from ui_parcelinfocontentwidget import Ui_ParcelInfoContentWidget

from monitoringwindow import MonitoringWindow
from parcellistdialog import ParcelListDialog
from parcelwindow import ParcelWindow
from photodialog import PhotoDialog
from qgsutils import SpatialiteIterator
from widgets.elevatedfeaturewidget import ElevatedFeatureWidget


class ParcelButtonBar(QtGui.QWidget):
    """Widget for the four action buttons on top of the ParcelInfoWidget."""

    def __init__(self, parent, main, layer=None, parcel=None):
        """Initialisation.

        Populates the interface based on attribute values of the parcel.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to be used as parent widget of this one.
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.
        layer : QGisCore.QgsVectorLayer, optional
            Layer of the parcel feature.
        parcel : QGisCore.QgsFeature, optional
            Feature representing the parcel.

        """
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.main = main
        self.layer = layer
        self.feature = parcel

        self.editWindows = {}

        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(-1, 6, -1, 6)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum,
                                       QtGui.QSizePolicy.Maximum)

        self.btn_photo = QtGui.QPushButton()
        self.btn_photo.setIcon(QtGui.QIcon(":/icons/icons/photo.png"))
        self.btn_photo.setIconSize(QtCore.QSize(64, 64))
        self.btn_photo.setSizePolicy(sizePolicy)

        self.btn_zoomto = QtGui.QPushButton()
        self.btn_zoomto.setIcon(QtGui.QIcon(":/icons/icons/zoomto.png"))
        self.btn_zoomto.setIconSize(QtCore.QSize(64, 64))
        self.btn_zoomto.setSizePolicy(sizePolicy)

        self.btn_bezwaarformulier = QtGui.QPushButton()
        self.btn_bezwaarformulier.setIcon(QtGui.QIcon(":/icons/icons/pdf.png"))
        self.btn_bezwaarformulier.setIconSize(QtCore.QSize(64, 64))
        self.btn_bezwaarformulier.setSizePolicy(sizePolicy)

        self.btn_edit = QtGui.QPushButton()
        self.btn_edit.setIcon(QtGui.QIcon(":/icons/icons/edit.png"))
        self.btn_edit.setIconSize(QtCore.QSize(64, 64))
        self.btn_edit.setSizePolicy(sizePolicy)

        self.layout.addWidget(self.btn_photo)
        self.layout.addWidget(self.btn_zoomto)
        self.layout.addWidget(self.btn_bezwaarformulier)
        self.layout.addWidget(self.btn_edit)

        QtCore.QObject.connect(self.btn_photo, QtCore.SIGNAL('clicked(bool)'),
                               self.takePhotos)
        QtCore.QObject.connect(self.btn_edit, QtCore.SIGNAL('clicked(bool)'),
                               self.showEditWindow)

        self.populate()

    def isEditable(self):
        """Check if the user is allowed to edit the currently selected parcel.

        Returns
        -------
        boolean
            True if the user is allowed to edit the feature, False otherwise.

        """
        if self.feature:
            if self.feature.attribute('uniek_id') and \
                    self.feature.attribute('datum_uit') == None and \
                    not self.parent.monitoringOpen:
                return True
        return False

    def setLayer(self, layer):
        """Set the layer.

        Parameters
        ----------
        layer : QGisCore.QgsVectorLayer
            Layer of the feature to show.

        """
        self.layer = layer

    def setFeature(self, feature):
        """Set the feature.

        Parameters
        ----------
        feature : QGisCore.QgsFeature
            Parcel feature to show.

        """
        self.feature = feature
        self.populate()

    def populate(self):
        """Populate the contents of this widget.

        Based on information in the attribute values of the parcel.
        """
        self.populateTakePhotos()
        self.populateObjectionForm()
        self.populateEditButton()

    def populateTakePhotos(self):
        """Populate the 'take photos' button.

        Only enable taking photos on the tablets and when the feature is
        editable.
        """
        def takePhotos(enabled):
            self.btn_photo.setEnabled(enabled)
            self.btn_photo.setFlat(not enabled)

        if self.isEditable():
            # only enable taking photo's on tablets
            takePhotos(socket.gethostname().startswith('toughpad'))
        else:
            takePhotos(False)

    def populateObjectionForm(self):
        """Populate the 'show objection form' button.

        Enables the button if there are one or more objection forms available
        for this parcel.
        """
        if self.feature:
            try:
                cmdShow = os.environ['COMSPEC'] + ' /c start "" "%s"'
                cmdExplore = os.path.join(os.environ['SYSTEMROOT'],
                                          'explorer.exe') + ' "%s"'
            except KeyError:
                self.btn_bezwaarformulier.setEnabled(False)
                self.btn_bezwaarformulier.setFlat(True)
                return

            objectionPath = '/'.join([os.path.dirname(
                QGisCore.QgsProject.instance().fileName()),
                self.main.settings.getValue('paths/bezwaren'),
                str(self.feature.attribute('producentnr'))])
            objectionPath = objectionPath.replace('/', '\\')
            self.parent.objectionPath = []
            if os.path.exists(objectionPath):
                fileList = [i.lower() for i in os.listdir(objectionPath)]
                exts = set([f[f.rfind('.')+1:] for f in fileList])
                if len(exts) == 1 and 'pdf' in exts:
                    # only pdfs
                    for f in fileList:
                        self.parent.objectionPath.append(cmdShow % (
                            objectionPath + '/' + f))
                elif len(exts) > 0:
                    # other thing(s)
                    self.parent.objectionPath.append(
                        cmdExplore % objectionPath)
                self.btn_bezwaarformulier.setEnabled(True)
                self.btn_bezwaarformulier.setFlat(False)
                return
        self.btn_bezwaarformulier.setEnabled(False)
        self.btn_bezwaarformulier.setFlat(True)

    def populateEditButton(self):
        """Populate the 'edit parcel' button.

        Enables the button if the feature is editable and changed the icon of
        the button if an edit window for this feature is already open and
        minimized.
        """
        def editing(enabled):
            self.btn_edit.setEnabled(enabled)
            self.btn_edit.setFlat(not enabled)

        self.btn_edit.setIcon(QtGui.QIcon(':/icons/icons/edit.png'))

        if not self.isEditable():
            print "Not editable"
            editing(False)
            return

        editing(True)

        fid = self.feature.attribute('uniek_id')
        if fid in self.editWindows:
            if self.editWindows[fid].isMinimized():
                self.btn_edit.setIcon(
                    QtGui.QIcon(':/icons/icons/maximize.png'))

    def takePhotos(self):
        """Take photos of this parcel.

        Opens a photodialog.PhotoDialog, starting the Windows Camera app.
        """
        d = PhotoDialog(self.main.iface, str(self.feature.attribute(
            'uniek_id')))
        QtCore.QObject.connect(d, QtCore.SIGNAL('saved()'),
                               self.parent.contentWidget.populateShowPhotos)
        d.show()

    def showEditWindow(self):
        """Open a ParcelWindow to edit the feature."""
        def clearEditWindow(fid):
            QtCore.QObject.disconnect(
                w, QtCore.SIGNAL('saved(QgsVectorLayer, QgsFeature)'),
                reloadFeature)
            QtCore.QObject.disconnect(
                w, QtCore.SIGNAL('closed()'), lambda: clearEditWindow(fid))
            QtCore.QObject.disconnect(
                w, QtCore.SIGNAL('windowStateChanged()'),
                self.populateEditButton)
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
            QtCore.QObject.connect(
                w, QtCore.SIGNAL('saved(QgsVectorLayer, QString)'),
                reloadFeature)
            QtCore.QObject.connect(
                w, QtCore.SIGNAL('closed()'), lambda: clearEditWindow(fid))
            QtCore.QObject.connect(
                w, QtCore.SIGNAL('windowStateChanged()'),
                self.populateEditButton)
            QtCore.QObject.connect(
                w, QtCore.SIGNAL('closed()'),
                self.parent.contentWidget.populateMonitoringButton)
            self.editWindows[fid] = w

        self.btn_edit.setIcon(QtGui.QIcon(':/icons/icons/edit.png'))
        self.editWindows[fid].setWindowState(Qt.Qt.WindowActive)
        self.editWindows[fid].show()


class ParcelInfoWidget(ElevatedFeatureWidget, Ui_ParcelInfoWidget):
    """Class representing the content of the ParcelInfoDock.

    Consisting of a ParcelButtonBar at the top and a ParcelInfoContentWidget
    below it.

    """

    def __init__(self, parent, main, layer=None, parcel=None):
        """Initialisation.

        Populates the interface based on attribute values of the parcel.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to be used as parent widget of this one.
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.
        layer : QGisCore.QgsVectorLayer, optional
            Layer of the parcel feature.
        parcel : QGisCore.QgsFeature, optional
            Feature representing the parcel.

        """
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.main = main
        self.layer = layer
        self.setupUi(self)

        self.objectionPath = []
        self.monitoringOpen = False

        self.buttonBar = ParcelButtonBar(self, self.main, self.layer, parcel)
        self.contentWidget = ParcelInfoContentWidget(self, self.main, parcel)
        self.layout().addWidget(self.buttonBar)
        self.layout().addWidget(self.contentWidget)

        self.populate()

        QtCore.QObject.connect(self.buttonBar.btn_bezwaarformulier,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.showObjection)
        QtCore.QObject.connect(self.buttonBar.btn_zoomto,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.zoomTo)
        QtCore.QObject.connect(self.buttonBar.btn_edit,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.contentWidget.populateMonitoringButton)

    def setLayer(self, layer):
        """Set the layer.

        Parameters
        ----------
        layer : QGisCore.QgsVectorLayer
            Layer of the feature to show.

        """
        self.layer = layer

    def populate(self):
        """Populate the contents of this widget and child widgets.

        Based on information in the attribute values of the parcel.
        """
        ElevatedFeatureWidget.populate(self)
        if self.feature:
            self.showInfo()
            self.main.selectionManagerPolygons.clear()
            if self.feature.attribute('advies_behandeld'):
                s = SpatialiteIterator(self.layer)
                fts = s.queryExpression(
                    "producentnr_zo = '%s' and datum_bezwaar is not null" %
                    self.feature.attribute('producentnr_zo'), attributes=[])
                for f in fts:
                    self.main.selectionManagerPolygons.select(
                        f, mode=1, toggleRendering=False)
            self.main.selectionManagerPolygons.select(self.feature, mode=0,
                                                      toggleRendering=True)
        else:
            self.clear()

        self.buttonBar.setLayer(self.layer)
        self.buttonBar.setFeature(self.feature)
        self.contentWidget.setFeature(self.feature)

    def clear(self):
        """Clear the contents of this widget.

        Set the current parcel to `None` and show a message that no date is
        available.
        """
        self.feature = None
        self.lb_geenselectie.show()
        self.buttonBar.hide()
        self.contentWidget.hide()
        self.main.selectionManagerPolygons.clear()

    def showInfo(self):
        """Show info of a parcel.

        This is the inverse of clear().
        """
        self.buttonBar.show()
        self.contentWidget.show()
        self.lb_geenselectie.hide()

    def showObjection(self):
        """Open all objection paths (folders or files) in Windows Explorer.

        Used as a callback for the 'show objection' button in ParcelButtonBar.
        """
        for o in self.objectionPath:
            subprocess.Popen(o)

    def zoomTo(self):
        """Zoom to map canvas to the extent of the parcel shown in this widget.

        Used as a callback for the 'zoom to parcel' button in ParcelButtonBar.
        """
        self.main.iface.mapCanvas().setExtent(
            self.feature.geometry().boundingBox().buffer(10))
        self.main.iface.mapCanvas().refresh()


class ParcelInfoContentWidget(ElevatedFeatureWidget,
                              Ui_ParcelInfoContentWidget):
    """Class for the content widget that represents a single parcel."""

    def __init__(self, parent, main, parcel=None):
        """Initialisation.

        Populates the interface based on attribute values of the parcel.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to be used as parent for this widget.
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.
        parcel : QGisCore.QgsFeature, optional
            The feature representing the parcel. The attribute values of this
            feature will be shown as the content of this widget.

        """
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.main = main

        self.photoPath = None

        self.setupUi(self)

        self.btn_gpsDms.setChecked(self.main.qsettings.value(
            '/Qgis/plugins/Erosiebezwaren/gps_dms', 'false') == 'true')
        QtCore.QObject.connect(self.btn_gpsDms,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.toggleGpsDms)

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
        self.efw_conform_eerder_advies.setValueMap(jaNee)

        self.populate()

        if type(parent) is ParcelInfoWidget:
            QtCore.QObject.connect(
                self.btn_showPhotos,
                QtCore.SIGNAL('clicked(bool)'), self.showPhotos)
            QtCore.QObject.connect(
                self.btn_monitoring,
                QtCore.SIGNAL('clicked(bool)'), self.showMonitoring)
            QtCore.QObject.connect(
                self.efwBtnAndereBezwaren_datum_bezwaar,
                QtCore.SIGNAL('clicked(bool)'), self.showParcelList)
            QtCore.QObject.connect(
                self.efwBtn_herindiening_bezwaar,
                QtCore.SIGNAL('clicked(bool)'), self.showPreviousObjections)
        else:
            self.btn_showPhotos.hide()
            self.btn_monitoring.hide()
            self.efwBtnAndereBezwaren_datum_bezwaar.hide()
            self.efwBtn_herindiening_bezwaar.hide()

            self.lb_gps.hide()
            self.lbv_gps.hide()
            self.btn_gpsDms.hide()

    def populate(self):
        """Populate the contents of this widget.

        Based on information in the attribute values of the parcel.
        """
        ElevatedFeatureWidget.populate(self)
        if not self.feature:
            self.clear()

        self.populateAdvies()
        self.populateGps()
        self.populateShowPhotos()
        self.populateArea()
        self.populateTabAdvies()
        self.populateMonitoringButton()

    def populateAdvies(self):
        """Populate the 'advies' label.

        Set the background and border color according to the formulated advice.
        """
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
                color = self.lbv_advies.colorMap.get(
                    self.feature.attribute('advies_nieuwe_kleur'),
                    ('#5d5d5d',))[0]
                self.lbv_advies.setStyleSheet(style % ('#5d5d5d', '#ffffff',
                                                       color))
            elif self.feature.attribute('advies_aanvaarding') == 1 or \
                (self.feature.attribute('advies_aanvaarding') == None and
                 self.feature.attribute('datum_bezwaar') == None):
                color, textcolor = self.lbv_advies.colorMap.get(
                    self.feature.attribute('advies_nieuwe_kleur'), ('#c6c6c6',
                                                                    '#000000'))
                self.lbv_advies.setText("Advies", forceText=True)
                self.lbv_advies.setStyleSheet(style % (color, textcolor,
                                                       color))
            else:
                self.lbv_advies.setText("Advies")
                color = self.lbv_advies.colorMap.get(self.feature.attribute(
                    'advies_nieuwe_kleur'), ('#c6c6c6',))[0]
                self.lbv_advies.setStyleSheet(style % ('#c6c6c6', '#000000',
                                                       color))
        else:
            self.lbv_advies.setText("Advies")
            self.lbv_advies.setStyleSheet(style % ('#c6c6c6', '#000000',
                                                   '#c6c6c6'))

    def populateGps(self):
        """Populate the labels with the GPS coordinates of this parcel.

        Set them based on the coordinates of the centroid of the parcel,
        taking the degrees/dms settings into account.
        """
        def rewriteText(t):
            tl = [i for i in t.split(',')]
            r = tl[1] + '<br>' + tl[0]
            return r

        if self.feature:
            gpsGeom = QGisCore.QgsGeometry(self.feature.geometry().centroid())
            gpsGeom.transform(QGisCore.QgsCoordinateTransform(
                QGisCore.QgsCoordinateReferenceSystem(
                    31370, QGisCore.QgsCoordinateReferenceSystem.EpsgCrsId),
                QGisCore.QgsCoordinateReferenceSystem(
                    4326, QGisCore.QgsCoordinateReferenceSystem.EpsgCrsId)))
            dms = self.main.qsettings.value(
                '/Qgis/plugins/Erosiebezwaren/gps_dms', 'false')
            if dms == 'true':
                self.lbv_gps.setText(rewriteText(
                    gpsGeom.asPoint().toDegreesMinutesSeconds(2)))
            else:
                self.lbv_gps.setText(rewriteText(
                    gpsGeom.asPoint().toDegreesMinutes(3)))
        else:
            self.lbv_gps.clear()

    def populateArea(self):
        """Populate the label with the area of the parcel.

        Set it with the area in ha calculated from the geometry of the parcel.
        """
        if self.feature:
            self.lbv_oppervlakte.setText('%0.3f ha' % (
                self.feature.geometry().area()/10000.0))
        else:
            self.lbv_oppervlakte.clear()

    def populateMonitoringButton(self):
        """Populate the button to open the 'monitoring' dialog.

        Set it to disabled when an edit window or monitoring window is already
        open for this parcel.
        """
        if self.btn_monitoring.isVisible() and (
                self.parent.monitoringOpen or
                len(self.parent.buttonBar.editWindows) > 0):
            self.btn_monitoring.setEnabled(False)
        else:
            self.btn_monitoring.setEnabled(True)

    def populateShowPhotos(self):
        """Populate the button to show existing photos of this parcel.

        Only show the button if there are photos available for this parcel.
        """
        def showPhotos(enabled):
            self.btn_showPhotos.show() if enabled else \
                self.btn_showPhotos.hide()

        if self.feature:
            # QGisCore.QgsProject.instance().fileName() returns path with
            # forward slashes, even on Windows. Append subdirectories with
            # forward slashes too and replace all of them afterwards with
            # backward slashes.
            fid = self.feature.attribute('uniek_id')
            if fid:
                photoPath = '/'.join([os.path.dirname(
                    QGisCore.QgsProject.instance().fileName()),
                                      'fotos', str(fid)])
                photoPath = photoPath.replace('/', '\\')
                if os.path.exists(photoPath) \
                        and len(os.listdir(photoPath)) > 0:
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
        """Show or hide the tab 'advies'.

        Only show the tab 'advies' if it contains information. Hide the tab if
        none of the fields have a value.
        """
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

            fields = self.feature.fields()
            for i in range(self.scrollContentsAdvies.layout().count()):
                w = self.scrollContentsAdvies.layout().itemAt(i).widget()
                if w:
                    m = re.match(r'^efw[^_]*_(.*)$', w.objectName())
                    if m:
                        if fields.indexFromName(m.group(1)) > -1 and \
                                self.feature.attribute(m.group(1)):
                            enableTabAdvies(True)
                            return

        enableTabAdvies(False)

    def clear(self):
        """Set the current feature to `None`."""
        self.feature = None

    def showPhotos(self):
        """Open the directory containing the photos of this parcel in Explorer.

        Used as callback for the 'show photos' button.
        """
        if not self.photoPath:
            return

        cmd = os.path.join(os.environ['SYSTEMROOT'], 'explorer.exe')
        cmd += ' "%s"' % self.photoPath
        subprocess.Popen(cmd)

    def showMonitoring(self):
        """Open the MonitoringWindow to edit the monitoring for this parcel."""
        def setMonitoringOpen(value):
            self.parent.monitoringOpen = value

        setMonitoringOpen(True)
        self.parent.buttonBar.populateEditButton()
        self.populateMonitoringButton()
        QtCore.QCoreApplication.processEvents()
        self.btn_monitoring.repaint()

        m = MonitoringWindow(self.main, self.feature, self.parent.layer)
        QtCore.QObject.connect(
            m, QtCore.SIGNAL('closed()'),
            lambda: setMonitoringOpen(False))
        QtCore.QObject.connect(
            m, QtCore.SIGNAL('closed()'),
            lambda: self.populateMonitoringButton())
        QtCore.QObject.connect(
            m, QtCore.SIGNAL('closed()'),
            lambda: self.parent.buttonBar.populateEditButton())
        m.show()

    def toggleGpsDms(self, checked=None):
        """Switch the format of the GPS coordinates.

        Switch between decimal degrees and degrees, minutes and seconds.

        Parameters
        ----------
        checked : boolean, optional
            The current value of the toggle button to switch format.

        """
        switch = {'true': 'false', 'false': 'true'}
        self.main.qsettings.setValue(
            '/Qgis/plugins/Erosiebezwaren/gps_dms',
            switch[self.main.qsettings.value(
                '/Qgis/plugins/Erosiebezwaren/gps_dms', 'true')])
        self.btn_gpsDms.setChecked(self.main.qsettings.value(
            '/Qgis/plugins/Erosiebezwaren/gps_dms') == 'true')
        self.populateGps()

    def showParcelList(self):
        """Open the dialog with other objections of the same farmer."""
        self.efwBtnAndereBezwaren_datum_bezwaar.setEnabled(False)
        QtCore.QCoreApplication.processEvents()
        self.efwBtnAndereBezwaren_datum_bezwaar.repaint()
        d = ParcelListDialog(self.parent)
        QtCore.QObject.connect(
            d, QtCore.SIGNAL('finished(int)'),
            lambda x: self.efwBtnAndereBezwaren_datum_bezwaar.setEnabled(True))
        d.populate(True, self.feature.attribute('naam'),
                   self.feature.attribute('producentnr_zo'))
        d.show()

    def showPreviousObjections(self):
        """Open the dialog with previous objections on the current parcel."""
        from previousobjectionsdialog import PreviousObjectionsDialog

        self.efwBtn_herindiening_bezwaar.setEnabled(False)
        QtCore.QCoreApplication.processEvents()
        self.efwBtn_herindiening_bezwaar.repaint()
        d = PreviousObjectionsDialog(self.main,
                                     self.feature.attribute('uniek_id'))
        if self.feature.attribute('naam'):
            d.lbv_naam.setText('van %s' % str(self.feature.attribute('naam')))
        else:
            d.lbv_naam.hide()
        QtCore.QObject.connect(
            d, QtCore.SIGNAL('finished(int)'),
            lambda x: self.efwBtn_herindiening_bezwaar.setEnabled(True))
        d.show()


class ParcelInfoDock(QtGui.QDockWidget):
    """Panel that contains information about a specific parcel."""

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QMainWindow
            Main window to attach this panel to.

        """
        QtGui.QDockWidget.__init__(self, "Bezwaren bodemerosie", parent)
        self.setObjectName("Bezwaren bodemerosie")
        parent.addDockWidget(Qt.Qt.RightDockWidgetArea, self)

        QtCore.QObject.connect(self, QtCore.SIGNAL('topLevelChanged(bool)'),
                               self.resizeToMinimum)

    def resizeToMinimum(self):
        """Resize to minimum size."""
        self.resize(self.minimumSize())

    def toggleVisibility(self):
        """Toggle the visibility of the panel."""
        self.setVisible(not self.isVisible())
