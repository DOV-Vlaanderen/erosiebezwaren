# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_parcelinfowidget import Ui_ParcelInfoWidget
from widgets import valuelabel

class ElevatedFeatureWidget(QWidget):
    def __init__(self, parent, feature=None):
        QWidget.__init__(self, parent)
        self.feature = feature
        self.fieldMap = {}

    def _setValue(self, widget, value):
        fnSetValue = None

        if type(widget) in (QLabel, valuelabel.AutohideValueLabel):
            fnSetValue = type(widget).setText

        if fnSetValue:
            fnSetValue(widget, value)

    def _mapWidgets(self, fields):
        for field in fields:
            fieldName = field.name()
            if 'vw_%s' % fieldName.lower() in self.__dict__:
                self.fieldMap[fieldName] = self.__dict__['vw_%s' % fieldName.lower()]

    def populate(self):
        if self.feature:
            if len(self.fieldMap) < 1:
                self._mapWidgets(self.feature.fields())

            for field in self.feature.fields():
                widget = self.fieldMap.get(field.name(), None)
                if widget:
                    self._setValue(widget, self.feature.attribute(field.name()))

    def setFeature(self, feature):
        self.feature = feature
        self.populate()

class ParcelInfoWidget(ElevatedFeatureWidget, Ui_ParcelInfoWidget):
    def __init__(self, parent, parcel=None):
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.setupUi(self)
        self.populate()

    def populate(self):
        ElevatedFeatureWidget.populate(self)
        if self.feature:
            self.showInfo()
        else:
            self.clear()

    def clear(self):
        self.lb_geenselectie.show()
        self.infoWidget.hide()

    def showInfo(self):
        self.infoWidget.show()
        self.lb_geenselectie.hide()

class ParcelInfoDock(QDockWidget):
    def __init__(self, parent):
        QDockWidget.__init__(self, "Perceelsinformatie", parent)
        self.setObjectName("Perceelsinformatie")
        parent.addDockWidget(Qt.RightDockWidgetArea, self)

        QObject.connect(self, SIGNAL('topLevelChanged(bool)'), self.resizeToMinimum)

    def resizeToMinimum(self):
        self.resize(self.minimumSize())

    def toggleVisibility(self):
        self.setVisible(not self.isVisible())
