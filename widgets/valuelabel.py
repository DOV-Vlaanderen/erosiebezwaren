# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

class ValueLabel(QLabel):
    def setText(self, text):
        if text:
            QLabel.setText(self, unicode(text))
        else:
            self.clear()

class ValueMappedLabel(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.valueTextMap = {}

    def setValues(self, values):
        self.valueTextMap.clear()
        for v in values:
            self.valueTextMap[v[1]] = v[0]

    def setValueMap(self, valueMap):
        self.valueTextMap = valueMap

    def setText(self, value):
        if value in self.valueTextMap:
            QLabel.setText(self, unicode(self.valueTextMap[value]))
        else:
            self.clear()

class DefaultValueLabel(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self)
        self.defaultValue = None

    def setText(self, text):
        if not self.defaultValue:
            self.defaultValue = text

        if text:
            QLabel.setText(self, text)
        elif self.defaultValue:
            QLabel.setText(self, self.defaultValue)
        else:
            self.clear()

class AutohideValueLabel(ValueLabel):
    def setText(self, text):
        ValueLabel.setText(self, text)
        if text:
            self.show()

    def clear(self):
        self.hide()
        ValueLabel.clear(self)

    def hide(self):
        if self.buddy():
            self.buddy().hide()
        ValueLabel.hide(self)

    def show(self):
        if self.buddy():
            self.buddy().show()
        ValueLabel.show(self)

class VisibilityBooleanLabel(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.fixedText = None

    def setText(self, text):
        if not self.fixedText:
            self.fixedText = text
            QLabel.setText(self, self.fixedText)

        if text:
            self.show()
        else:
            self.hide()

class ColorLabel(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.fixedText = None
        self.colorMap = {}

    def setColorMap(self, colorMap):
        self.colorMap = colorMap

    def setText(self, text):
        if not self.fixedText:
            self.fixedText = text
            QLabel.setText(self, self.fixedText)

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
    def __init__(self, parent):
        ColorLabel.__init__(self, parent)

        self.colorMap = {'verwaarloosbaar': ('#38a800', '#000000'),
                         'zeer laag': ('#8ff041', '#000000'),
                         'laag': ('#ffff00', '#000000'),
                         'medium': ('#ffaa00', '#000000'),
                         'hoog': ('#ff0000', '#ffffff'),
                         'zeer hoog': ('#a800e6', '#ffffff')}

class AutohideColorValueLabel(AutohideValueLabel, ColorLabel):
    def __init__(self, parent):
        ColorLabel.__init__(self, parent)
        del(self.fixedText)

    def setText(self, text):
        AutohideValueLabel.setText(self, text)
        bgcolor, textcolor = self.colorMap.get(text, ('#c6c6c6', '#000000'))
        self._setStyleSheet(bgcolor, textcolor)

class DefaultColorValueLabel(DefaultValueLabel, ColorLabel):
    def __init__(self, parent):
        ColorLabel.__init__(self, parent)
        DefaultValueLabel.__init__(self, parent)
        del(self.fixedText)

    def setText(self, text):
        DefaultValueLabel.setText(self, text)
        bgcolor, textcolor = self.colorMap.get(text, ('#c6c6c6', '#000000'))
        self._setStyleSheet(bgcolor, textcolor)

class EnabledBooleanButton(QPushButton):
    def setValue(self, value):
        if value:
            self.setEnabled(True)
        else:
            self.setEnabled(False)
