# -*- coding: utf-8 -*-
"""Module containing classes for custom display widgets.

Contains the classes ValueLabel, SplitMergedValueLabel, ValueMappedLabel,
DefaultValueLabel, AutohideValueLabel, VisibilityBooleanLabel,
InvertedVisibilityBooleanLabel, ColorLabel, SensitivityColorLabel,
AutohideColorValueLabel, DefaultColorValueLabel, EnabledBooleanButton and
VisibilityBooleanButton.
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

import PyQt4.QtGui as QtGui


class ValueLabel(QtGui.QLabel):
    """Label to show a text.

    If it has a buddy widget, hide and show that simultaneously with this
    widget.
    """

    def setText(self, text):
        """Set the text of the label.

        Parameters
        ----------
        text : str or None
            Set the text of the label to this text or clear the label when
            passed None.

        """
        if text:
            QtGui.QLabel.setText(self, unicode(text))
        else:
            self.clear()

    def hide(self):
        """Hide the label.

        If the label has a buddy() widget, hide that as well.
        """
        if self.buddy():
            self.buddy().hide()
        QtGui.QLabel.hide(self)

    def show(self):
        """Show the label.

        If the label has a buddy() widget, show that as well.
        """
        if self.buddy():
            self.buddy().show()
        QtGui.QLabel.show(self)


class SplitMergedValueLabel(QtGui.QLabel):
    """Label to show whether a parcel was split or merged."""

    def setText(self, text):
        """Set the text of the label based on the percentage overlap.

        Parameters
        ----------
        text : float as str
            Percentage of overlap between the old and the new parcel. Expressed
            as a string parsable to float.

        """
        if text and text != '':
            value = float(text)
            if value < 80:
                QtGui.QLabel.setText(self, 'Ja (overlap %0.1f%%)' % value)
            else:
                QtGui.QLabel.setText(self, 'Nee')
            self.show()
        else:
            self.clear()

    def clear(self):
        """Clear and hide the label."""
        self.hide()
        QtGui.QLabel.clear(self)

    def hide(self):
        """Hide the label.

        If the label has a buddy() widget, hide that as well.
        """
        if self.buddy():
            self.buddy().hide()
        QtGui.QLabel.hide(self)

    def show(self):
        """Show the label.

        If the label has a buddy() widget, show that as well.
        """
        if self.buddy():
            self.buddy().show()
        QtGui.QLabel.show(self)


class ValueMappedLabel(ValueLabel):
    """Label to show a text based on a given value."""

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget.

        """
        ValueLabel.__init__(self, parent)
        self.valueTextMap = {}

    def setValues(self, values):
        """Set the text value mapping of this label.

        The label will display the text corresponding to the value.

        Parameters
        ----------
        values : list of tuple(2)
            A list of tuples containing the text and a corresponding value.

        """
        self.valueTextMap.clear()
        for v in values:
            self.valueTextMap[v[1]] = v[0]

    def setValueMap(self, valueMap):
        """Set the text value map to the given dict.

        This is equivaluent to setting the mapping with setValues.

        Parameters
        ----------
        valueMap : dict
            Dictionary mapping the values (as keys) to their corresponding
            texts (as values).

        """
        self.valueTextMap = valueMap

    def setText(self, value):
        """Set the text of the label based on the known mapping and the value.

        Parameters
        ----------
        value : str
            The new value for the label. Sets the text of the label to the
            corresponding text based on the mapping.

        """
        if value in self.valueTextMap:
            QtGui.QLabel.setText(self, unicode(self.valueTextMap[value]))
        else:
            self.clear()


class DefaultValueLabel(QtGui.QLabel):
    """Label to show a fixed default value."""

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget.

        """
        QtGui.QLabel.__init__(self)
        self.defaultValue = None

    def setText(self, text):
        """Set the text of the label.

        The first text to be set will be the default value too.

        Parameters
        ----------
        text : str or None
            Set the text of the label to this text or set the default text when
            passed None.

        """
        if not self.defaultValue:
            self.defaultValue = text

        if text:
            QtGui.QLabel.setText(self, text)
        elif self.defaultValue:
            QtGui.QLabel.setText(self, self.defaultValue)
        else:
            self.clear()


class AutohideValueLabel(ValueLabel):
    """ValueLabel that hides when no text is to be shown.

    If it has a buddy widget, hide and show that simultaneously with this
    widget.
    """

    def setText(self, text):
        """Set the text of the label.

        Parameters
        ----------
        text : str or None
            Set the text of the label to this text. Hide the label when
            passed None, show the label when passed anything else.

        """
        ValueLabel.setText(self, text)
        if text:
            self.show()
        else:
            self.hide()

    def clear(self):
        """Clear and hide the label."""
        self.hide()
        ValueLabel.clear(self)


class VisibilityBooleanLabel(QtGui.QLabel):
    """Label that shows and hides itself if being passed a value.

    This label shows its default text when passed a value different from None
    and hides itself when passed None.
    """

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget.

        """
        QtGui.QLabel.__init__(self, parent)
        self.fixedText = None

    def setText(self, text):
        """Set the text of the label.

        Parameters
        ----------
        text : str or None
            The first time this is called: set the text of the label to this
            text.
            All the following times: Hide the label when passed None, show the
            label when passed anything else.

        """
        if not self.fixedText:
            self.fixedText = text
            QtGui.QLabel.setText(self, self.fixedText)

        if text:
            self.show()
        else:
            self.hide()


