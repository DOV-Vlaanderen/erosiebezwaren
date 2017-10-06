# -*- coding: utf-8 -*-
"""Module containing classes for custom input widgets.

Contains the classes ValueDateEdit, DefaultValueDateEdit, ValueLineEdit,
ValueCheckBox, ValueBooleanButton, ValueComboBox, ValueMappedComboBox and
ValueTextEdit.
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


class ValueDateEdit(QtGui.QDateEdit):
    """Widget to edit a date in the format 'dd/MM/yyyy'."""

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget.

        """
        QtGui.QDateEdit.__init__(self, parent)
        self.format = 'dd/MM/yyyy'

    def setValue(self, date):
        """Set the value.

        Parameters
        ----------
        date : str
            The date to set the value to, in the format 'dd/MM/yyyy'.

        """
        if date:
            self.setDate(QtCore.QDate.fromString(date, self.format))
        else:
            self.clear()

    def getValue(self):
        """Get the value.

        Returns
        -------
        str
            The date of the widget, in the format 'dd/MM/yyyy'.

        """
        return self.date().toString(self.format)


class DefaultValueDateEdit(QtGui.QDateEdit):
    """Widget to edit a date in the format 'dd/MM/yyyy', with default date."""

    def __init__(self, parent, defaultDate=QtCore.QDate.currentDate()):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget.
        defaultDate : QtCore.QDate, optional
            Date to use as default date, defaults to today.

        """
        QtGui.QDateEdit.__init__(self, parent)
        self.setDate(defaultDate)
        self.format = 'dd/MM/yyyy'

    def setValue(self, date):
        """Set the value.

        Parameters
        ----------
        date : str
            The date to set the value to, in the format 'dd/MM/yyyy'. Use the
            current date when 'None'.

        """
        if date:
            self.setDate(QtCore.QDate.fromString(date, self.format))
        else:
            self.setDate(QtCore.QDate.currentDate())

    def getValue(self):
        """Get the value.

        Returns
        -------
        str
            The date of the widget, in the format 'dd/MM/yyyy'.

        """
        return self.date().toString(self.format)


class ValueLineEdit(QtGui.QLineEdit):
    """Widget to edit text line."""

    def setText(self, text):
        """Set the text.

        Parameters
        ----------
        text : str
            The text to show in the line edit. Set to None to clear the text.

        """
        if text:
            QtGui.QLineEdit.setText(self, text)
        else:
            self.clear()


class ValueCheckBox(QtGui.QCheckBox):
    """Widget to edit a boolean value in a checkbox."""

    def setValue(self, value):
        """Set the value.

        Parameters
        ----------
        value : int
            The new value of the checkbox. Checks the chechbox when 1, uncheck
            otherwise.

        """
        self.setChecked(value == 1)

    def getValue(self):
        """Get the value.

        Returns
        -------
        int
            The value of the checkbox: 1 if it's checked, 0 if it's unchecked.

        """
        if self.isChecked():
            return 1
        return 0


class ValueBooleanButton(QtGui.QPushButton):
    """Widget to map a boolean value to a togglebutton."""

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget.

        """
        QtGui.QPushButton.__init__(self, parent)
        self.setContentsMargins(4, 4, 4, 4)
        self.setMinimumHeight(32)
        self.setCheckable(True)
        self.text = None
        self.__setStyleSheet()
        QtCore.QObject.connect(self, QtCore.SIGNAL('clicked()'),
                               self.__updateValue)

    def setText(self, text):
        """Set the text.

        Parameters
        ----------
        text : str
            The text to show on the button.

        """
        if not self.text:
            self.text = text
        QtGui.QPushButton.setText(self, self.text)

    def setValue(self, value):
        """Set the value, appending 'Ja' or 'Nee' to the text of the button.

        Parameters
        ----------
        value : int
            The value of the button: 1 if it's checked, 0 if it's unchecked.
            Adds 'Ja' to the text of the button if 1, 'Nee' if it's 0.

        """
        if value == 1:
            QtGui.QPushButton.setText(self, self.text + ': Ja')
            self.setChecked(True)
        else:
            QtGui.QPushButton.setText(self, self.text + ': Nee')
            self.setChecked(False)

    def getValue(self):
        """Get the value.

        Returns
        -------
        int
            The value of the button: 1 if it's checked, 0 if it's unchecked.

        """
        if self.isChecked():
            return 1
        return 0

    def __updateValue(self):
        if self.isChecked():
            self.setValue(1)
        else:
            self.setValue(0)

    def __setStyleSheet(self):
        style = "QPushButton {"
        style += "border: 2px solid white;"
        style += "border-radius: 4px;"
        style += "padding: 2px;"
        style += "background-color: #C6C6C6;"
        style += "color: #000000;"
        style += "}"

        style += "QPushButton:checked {"
        style += "background-color: #CBE195;"
        style += "color: #000000;"
        style += "}"

        style += "QPushButton:disabled {"
        style += "color: #909090;"
        style += "}"
        self.setStyleSheet(style)


