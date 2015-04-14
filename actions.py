# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os
import subprocess
import time

import photodialog

from parcelidentifier import ParcelIdentifyAction

class MapViewGroup(QToolButton):
    def __init__(self, main, text, parent):
        QToolButton.__init__(self, parent)
        self.main = main
        self.setText(text)
        self.setPopupMode(self.InstantPopup)
        self.menu = QMenu(self)
        self.setMenu(self.menu)

    def addMapView(self, name, layersEnabled, layersDisabled):
        action = QAction(name, self.menu)
        QObject.connect(action, SIGNAL('triggered(bool)'),
            lambda x: self.main.utils.toggleLayersGroups(layersEnabled, layersDisabled))
        self.menu.addAction(action)

class Actions(object):
    def __init__(self, main, parent):
        self.main = main
        self.parent = parent

    def annotateArrow(self, start):
        if start:
            self.main.utils.editInLayer('Pijlen')
        else:
            self.main.utils.stopEditInLayer('Pijlen')

    def takePhotos(self):
        def save(result):
            if result == QDialog.Accepted:
                print "Photos have been saved"
            elif result == QDialog.Rejected:
                print "Photos NOT SAVED"

        #cmd = "C:\\Windows\\explorer.exe shell:AppsFolder\\Panasonic.CameraPlus_ehmb8xpdwb7p4!App"
        cmd = os.path.join(os.environ['SYSTEMROOT'], 'explorer.exe')
        cmd += " shell:AppsFolder\\Microsoft.MoCamera_cw5n1h2txyewy!Microsoft.Camera"
        photoPath = os.path.join(os.environ['USERPROFILE'], 'Pictures', 'Camera Roll')

        d = photodialog.PhotoDialog(self.main.iface, photoPath)
        QObject.connect(d, SIGNAL('finished(int)'), save)

        sp = subprocess.Popen(cmd)
        d.show()

    def showPdf(self, path=None):
        cmd = os.environ['COMSPEC'] + ' /c "start %s"'
        if not path:
            path = "C:\\Users\\Elke\\Documents\\qgis\\testpdf.pdf"
        sp = subprocess.Popen(cmd % path)

    def showKeyboard(self):
        cmd = os.path.join(os.environ['COMMONPROGRAMFILES'], 'microsoft shared', 'ink', 'TabTip.exe')
        sp = subprocess.Popen(cmd, env=os.environ, shell=True)

    def addToToolbar(self, toolbar):
        annotateArrow = QAction('APY', self.parent)
        annotateArrow.setCheckable(True)
        QObject.connect(annotateArrow, SIGNAL('triggered(bool)'), self.annotateArrow)
        toolbar.addAction(annotateArrow)

        takePhotos = QAction('PHO', self.parent)
        QObject.connect(takePhotos, SIGNAL('triggered(bool)'), self.takePhotos)
        toolbar.addAction(takePhotos)

        loketOverzichtskaart = MapViewGroup(self.main, 'OZK', toolbar)
        loketOverzichtskaart.addMapView('Routekaart', layersEnabled=['Annotaties'], layersDisabled=['Overzichtskaart', 'Topokaart'])
        loketOverzichtskaart.addMapView('Luchtfoto', layersEnabled=['Annotaties'], layersDisabled=['Overzichtskaart', 'Topokaart'])
        toolbar.addWidget(loketOverzichtskaart)

        showPdf = QAction('PDF', self.parent)
        QObject.connect(showPdf, SIGNAL('triggered(bool)'), self.showPdf)
        toolbar.addAction(showPdf)

        toolbar.addAction(ParcelIdentifyAction(self.main, self.parent, 'bezwarenkaart'))


