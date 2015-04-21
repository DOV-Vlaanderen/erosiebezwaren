# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import re
import subprocess

from ui_parcelinfowidget import Ui_ParcelInfoWidget
from widgets import valuelabel
from parcelwindow import ParcelWindow
from photodialog import PhotoDialog
from parcellistdialog import ParcelListDialog

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
    def __init__(self, parent, main, layer=None, parcel=None):
        ElevatedFeatureWidget.__init__(self, parent, parcel)
        self.main = main
        self.layer = layer
        self.setupUi(self)

        QObject.connect(self.vwBtn_bezwaarformulier, SIGNAL('clicked(bool)'), self.showPdf_mock)
        QObject.connect(self.btn_edit, SIGNAL('clicked(bool)'), self.showEditWindow)
        QObject.connect(self.btn_zoomto, SIGNAL('clicked(bool)'), self.zoomTo)
        QObject.connect(self.btn_photo, SIGNAL('clicked(bool)'), self.takePhotos)
        QObject.connect(self.btn_anderePercelen, SIGNAL('clicked(bool)'), self.showParcelList)

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

    def showPdf_mock(self):
        cmd = os.environ['COMSPEC'] + ' /c "start %s"'
        path = "C:\\Users\\Elke\\Documents\\qgis\\testpdf.pdf"
        sp = subprocess.Popen(cmd % path)

    def showEditWindow(self):
        p = ParcelWindow(self.main, self.layer, self.feature)
        p.show()

    def zoomTo(self):
        self.layer.removeSelection()
        self.layer.select(self.feature.id())
        self.main.iface.mapCanvas().zoomToSelected(self.layer)
        self.layer.removeSelection()

    def takePhotos(self):
        #cmd = "C:\\Windows\\explorer.exe shell:AppsFolder\\Panasonic.CameraPlus_ehmb8xpdwb7p4!App"
        cmd = os.path.join(os.environ['SYSTEMROOT'], 'explorer.exe')
        cmd += " shell:AppsFolder\\Microsoft.MoCamera_cw5n1h2txyewy!Microsoft.Camera"
        photoPath = os.path.join(os.environ['USERPROFILE'], 'Pictures', 'Camera Roll')

        d = PhotoDialog(self.main.iface, photoPath)

        sp = subprocess.Popen(cmd)
        d.show()

    def showParcelList(self):
        d = ParcelListDialog(self, self.layer, self.feature)
        d.show()

class ParcelInfoDock(QDockWidget):
    def __init__(self, parent):
        QDockWidget.__init__(self, "Bezwaren bodemerosie", parent)
        self.setObjectName("Bezwaren bodemerosie")
        parent.addDockWidget(Qt.RightDockWidgetArea, self)

        QObject.connect(self, SIGNAL('topLevelChanged(bool)'), self.resizeToMinimum)

    def resizeToMinimum(self):
        self.resize(self.minimumSize())

    def toggleVisibility(self):
        self.setVisible(not self.isVisible())
