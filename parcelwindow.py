#-*- coding: utf-8 -*-

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
            'Katrien Oorts',
            'Sabine Buyle'
        ])

        if not self.isObjection():
            self.efwCmb_advies_aanvaarding.hide()
            self.efwCmb_advies_aanvaarding.setEnabled(False)
            self.efw_conform_eerder_advies.hide()
            self.efw_conform_eerder_advies.setEnabled(False)

        QObject.connect(self.btn_setToday, SIGNAL('clicked(bool)'), self.setToday)
        QObject.connect(self.btn_minimize, SIGNAL('clicked()'), self.minimize)
        QObject.connect(self.btn_save, SIGNAL('clicked()'), self.save)
        QObject.connect(self.btn_cancel, SIGNAL('clicked()'), self.cancel)
 
        self.populate()
        self.connectValidators()

    def isObjection(self):
        return self.feature.attribute('datum_bezwaar') != None

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

        if self.feature.attribute('jaarlijks_herberekenen') == None:
            # defaults to true
            self.efw_jaarlijks_herberekenen.setValue(1)

        if not self.efwCmb_veldcontrole_door.getValue():
            self.efwCmb_veldcontrole_door.setValue(self.main.qsettings.value('/Qgis/plugins/Erosiebezwaren/editor', None))

        self.initialEditor = self.efwCmb_veldcontrole_door.getValue()
        self.populateArea()

    def populateArea(self):
        if self.feature:
            self.lbv_oppervlakte.setText('%0.3f ha' % (self.feature.geometry().area()/10000.0))
        else:
            self.lbv_oppervlakte.clear()

    def connectValidators(self):
        QObject.connect(self.efwCmb_advies_behandeld, SIGNAL('currentIndexChanged(int)'), self._validate)
        QObject.connect(self.efwCmb_advies_aanvaarding, SIGNAL('currentIndexChanged(int)'), self._validate)
        QObject.connect(self.efw_advies_nieuwe_kleur, SIGNAL('valueChanged(QString)'), self._checkSaveable)
        self._validate()
        self._checkSaveable()

        self.efwCmb_advies_behandeld.setValue(self.feature.attribute('advies_behandeld'))
        self.efwCmb_advies_aanvaarding.setValue(self.feature.attribute('advies_aanvaarding'))
        self.efw_advies_nieuwe_kleur.setValue(self.feature.attribute('advies_nieuwe_kleur'))

    def _validate(self, *args):
        advies_behandeld = self.efwCmb_advies_behandeld.getValue()
        if advies_behandeld in ('Te behandelen', 'Herberekening afwachten'):
            self.efwCmb_advies_aanvaarding.setValue(None)
            self.efwCmb_advies_aanvaarding.setEnabled(False)
        else:
            self.efwCmb_advies_aanvaarding.setEnabled(self.isObjection())

        if advies_behandeld in ('Veldcontrole gebeurd', 'Herberekening afwachten'):
            self.efw_landbouwer_aanwezig.setEnabled(True)
        else:
            self.efw_landbouwer_aanwezig.setValue(0)
            self.efw_landbouwer_aanwezig.setEnabled(False)

        advies_aanvaarding = self.efwCmb_advies_aanvaarding.getValue()
        if advies_aanvaarding == 1:
            self.efw_advies_nieuwe_kleur.setEnabled(True)
            self.efw_advies_nieuwe_kleur.setValue(self.feature.attribute('advies_nieuwe_kleur'))
            self.efw_advies_nieuwe_kleur.setMaxValue(self.feature.attribute('kleur_2017'))
            self.efw_jaarlijks_herberekenen.setEnabled(False)
            self.efw_jaarlijks_herberekenen.setValue(0)
        elif advies_aanvaarding == 0:
            self.efw_advies_nieuwe_kleur.setEnabled(not self.feature.attribute('kleur_2017'))
            self.efw_advies_nieuwe_kleur.setValue(self.feature.attribute('kleur_2017'))
            self.efw_jaarlijks_herberekenen.setEnabled(True)
            if self.feature.attribute('jaarlijks_herberekenen') == None:
                self.efw_jaarlijks_herberekenen.setValue(1)
            else:
                self.efw_jaarlijks_herberekenen.setValue(self.feature.attribute('jaarlijks_herberekenen'))
        else:
            self.efw_advies_nieuwe_kleur.setEnabled(False)
            self.efw_advies_nieuwe_kleur.setValue(None)
            self.efw_jaarlijks_herberekenen.setEnabled(False)
            self.efw_jaarlijks_herberekenen.setValue(1)

        if not self.isObjection() and advies_behandeld and advies_behandeld not in ('Te behandelen', 'Herberekening afwachten'):
            self.efw_advies_nieuwe_kleur.setEnabled(True)

        if self.feature.attribute('herindiening_bezwaar') == 'true' and advies_behandeld not in ('Te behandelen', 'Herberekening afwachten'):
            self.efw_conform_eerder_advies.setEnabled(True)
        else:
            self.efw_conform_eerder_advies.setValue(0)
            self.efw_conform_eerder_advies.setEnabled(False)

    def _checkSaveable(self, *args):
        self.btn_save.setEnabled(self._isSaveable())

    def _isSaveable(self):
        advies_behandeld = self.efwCmb_advies_behandeld.getValue()
        advies_aanvaarding = self.efwCmb_advies_aanvaarding.getValue()
        if advies_behandeld in ('Te behandelen', 'Herberekening afwachten') and advies_aanvaarding == None:
            return True

        return self.efw_advies_nieuwe_kleur.getValue() != None

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

        self.setMinimumSize(1200, 1000)

    def closeEvent(self, event):
        self.parcelEditWidget.stop()
        self.closed.emit()

    def changeEvent(self, event):
        if type(event) is QWindowStateChangeEvent:
            self.windowStateChanged.emit()
