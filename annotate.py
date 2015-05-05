# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

class AnnotationManager(object):
    def __init__(self, main):
        self.main = main
        #QObject.connect(self.mapCanvas, SIGNAL('mapToolSet(QgsMapTool*)'), self.mapToolChanged)

        self.annotateArrow = QAction(QIcon(':/icons/icons/pijlen.png'), 'Teken een pijl', self.main.iface)
        self.annotateArrow.setCheckable(True)
        QObject.connect(self.annotateArrow, SIGNAL('triggered(bool)'), self.drawArrow)

        self.annotatePolygon = QAction(QIcon(':/icons/icons/polygonen.png'), 'Teken een polygoon', self.main.iface)
        self.annotatePolygon.setCheckable(True)
        QObject.connect(self.annotatePolygon, SIGNAL('triggered(bool)'), self.drawPolygon)

    def addActionsToToolbar(self, toolbar):
        toolbar.addAction(self.annotateArrow)
        toolbar.addAction(self.annotatePolygon)
  
    def drawArrow(self, start):
        if start:
            self.main.utils.editInLayer('Pijlen')
        else:
            self.main.utils.stopEditInLayer('Pijlen')

    def drawPolygon(self, start):
        if start:
            self.main.utils.editInLayer('Polygonen')
        else:
            self.main.utils.stopEditInLayer('Polygonen')
