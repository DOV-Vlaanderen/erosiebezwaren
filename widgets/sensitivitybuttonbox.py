# -*- coding: utf-8 -*-
"""Module containing the SensitivityButton and SensitivityButtonBox classes."""

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


class SensitivityButton(QtGui.QPushButton):
    """Button representing an erosion sensitivity class."""

    def __init__(self, parent, value, label, bgcolor, textcolor):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget for the button.
        value : str
            The erosion class value this button represents.
        label : str
            The text to show as the label on the button.
        bgcolor : str
            Color to use as the background color of the button, in hex format.
            F.ex. '#ffffff' for white.
        textcolor : str
            Color to use for the text (label) on the button, in hex format.
            F.ex. '#ffffff' for white.

        """
        QtGui.QPushButton.__init__(self, label, parent)
        self.value = value
        self.label = label
        self.bgcolor = bgcolor
        self.textcolor = textcolor
        self.parent = parent

        self.setContentsMargins(4, 4, 4, 4)
        self.setMinimumHeight(32)
        self.setCheckable(True)
        self.__setStyleSheet()

        QtCore.QObject.connect(self, QtCore.SIGNAL('clicked(bool)'),
                               self.updateParent)

    def updateParent(self, checked):
        """Update the parent when this button changes state.

        Parameters
        ----------
        checked: boolean
            Current status of this button.

        """
        if checked:
            self.parent.setCheckedButton(self)
        else:
            self.parent.setUnchecked()

    def __setStyleSheet(self):
        """Set the stylesheet for this button."""
        style = "QPushButton {"
        style += "border: 2px solid white;"
        style += "border-radius: 4px;"
        style += "padding: 2px;"
        style += "background-color: #C6C6C6;"
        style += "color: #000000;"
        style += "}"

        style += "QPushButton:checked {"
        style += "background-color: %s;" % self.bgcolor
        style += "color: %s;" % self.textcolor
        style += "}"

        style += "QPushButton:disabled {"
        style += "color: #909090;"
        style += "}"
        self.setStyleSheet(style)


class SensitivityButtonBox(QtGui.QWidget):
    """Widget containing SensitivityButton's for all erosion classes.

    Signals
    -------
    valueChanged : QtCore.pyqtSignal(str)
        Emitted when the value of this widget changed. Contains the new value
        (value of the currently active button) or 'None' when no button
        selected.

    """

    VERWAARLOOSBAAR, ZEERLAAG, LAAG, MEDIUM, HOOG, ZEERHOOG = range(6)
    valueChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget.

        """
        QtGui.QWidget.__init__(self, parent)
        self.layout = QtGui.QGridLayout(self)
        self.setLayout(self.layout)

        self.buttons = [SensitivityButton(
                            self, 'verwaarloosbaar', 'Verwaarloosbaar',
                            '#38a800', '#000000'),
                        SensitivityButton(
                            self, 'zeer laag', 'Zeer laag',
                            '#8ff041', '#000000'),
                        SensitivityButton(
                            self, 'laag', 'Laag',
                            '#ffff00', '#000000'),
                        SensitivityButton(
                            self, 'medium', 'Medium',
                            '#ffaa00', '#000000'),
                        SensitivityButton(
                            self, 'hoog', 'Hoog',
                            '#ff0000', '#ffffff'),
                        SensitivityButton(
                            self, 'zeer hoog', 'Zeer hoog',
                            '#a800e6', '#ffffff')]

        self.valueList = [b.value for b in self.buttons]

        for i in range(len(self.buttons)):
            self.layout.addWidget(self.buttons[i], i / 3, i % 3)

        nvt = SensitivityButton(
            self, 'niet van toepassing', 'Niet van toepassing',
            '#5D5D5D', '#ffffff')
        self.buttons.append(nvt)
        self.layout.addWidget(nvt, 2, 0, 1, 3)

    def setUnchecked(self):
        """Deselect all buttons."""
        for btn in self.buttons:
            btn.setChecked(False)
        self.valueChanged.emit(None)

    def setCheckedButton(self, btn):
        """Deselect all button except the given button.

        Parameters
        ----------
        btn : SensitivityButton
            The button to select. All other button will be deselected.

        """
        for i in range(len(self.buttons)):
            if self.buttons[i] != btn:
                self.buttons[i].setChecked(False)
        self.valueChanged.emit(btn.value)

    def getCheckedButton(self):
        """Get the currently selected button.

        Returns
        -------
        SensitivityButton
            The button that is currently selecter, or None if no button is
            selected.

        """
        for btn in self.buttons:
            if btn.isChecked():
                return btn
        return None

    def getValue(self):
        """Get the value of this widget.

        Returns
        -------
        str
            The value of the selected button, or None if no button is currently
            selected.

        """
        btn = self.getCheckedButton()
        if btn:
            return btn.value
        return None

    def setValue(self, value):
        """Set a new value for this widget, selecting the corresponding button.

        Parameters
        ----------
        value : str or None
            The value of the button to select. Deselect all buttons when None.

        """
        if value == None:
            self.setUnchecked()
        else:
            for btn in self.buttons:
                btn.setChecked(btn.value == value)
            self.valueChanged.emit(value)

    def setEnabled(self, enabled):
        """Enable or disable (all the buttons of) this widget.

        Parameters
        ----------
        enabled : boolean
            The new status of this widget: 'True' to enable, 'False' to
            disable.

        """
        for i in range(len(self.buttons)):
            self.buttons[i].setEnabled(enabled)

    def setMaxValue(self, maxValue):
        """Set the maximum allowed value.

        Parameters
        ----------
        maxValue : str
            Maximum value that the user is allowed to select. All buttons with
            a value higher than this value will be disabled.

        """
        self.setEnabled(False)
        self.buttons[-1].setEnabled(True)

        for i in range(len(self.buttons)-1):
            if self.buttons[i].value == maxValue:
                break
            self.buttons[i].setEnabled(True)

        if self.getValue() not in self.valueList \
                or maxValue not in self.valueList:
            return

        if self.valueList.index(self.getValue()) \
                >= self.valueList.index(maxValue):
            self.setValue(None)
