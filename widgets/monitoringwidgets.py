# -*- coding: utf-8 -*-
"""Module containing the widgets of the erosion monitoring dialog.

Contains the classes MonitoringItemWidget, CheckableCell, BasisPakketWidget,
TeeltTechnischWidget, BufferStrookHellingWidget.
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

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui


class MonitoringItemWidget(QtGui.QWidget):
    """Subclass of a QtGui.QWidget adding an extra 'valueChanged' signal.

    Signals
    -------
    valueChanged : QtCore.pyqtSignal()
        Emitted when (one of) the value(s) of the widget changed.
    """

    valueChanged = QtCore.pyqtSignal()

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            The widget to use as the parent widget.

        """
        QtGui.QWidget.__init__(self, parent)


class CheckableCell(QtGui.QPushButton):
    """Class for a button with boolean states.

    It shows an 'X' when selected, or empty when not selected.
    """

    def __init__(self, objectName, label, parent):
        """Initialisation.

        Parameters
        ----------
        objectName : str
            The name to use as objectName of the widget.
        label : str
            The label to use as default label.
        parent : QtGui.QWidget
            The widget to use as parent widget.

        """
        QtGui.QPushButton.__init__(self, label, parent)
        self.setObjectName(objectName)

        self.setCheckable(True)
        self.__setStyleSheet()

        QtCore.QObject.connect(self, QtCore.SIGNAL('clicked()'),
                               self.__updateValue)

    def setValue(self, checked):
        """Update the value of the cell.

        Parameters
        ----------
        checked : boolean
            The new value of the cell.

        """
        self.setChecked(checked)
        self.setText('X') if checked else self.setText('')

    def __updateValue(self):
        """Update the value of the cell based on its 'checked' status."""
        self.setValue(self.isChecked())

    def __setStyleSheet(self):
        """Set the stylesheet for the QPushButton."""
        style = "QPushButton, QPushButton:checked, "
        style += "QPushButton:disabled {"
        style += "border: none;"
        style += "background-color: white;"
        style += "border-radius: 4px;"
        style += "padding: 2px;"
        style += "}"

        style += "QPushButton:disabled {"
        style += "background-color: none;"
        style += "}"
        self.setStyleSheet(style)


