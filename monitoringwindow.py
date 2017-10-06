# -*- coding: utf-8 -*-
"""Module containing the MonitoringWindow and MonitoringWidget classes."""

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

from ui_monitoringwidget import Ui_MonitoringWidget
from widgets.elevatedfeaturewidget import ElevatedFeatureWidget
from widgets.monitoringwidgets import BasisPakketWidget
from widgets.monitoringwidgets import BufferStrookHellingWidget
from widgets.monitoringwidgets import TeeltTechnischWidget
from widgets.valueinput import ValueComboBox


class MonitoringWidget(ElevatedFeatureWidget, Ui_MonitoringWidget):
    """Class grouping the three monitoringwidgets into one widget.

    This widget is used as central widget in the MonitoringWindow to edit the
    monitoring fields for a specific parcel.
    """

    def __init__(self, parent, main, feature, layer):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QMainWindow
            Parent window of this widget.
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.
        feature : QGisCore.QgsFeature
            Parcel to edit monitoring for.
        layer : QGisCore.QgsVectorLayer
            Layer to save the changed fields to.

        """
        ElevatedFeatureWidget.__init__(self, parent)
        self.main = main
        self.feature = feature
        self.layer = layer
        self.setupUi(self)

        QtCore.QObject.connect(self.btn_save, QtCore.SIGNAL('clicked()'),
                               self.save)
        QtCore.QObject.connect(self.btn_cancel, QtCore.SIGNAL('clicked()'),
                               self.stop)

        self.lbv_header.setText('Bewerk monitoring voor perceel %s\n  van %s'
                                % (self.feature.attribute('uniek_id'),
                                   self.feature.attribute('naam')))

        self.efw_basispakket = BasisPakketWidget(self)
        self.efw_basispakket.setGeenMtrglEnabled(self.feature.attribute(
            'landbouwer_aanwezig') == 1)
        self.lyt_basispakket.addWidget(self.efw_basispakket)

        label = QtGui.QLabel('Hellingtype', self)
        self.lyt_bufferstrook.addWidget(label)
        self.efw_bufferstrook_helling = BufferStrookHellingWidget(self)
        self.lyt_bufferstrook.addWidget(self.efw_bufferstrook_helling)

        label = QtGui.QLabel('Maatregel', self)
        self.lyt_bufferstrook.addWidget(label)
        self.efw_bufferstrook_mtrgl = ValueComboBox(self)
        self.efw_bufferstrook_mtrgl.initialValues = []
        self.efw_bufferstrook_mtrgl.setValues([
            'Standaardinvulling',
            'Attest',
            'Onvoldoende invulling',
            'Geen maatregel',
            'Geen info'
        ])
        self.lyt_bufferstrook.addWidget(self.efw_bufferstrook_mtrgl)

        self.efw_teelttechnisch = TeeltTechnischWidget(self)
        self.lyt_teelttechnisch.addWidget(self.efw_teelttechnisch)

        self.populate()
        self.connectValidators()

    def save(self):
        """Save the changes made to the feature to the layer.

        If we were able to save succesfully, close the window by calling
        `stop`.
        """
        if self.feature:
            success = self.saveFeature()
            if success:
                self.stop()

    def stop(self):
        """Close the parent window."""
        self.btn_save.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        QtCore.QCoreApplication.processEvents()
        self.btn_save.repaint()
        self.btn_cancel.repaint()
        self.parent.close()

    def connectValidators(self):
        """Connect validation to the changed signals of the entry widgets."""
        QtCore.QObject.connect(
            self.efw_basispakket,
            QtCore.SIGNAL('valueChanged()'), self._validate)
        QtCore.QObject.connect(
            self.efw_bufferstrook_helling,
            QtCore.SIGNAL('valueChanged()'), self._validate)
        QtCore.QObject.connect(
            self.efw_bufferstrook_mtrgl,
            QtCore.SIGNAL('currentIndexChanged(int)'), self._validate)
        QtCore.QObject.connect(
            self.efw_teelttechnisch,
            QtCore.SIGNAL('valueChanged()'), self._validate)
        self._validate()

    def _validate(self, *args):
        """Validate.

        Change the value of certain widgets depending on the value of others.
        """
        disabledOptions = set()

        if 'voor_groen' not in self.efw_basispakket.getValue():
            disabledOptions |= set(['directinzaai', 'strip-till'])

        if 'voor_ploegen' in self.efw_basispakket.getValue():
            disabledOptions |= set(['nietkerend', 'directinzaai',
                                    'strip-till'])

        self.efw_teelttechnisch.setDisabledOptions(disabledOptions)

        self._checkSaveable()

    def _checkSaveable(self, *args):
        """Enable or disable the save button according to the validation.

        Only allows saving if all widgets validate.
        """
        self.btn_save.setEnabled(self._isSaveable())

    def _isSaveable(self):
        """Check whether we are allowed to save.

        Returns
        -------
        boolean
            True if validation succeeded and we can save the feature, False if
            validation failed and we should correct before being allowed to
            save.

        """
        return \
            len(set([i.strip().split('_')[0] for i in
                     self.efw_basispakket.getValue().split(';')])) == 2 and \
            self.efw_bufferstrook_helling.getValue() is not None and \
            self.efw_bufferstrook_mtrgl.getValue() is not None and \
            self.efw_teelttechnisch.getValue() != ''


class MonitoringWindow(QtGui.QMainWindow):
    """Window showing the MonitoringWidget for a specific field."""

    closed = QtCore.pyqtSignal()

    def __init__(self, main, feature, layer):
        """Initialisation.

        Parameters
        ----------
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.
        feature : QGisCore.QgsFeature
            Parcel to edit monitoring for.
        layer : QGisCore.QgsVectorLayer
            Layer to save the changed fields to.

        """
        QtGui.QMainWindow.__init__(self, main.iface.mainWindow())
        self.main = main
        self.feature = feature
        self.layer = layer

        self.setWindowTitle('Bewerk monitoring %s' % self.feature.attribute(
            'uniek_id'))

        self.monitoringWidget = MonitoringWidget(self, self.main, self.feature,
                                                 self.layer)
        self.setCentralWidget(self.monitoringWidget)

        self.setMinimumSize(800, 1000)

    def closeEvent(self, event):
        """Emit the closed signal on closing of the window."""
        self.closed.emit()
