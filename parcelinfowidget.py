# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import re
import subprocess

from ui_parcelinfowidget import Ui_ParcelInfoWidget
from widgets import valuelabel

class ElevatedFeatureWidget(QWidget):
    def __init__(self, parent, feature=None):
        QWidget.__init__(self, parent)
        self.feature = feature
        self.fieldMap = {}
        self.mapRegex = re.compile(r'^vw_.*_(.*)$')

    def _setValue(self, widget, value):
        fnSetValue = None

        if issubclass(type(widget), QLabel):
            fnSetValue = widget.setText
        elif issubclass(type(widget), valuelabel.EnabledBooleanButton):
            fnSetValue = widget.setValue

        if fnSetValue:
            fnSetValue(value)

    def _mapWidgets(self, fields):
        for field in fields:
            fieldName = field.name()
            regex = re.compile(r'^vw[^_]*_%s$' % fieldName, re.I)
            for dictfield in self.__dict__:
                if regex.match(dictfield):
                    if fieldName not in self.fieldMap:
                        self.fieldMap[fieldName] = set()
                    self.fieldMap[fieldName].add(self.__dict__[dictfield])

    def populate(self):
        if self.feature:
            if len(self.fieldMap) < 1:
                self._mapWidgets(self.feature.fields())

            for field in self.feature.fields():
                widgets = self.fieldMap.get(field.name(), [])
                for w in widgets:
                    self._setValue(w, self.feature.attribute(field.name()))

    def setFeature(self, feature):
        self.feature = feature
        self.populate()

class ParcelInfoWidget(ElevatedFeatureWidget, Ui_ParcelInfoWidget):
    def __init__(self, parent, parcel=None):
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.setupUi(self)

        QObject.connect(self.vw_btn_pdf, SIGNAL('triggered(bool)'), self.showPdf)

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

    def showPdf(self):
        if self.feature.attribute('bezwaarformulier'):
            cmd = os.environ['COMSPEC'] + ' /c "start %s"'
            sp = subprocess.Popen(cmd % self.feature.attribute('bezwaarformulier'))

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
