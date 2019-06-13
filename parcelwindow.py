# -*- coding: utf-8 -*-
"""Module containing the ParcelWindow and ParcelEditWidget classes."""

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

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui

from ui_parceleditwidget import Ui_ParcelEditWidget

from widgets.elevatedfeaturewidget import ElevatedFeatureWidget


class ParcelEditWidget(ElevatedFeatureWidget, Ui_ParcelEditWidget):
    """Class representing the widget to edit a parcel."""

    def __init__(self, parent, main, layer, parcel):
        """Initialisation.

        Populate the widget based on attribute values of the parcel.

        Parameters
        ----------
        parent : ParcelWindow
            Parent window of the ParcelEditWidget.
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.
        layer : QGisCore.QgsVectorLayer
            Layer of the feature to edit.
        parcel : QGisCore.QgsFeature
            Feature of the parcel to edit.

        """
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
            'Roel Huybrechts'
        ])

        if not self.isObjection():
            self.efwCmb_advies_aanvaarding.hide()
            self.efwCmb_advies_aanvaarding.setEnabled(False)
            self.efw_conform_eerder_advies.hide()
            self.efw_conform_eerder_advies.setEnabled(False)

        QtCore.QObject.connect(
            self.btn_setToday, QtCore.SIGNAL('clicked(bool)'), self.setToday)
        QtCore.QObject.connect(
            self.btn_minimize, QtCore.SIGNAL('clicked()'), self.minimize)
        QtCore.QObject.connect(
            self.btn_save, QtCore.SIGNAL('clicked()'), self.save)
        QtCore.QObject.connect(
            self.btn_cancel, QtCore.SIGNAL('clicked()'), self.cancel)

        self.populate()
        self._connectValidators()

    def isObjection(self):
        """Check if the parcel has an objection.

        Returns
        -------
        boolean
            `True` if the parcel has an objection, `False` otherwise.

        """
        return self.feature.attribute('datum_bezwaar') != None

    def minimize(self):
        """Minimize the parent window of this widget."""
        self.parent.showMinimized()

    def stop(self):
        """Stop interacting, disabling the save and cancel buttons."""
        self.btn_save.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        QtCore.QCoreApplication.processEvents()
        self.btn_save.repaint()
        self.btn_cancel.repaint()

    def save(self):
        """Save and close the edit window.

        Save the updated version of the feature to the layer and, on success,
        close the parent window.
        """
        success = self.saveFeature()

        if not success:
            return

        editor = self.efwCmb_veldcontrole_door.getValue()
        if editor and (editor != self.initialEditor):
            self.main.qsettings.setValue('/Qgis/plugins/Erosiebezwaren/editor',
                                         editor)
        self.main.iface.mapCanvas().refresh()
        self.stop()
        self.parent.saved.emit(self.layer, self.feature.attribute('uniek_id'))
        self.parent.close()

    def cancel(self):
        """Cancel editing: stop interacting and close parent window."""
        self.stop()
        self.parent.close()

    def setToday(self):
        """Set the day of the 'datum_veldbezoek' entry to the current date."""
        self.efw_datum_veldbezoek.setDate(QtCore.QDate.currentDate())

    def populate(self):
        """Populate the widget based on the attribute values of the feature."""
        ElevatedFeatureWidget.populate(self)

        self.lbv_header.setText('Bewerk advies voor perceel %s\n  van %s' %
                                (self.feature.attribute('uniek_id'),
                                 self.feature.attribute('naam')))
        self.parent.setWindowTitle('Bewerk advies %s' %
                                   self.feature.attribute('uniek_id'))

        if self.feature.attribute('jaarlijks_herberekenen') == None:
            # defaults to true
            self.efw_jaarlijks_herberekenen.setValue(1)

        if not self.efwCmb_veldcontrole_door.getValue():
            self.efwCmb_veldcontrole_door.setValue(self.main.qsettings.value(
                '/Qgis/plugins/Erosiebezwaren/editor', None))

        self.initialEditor = self.efwCmb_veldcontrole_door.getValue()
        self._populateArea()

    def _populateArea(self):
        """Populate the label with the area of the parcel.

        Set it with the area in ha calculated from the geometry of the parcel.
        """
        if self.feature:
            self.lbv_oppervlakte.setText('%0.3f ha' % (
                self.feature.geometry().area()/10000.0))
        else:
            self.lbv_oppervlakte.clear()

    def _connectValidators(self):
        """Connect validators to the changed signals of the entry fields."""
        QtCore.QObject.connect(
            self.efwCmb_advies_behandeld,
            QtCore.SIGNAL('currentIndexChanged(int)'), self._validate)
        QtCore.QObject.connect(
            self.efwCmb_advies_aanvaarding,
            QtCore.SIGNAL('currentIndexChanged(int)'), self._validate)
        QtCore.QObject.connect(
            self.efw_advies_nieuwe_kleur,
            QtCore.SIGNAL('valueChanged(QString)'), self._checkSaveable)
        self._validate()
        self._checkSaveable()

        self.efwCmb_advies_behandeld.setValue(
            self.feature.attribute('advies_behandeld'))
        self.efwCmb_advies_aanvaarding.setValue(
            self.feature.attribute('advies_aanvaarding'))
        self.efw_advies_nieuwe_kleur.setValue(
            self.feature.attribute('advies_nieuwe_kleur'))

    def _validate(self, *args):
        """Validate the entry fields.

        Adjusts the value of some entry fields based on the values of others.

        Parameters
        ----------
        *args : list
            Catchall parameter. All parameters are ignored. This way we make
            sure the function can be called with any (number of) arguments.

        """
        advies_behandeld = self.efwCmb_advies_behandeld.getValue()
        if advies_behandeld in ('Te behandelen', 'Herberekening afwachten'):
            self.efwCmb_advies_aanvaarding.setValue(None)
            self.efwCmb_advies_aanvaarding.setEnabled(False)
        else:
            self.efwCmb_advies_aanvaarding.setEnabled(self.isObjection())

        if advies_behandeld in ('Veldcontrole gebeurd',
                                'Herberekening afwachten'):
            self.efw_landbouwer_aanwezig.setEnabled(True)
        else:
            self.efw_landbouwer_aanwezig.setValue(0)
            self.efw_landbouwer_aanwezig.setEnabled(False)

        advies_aanvaarding = self.efwCmb_advies_aanvaarding.getValue()
        if advies_aanvaarding == 1:
            self.efw_advies_nieuwe_kleur.setEnabled(True)
            self.efw_advies_nieuwe_kleur.setValue(self.feature.attribute(
                'advies_nieuwe_kleur'))
            self.efw_advies_nieuwe_kleur.setMaxValue(self.feature.attribute(
                'kleur_2019'))
            self.efw_jaarlijks_herberekenen.setEnabled(False)
            self.efw_jaarlijks_herberekenen.setValue(0)
        elif advies_aanvaarding == 0:
            self.efw_advies_nieuwe_kleur.setEnabled(
                not self.feature.attribute('kleur_2019'))
            self.efw_advies_nieuwe_kleur.setValue(
                self.feature.attribute('kleur_2019'))
            self.efw_jaarlijks_herberekenen.setEnabled(True)
            if self.feature.attribute('jaarlijks_herberekenen') == None:
                self.efw_jaarlijks_herberekenen.setValue(1)
            else:
                self.efw_jaarlijks_herberekenen.setValue(
                    self.feature.attribute('jaarlijks_herberekenen'))
        else:
            self.efw_advies_nieuwe_kleur.setEnabled(False)
            self.efw_advies_nieuwe_kleur.setValue(None)
            self.efw_jaarlijks_herberekenen.setEnabled(False)
            self.efw_jaarlijks_herberekenen.setValue(1)

        if not self.isObjection() and advies_behandeld \
            and advies_behandeld not in ('Te behandelen',
                                         'Herberekening afwachten'):
            self.efw_advies_nieuwe_kleur.setEnabled(True)

        if self.feature.attribute('herindiening_bezwaar') == 'true' \
            and advies_behandeld not in ('Te behandelen',
                                         'Herberekening afwachten'):
            self.efw_conform_eerder_advies.setEnabled(True)
        else:
            self.efw_conform_eerder_advies.setValue(0)
            self.efw_conform_eerder_advies.setEnabled(False)

    def _checkSaveable(self, *args):
        """Set the state of the save button depending on our current state.

        Only allow the user to save the feature if all validation passes.

        Parameters
        ----------
        *args : list
            Catchall parameter. All parameters are ignored. This way we make
            sure the function can be called with any (number of) arguments.

        """
        self.btn_save.setEnabled(self._isSaveable())

    def _isSaveable(self):
        """Check if we are in a state that would allow saving.

        Only allow the user to save the feature if all validation passes.

        Returns
        -------
        boolean
            `True` if validation passes and we are good to save, `False`
            otherwise.

        """
        advies_behandeld = self.efwCmb_advies_behandeld.getValue()
        advies_aanvaarding = self.efwCmb_advies_aanvaarding.getValue()
        if advies_behandeld in ('Te behandelen', 'Herberekening afwachten') \
                and advies_aanvaarding is None:
            return True

        return self.efw_advies_nieuwe_kleur.getValue() is not None