class BasisPakketWidget(MonitoringItemWidget):
    """Class for the widget for the 'basispakket' set."""

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use a parent widget.

        """
        MonitoringItemWidget.__init__(self, parent)

        self.layout = QtGui.QGridLayout(self)
        self.setLayout(self.layout)

        self.horMaxSizePolicy = QtGui.QSizePolicy()
        self.horMaxSizePolicy.setHorizontalPolicy(QtGui.QSizePolicy.Maximum)

        self.geenMtrglEnabled = True

        self.options = [
            ('groen', 'Groenbedekker'),
            ('voor112', 'Teelt voor 1/12'),
            ('nietkerend', 'Niet-kerende'),
            ('ploegen', 'Ploegen'),
            ('mulch', 'Mulch'),
            ('resten', 'Teeltresten'),
            ('geenmtrgl', 'Geen maatregel'),
            ('geeninfo', 'Geen info')
        ]

        self.periods = [
            ('voor', 'Voor hoofdteelt'),
            ('na', 'Na hoofdteelt')
        ]

        self.cells = dict(zip([p[0] for p in self.periods],
                              [{} for i in range(len(self.periods))]))

        for i in range(len(self.periods)):
            label = QtGui.QLabel(self.periods[i][1])
            label.setSizePolicy(self.horMaxSizePolicy)
            self.layout.addWidget(label, 0, i+1)

        for i in range(len(self.options)):
            label = QtGui.QLabel(self.options[i][1])
            label.setSizePolicy(self.horMaxSizePolicy)
            self.layout.addWidget(label, i+1, 0)

        for i in range(len(self.options)):
            for j in range(len(self.periods)):
                option = self.options[i]
                period = self.periods[j]
                cell = CheckableCell('%s_%s' % (period[0], option[0]), '',
                                     self)
                QtCore.QObject.connect(cell, QtCore.SIGNAL('toggled(bool)'),
                                       self._validate)
                QtCore.QObject.connect(cell, QtCore.SIGNAL('toggled(bool)'),
                                       lambda x: self.valueChanged.emit())
                self.cells[period[0]][option[0]] = cell
                self.layout.addWidget(self.cells[period[0]][option[0]],
                                      i+1, j+1)

    def _validate(self, *args):
        """Validate the values of this widget."""
        for p in self.periods:
            geenChecked = [self.cells[p[0]][i] for i in self.cells[p[0]]
                           if i.startswith('geen') and
                           self.cells[p[0]][i].isChecked()]
            geenMtrgl = [self.cells[p[0]][i] for i in self.cells[p[0]]
                         if i == 'geenmtrgl'][0]
            if len(geenChecked) > 0:
                for c in self.cells[p[0]].values():
                    if c != geenChecked[0]:
                        c.setValue(False)
                        c.setEnabled(False)
            else:
                for c in self.cells[p[0]].values():
                    if not self.geenMtrglEnabled and c == geenMtrgl:
                        c.setEnabled(False)
                    else:
                        c.setEnabled(True)

    def setGeenMtrglEnabled(self, enabled):
        """Enable or disable 'geen maatregelen'.

        Parameters
        ----------
        enabled : boolean
            Whether to enable (True) or disable (False) the 'geen maatregelen'
            option.

        """
        self.geenMtrglEnabled = enabled
        self._validate()

    def setValue(self, value):
        """Set the value of the subwidgets based on the given feature value.

        Parameters
        ----------
        value : str
            List of objectNames of cells to check, separated by ';'.

        """
        if value:
            ls = [i.strip() for i in value.strip().split(';')]
        else:
            ls = []

        for p in self.cells:
            for o in self.cells[p]:
                self.cells[p][o].setValue('%s_%s' % (p, o) in ls)

    def getValue(self):
        """Get the value of this widget, which is a list of checked cells.

        Returns
        -------
        str
            List of objectNames of checked subwidgets, separated by '; '.

        """
        return '; '.join(
            sorted(['voor_'+c for c in self.cells['voor']
                    if self.cells['voor'][c].isChecked()]) +
            sorted(['na_'+c for c in self.cells['na']
                    if self.cells['na'][c].isChecked()])
        )


class TeeltTechnischWidget(MonitoringItemWidget):
    """Class for the widget for the 'teelttechnisch' set."""

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use a parent widget.

        """
        MonitoringItemWidget.__init__(self, parent)

        self.layout = QtGui.QGridLayout(self)
        self.setLayout(self.layout)

        self.options = [
            ('nietkerend', 'Niet-kerende'),
            ('directinzaai', 'Direct inzaai'),
            ('strip-till', 'Strip-till'),
            ('drempeltjes', 'Drempeltjes'),
            ('bioaardappel', 'Bio-aardappel'),
            ('diepetandbew', 'Diepe tandbewerking'),
            ('hoogtelijnen', 'Hoogtelijnen'),
            ('graszones', 'Graszones'),
            ('geenmtrgl', 'Geen maatregel'),
            ('geeninfo', 'Geen info')
        ]

        self.cells = {}
        self.disabledCells = []

        for i in range(len(self.options)):
            self.layout.addWidget(QtGui.QLabel(self.options[i][1]), i+1, 0)

        for i in range(len(self.options)):
            option = self.options[i]
            cell = CheckableCell(option[0], '', self)
            QtCore.QObject.connect(cell, QtCore.SIGNAL('toggled(bool)'),
                                   self._validate)
            QtCore.QObject.connect(cell, QtCore.SIGNAL('toggled(bool)'),
                                   lambda x: self.valueChanged.emit())
            self.cells[option[0]] = cell
            self.layout.addWidget(self.cells[option[0]], i+1, 1)

    def _validate(self, *args):
        """Validate the values of this widget."""
        geenChecked = [self.cells[i] for i in self.cells
                       if i.startswith('geen') and self.cells[i].isChecked()]
        if len(geenChecked) > 0:
            for c in self.cells.values():
                if c != geenChecked[0]:
                    c.setValue(False)
                    c.setEnabled(False)
        else:
            for c in self.cells:
                if c in self.disabledCells:
                    self.cells[c].setValue(False)
                    self.cells[c].setEnabled(False)
                else:
                    self.cells[c].setEnabled(True)

    def setValue(self, value):
        """Set the value of the subwidgets based on the given feature value.

        Parameters
        ----------
        value : str
            List of options to check, separated by ';'.

        """
        if value:
            ls = [i.strip() for i in value.strip().split(';')]
        else:
            ls = []

        for p in self.cells:
            self.cells[p].setValue(p in ls)

    def getValue(self):
        """Get the value of this widget, which is a list of checked options.

        Returns
        -------
        str
            List of objectNames of checked subwidgets, separated by '; '.

        """
        return '; '.join(sorted([c for c in self.cells
                                 if self.cells[c].isChecked()]))

    def setDisabledOptions(self, options):
        """Set the options which are to be disabled.

        Parameters
        ----------
        options : set of str
            Set of option names to be disabled.

        """
        self.disabledCells = options
        self._validate()


