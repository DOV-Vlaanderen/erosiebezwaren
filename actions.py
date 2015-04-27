#-*- coding: utf-8 -*-

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os
import subprocess
import time

from parcelidentifier import ParcelIdentifyAction
from mapswitchdialog import MapSwitchButton

class Actions(object):
    def __init__(self, main, parent):
        self.main = main
        self.parent = parent

    def annotateArrow(self, start):
        if start:
            self.main.utils.editInLayer('Pijlen')
        else:
            self.main.utils.stopEditInLayer('Pijlen')

    def showKeyboard(self):
        cmd = os.path.join(os.environ['COMMONPROGRAMFILES'], 'microsoft shared', 'ink', 'TabTip.exe')
        sp = subprocess.Popen(cmd, env=os.environ, shell=True)

    def exit(self):
        self.main.selectionManager.deactivate()
        while True:
            QgsApplication.exitQgis()
            time.sleep(0.05)

    def addToToolbar(self, toolbar):
        #toolbar.addAction(MapSwitchAction(self.main, self.parent))
        exitAction = QAction(QIcon(':/icons/icons/exit.png'), 'EXI', self.parent)
        QObject.connect(exitAction, SIGNAL('triggered(bool)'), self.exit)
        toolbar.addAction(exitAction)

        toolbar.addWidget(MapSwitchButton(self.main, self.parent))

        annotateArrow = QAction(QIcon(':/icons/icons/pijlen.png'), 'APY', self.parent)
        annotateArrow.setCheckable(True)
        QObject.connect(annotateArrow, SIGNAL('triggered(bool)'), self.annotateArrow)
        toolbar.addAction(annotateArrow)

        toolbar.addAction(ParcelIdentifyAction(self.main, self.parent, 'bezwarenkaart'))