class ValueComboBox(QtGui.QComboBox):
    """Widget for a combobox."""

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget.

        """
        QtGui.QComboBox.__init__(self, parent)
        self.initialValues = ['']
        self.values = []

    def setValues(self, values):
        """Set the possible values for the combobox.

        Parameters
        ----------
        values : list of str
            The possible values for the combobox.

        """
        self.values = self.initialValues
        self.values.extend(values)
        self.clear()
        self.addItems(self.values)

    def setValue(self, value):
        """Set the current active value for the combobox.

        Parameters
        ----------
        value : str
            Set the active value of the combobox to this value. If the given
            value is not one of the values of the combobox, select the empty
            default value.

        """
        if value and value in self.values:
            self.setCurrentIndex(self.values.index(value))
        else:
            self.setCurrentIndex(-1)

    def getValue(self):
        """Get the value.

        Returns
        -------
        str
            The current value of the combobox.

        """
        if self.currentText():
            return self.currentText()
        return None


class ValueMappedComboBox(QtGui.QComboBox):
    """Widget for a combobox returning values for texts."""

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget.

        """
        QtGui.QComboBox.__init__(self, parent)
        self.values = []
        self.textValueMap = {}
        self.valueTextMap = {}

    def setValues(self, values):
        """Set the possible values for the combobox.

        Parameters
        ----------
        values : list of tuple(2)
            The possible values for the combobox: a list of tuples containing
            the text and a corresponding value.

        """
        self.textValueMap = {}
        self.valueTextMap = {}
        newValues = [('', None)]
        newValues.extend(values)
        self.clear()
        for v in newValues:
            self.addItem(v[0])
            self.values.append(v[0])
            self.textValueMap[v[0]] = v[1]
            self.valueTextMap[v[1]] = v[0]

    def setValue(self, value):
        """Set the current active value for the combobox.

        Sets the text of the combobox to the corresponding text.

        Parameters
        ----------
        value : str
            Set the active value of the combobox to this value. If the given
            value is not one of the values of the combobox, select the empty
            default value.

        """
        if value in self.valueTextMap:
            self.setCurrentIndex(self.values.index(self.valueTextMap[value]))
        else:
            self.setCurrentIndex(0)

    def getValue(self):
        """Get the value.

        Returns
        -------
        str
            The current value of the combobox.

        """
        if self.currentText() in self.textValueMap:
            return self.textValueMap[self.currentText()]
        return None


class ValueTextEdit(QtGui.QPlainTextEdit):
    """Widget to edit text field."""

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget.

        """
        QtGui.QPlainTextEdit.__init__(self, parent)

    def setValue(self, value):
        """Set the value.

        Parameters
        ----------
        value : str or None
            Set the value of the textfield to the this value, or clear the
            textfield when passed None.

        """
        if value:
            self.setPlainText(value)
        else:
            self.clear()

    def getValue(self):
        """Get the value.

        Returns
        -------
        str
            The value of the textfield.

        """
        return self.toPlainText()