class InvertedVisibilityBooleanLabel(QtGui.QLabel):
    """Label that shows and hides itself if being passed a value.

    This label shows its default text when passed None and hides itself when
    passed any other value. This is the inverse of the VisibilityBooleanLabel.
    """

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget.

        """
        QtGui.QLabel.__init__(self, parent)
        self.fixedText = None

    def setText(self, text):
        """Set the text of the label.

        Parameters
        ----------
        text : str or None
            The first time this is called: set the text of the label to this
            text.
            All the following times: Show the label when passed None, hide the
            label when passed anything else.

        """
        if not self.fixedText:
            self.fixedText = text
            QtGui.QLabel.setText(self, self.fixedText)

        if text:
            self.hide()
        else:
            self.show()


class ColorLabel(QtGui.QLabel):
    """Displays a text with a certain background color."""

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget.

        """
        QtGui.QLabel.__init__(self, parent)
        self.fixedText = None
        self.colorMap = {}

    def setColorMap(self, colorMap):
        """Set the color map to use. This maps texts to tuples with colors.

        Parameters
        ----------
        colorMap : dict of <str,tuple(2)>
            Dictionary mapping texts (as keys) to tuples containing background
            color and text color respectively (as hex values, f.ex. '#ffffff'
            for white).

        """
        self.colorMap = colorMap

    def setText(self, text, forceText=False):
        """Set the text of the label and adjust the colors accordingly.

        Parameters
        ----------
        text : str
            The first time this is called: set the default text of the label to
            this text. All the following times: set this text when
            forceText=True, else set the default text.
            Changes the colors according to this parameter, regardless of the
            value of forceText.
        forceText : boolean, optional
            If True: show the text passed as 'text', if False show the default
            text. Defaults to False.

        """
        if not self.fixedText:
            self.fixedText = text
            QtGui.QLabel.setText(self, self.fixedText)

        if forceText:
            QtGui.QLabel.setText(self, text)
        else:
            QtGui.QLabel.setText(self, self.fixedText)

        bgcolor, textcolor = self.colorMap.get(text, ('#c6c6c6', '#000000'))
        self._setStyleSheet(bgcolor, textcolor)

    def _setStyleSheet(self, bgcolor, textcolor):
        style = "* {"
        style += "border-radius: 4px;"
        style += "padding: 4px;"
        style += "background-color: %s;" % bgcolor
        style += "color: %s;" % textcolor
        style += "}"
        self.setStyleSheet(style)


class SensitivityColorLabel(ColorLabel):
    """Custom ColorLabel with a default colorMap for erosion classes."""

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget.

        """
        ColorLabel.__init__(self, parent)

        self.colorMap = {'verwaarloosbaar': ('#38a800', '#000000'),
                         'zeer laag': ('#8ff041', '#000000'),
                         'laag': ('#ffff00', '#000000'),
                         'medium': ('#ffaa00', '#000000'),
                         'hoog': ('#ff0000', '#ffffff'),
                         'zeer hoog': ('#a800e6', '#ffffff'),
                         'niet van toepassing': ('#5D5D5D', '#ffffff')}


class AutohideColorValueLabel(AutohideValueLabel, ColorLabel):
    """Displays a text with a color that hides when no text is to be shown."""

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget.

        """
        ColorLabel.__init__(self, parent)
        del(self.fixedText)

    def setText(self, text):
        """Set the text of the label.

        Parameters
        ----------
        text : str or None
            Set the text of the label to this text. Hide the label when
            passed None, show the label when passed anything else.
            Changes the colors according to this text and the colorMap.

        """
        AutohideValueLabel.setText(self, text)
        bgcolor, textcolor = self.colorMap.get(text, ('#c6c6c6', '#000000'))
        self._setStyleSheet(bgcolor, textcolor)


class DefaultColorValueLabel(DefaultValueLabel, ColorLabel):
    """Label to show a fixed default value but allows changing the color."""

    def __init__(self, parent):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as the parent widget.

        """
        ColorLabel.__init__(self, parent)
        DefaultValueLabel.__init__(self, parent)
        self.defaultColors = ('#c6c6c6', '#000000')
        del(self.fixedText)

    def setText(self, text):
        """Set the text of the label.

        The first text to be set will be the default value too.

        Parameters
        ----------
        text : str or None
            Set the text of the label to this text or set the default text when
            passed None. Changes the colors according to this parameter,
            regardless of the default text.

        """
        DefaultValueLabel.setText(self, text)
        bgcolor, textcolor = self.colorMap.get(text, self.defaultColors)
        self._setStyleSheet(bgcolor, textcolor)


class EnabledBooleanButton(QtGui.QPushButton):
    """A button that is enabled/disabled based on the presence of a value."""

    def setValue(self, value):
        """Enable or disable the button.

        Parameters
        ----------
        value : str or None
            Disable the button if passed None, enable the button if passed any
            other value.

        """
        if value:
            self.setEnabled(True)
        else:
            self.setEnabled(False)


class EnabledFlatBooleanButton(QtGui.QPushButton):
    """A button that is enabled and flat based on the presence of a value."""

    def setValue(self, value):
        """Enable or disable the button and set its status to flat.

        Parameters
        ----------
        value : str or None
            Disable and set the button to flat if passed None, enable and set
            the button to non-flat if passed any other value.

        """
        if value:
            self.setEnabled(True)
            self.setFlat(False)
        else:
            self.setEnabled(False)
            self.setFlat(True)


class VisibilityBooleanButton(QtGui.QPushButton):
    """A button that is visible based on the presence of a value."""

    def setValue(self, value):
        """Show or hide the button.

        Parameters
        ----------
        value : str or None
            Show the button if the value is not None or equals 'false' (case-
            insensitive), and hide the button otherwise.

        """
        if value and value.lower() != "false":
            self.show()
        else:
            self.hide()