class ParcelWindow(QtGui.QMainWindow):
    """Class representing the window to edit a parcel.

    Signals
    -------
    saved : QtCore.pyqtSignal('QgsVectorLayer', 'QString')
        Emitted when the feature has been saved. Includes a reference to the
        layer of the feature and the value of the attribute 'uniek_id'.
    closed : QtCore.pyqtSignal()
        Emitted when the window is closed.
    windowStateChanged : QtCore.pyqtSignal()
        Emitted when the state of the window is changed (i.e. minimized or
        maximize).

    """

    saved = QtCore.pyqtSignal('QgsVectorLayer', 'QString')
    closed = QtCore.pyqtSignal()
    windowStateChanged = QtCore.pyqtSignal()

    def __init__(self, main, layer, parcel):
        """Initialisation.

        Parameters
        ----------
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.
        layer : QGisCore.QgsVectorLayer
            Layer of the feature to edit.
        parcel : QGisCore.QgsFeature
            Feature of the parcel to edit.

        """
        QtGui.QMainWindow.__init__(self, main.iface.mainWindow())
        self.main = main
        self.layer = layer
        self.parcel = parcel

        self.parcelEditWidget = ParcelEditWidget(self, self.main, self.layer,
                                                 self.parcel)
        self.setCentralWidget(self.parcelEditWidget)

        self.setMinimumSize(1200, 1000)

    def closeEvent(self, event):
        """Catch the closeEvent of the window and emit closed signal.

        Parameters
        ----------
        event : QtGui.QCloseEvent
            Event of the closing of the window.

        """
        self.parcelEditWidget.stop()
        self.closed.emit()

    def changeEvent(self, event):
        """Catch the changeEvents of the window and emit windowStateChanged.

        Parameters
        ----------
        event : QtCore.QEvent
            Event of the window.

        """
        if type(event) is QtGui.QWindowStateChangeEvent:
            self.windowStateChanged.emit()