class BufferStrookHellingWidget(MonitoringItemWidget):
    """Class for the widget for the 'bufferstrook helling' set."""

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use a parent widget.

        """
        MonitoringItemWidget.__init__(self, parent)

        self.layout = QtGui.QVBoxLayout(self)
        self.setLayout(self.layout)

        self.options = [
            ['Uniform', ['Parallel', 'Waterscheiding', 'Schuin']],
            ['1 droge vallei', []],
            ['Complex', []]
        ]

        self.widgets = {}

        gb = QtGui.QGroupBox(self)
        bg = QtGui.QButtonGroup(self)
        gb.setLayout(QtGui.QVBoxLayout(gb))
        self.layout.addWidget(gb)

        for i in self.options:
            radio = QtGui.QRadioButton(i[0], gb)
            QtCore.QObject.connect(radio, QtCore.SIGNAL('toggled(bool)'),
                                   self._updateParentChild)
            QtCore.QObject.connect(radio, QtCore.SIGNAL('toggled(bool)'),
                                   lambda x: self.valueChanged.emit())
            gb.layout().addWidget(radio)
            bg.addButton(radio)
            bgx = None

            if len(i[1]) > 0:
                gbx = QtGui.QGroupBox(gb)
                bgx = QtGui.QButtonGroup(gb)
                gbx.setLayout(QtGui.QVBoxLayout(gbx))
                for j in i[1]:
                    radiox = QtGui.QRadioButton(j, gbx)
                    radiox.setEnabled(False)
                    QtCore.QObject.connect(radiox,
                                           QtCore.SIGNAL('toggled(bool)'),
                                           self._updateParentChild)
                    QtCore.QObject.connect(radiox,
                                           QtCore.SIGNAL('toggled(bool)'),
                                           lambda x: self.valueChanged.emit())
                    self.widgets[j] = (radiox, None, radio)
                    gbx.layout().addWidget(radiox)
                    bgx.addButton(radiox)

                gb.layout().addWidget(gbx)

            self.widgets[i[0]] = (radio, bgx, None)

    def _updateParentChild(self, toggled):
        """Update the toggled status of other widgets.

        Parameters
        ----------
        toggled : boolean
            The current status of the widget triggering this slot.

        """
        if toggled:
            w = self.widgets[self.sender().text()]
            if w[1]:
                for b in w[1].buttons():
                    b.setEnabled(True)
        else:
            w = self.widgets[self.sender().text()]
            if w[1]:
                w[1].setExclusive(False)
                for b in w[1].buttons():
                    b.setChecked(False)
                    b.setEnabled(False)
                w[1].setExclusive(True)

    def getValue(self):
        """Get the value of this widget.

        Returns
        -------
        str
            The current value of this widget.

        """
        checkedWidgets = [w[0] for w in self.widgets.values() if (
            w[0].isChecked() and w[0].isEnabled()
            and w[0].text() != 'Uniform')]

        if len(checkedWidgets) == 1:
            return checkedWidgets[0].text()

    def setValue(self, value):
        """Set the value of the widget to the given value.

        Parameters
        ----------
        value : str
            Value to check.

        """
        if value:
            self.widgets[value][0].setChecked(True)

        if value in ('Parallel', 'Waterscheiding', 'Schuin'):
            self.widgets['Uniform'][0].setChecked(True)
