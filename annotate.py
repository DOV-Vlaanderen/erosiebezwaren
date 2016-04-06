# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

class AnnotationManager(object):
    def __init__(self, main):
        def drawArrow(start):
            if start:
                if self.currentlyEditing:
                    QObject.disconnect(self.main.iface.mapCanvas(), SIGNAL('mapToolSet(QgsMapTool*)'), self.mapToolChanged)
                    self.main.utils.stopEditInLayer(self.currentlyEditing[0])
                    self.currentlyEditing[1].setChecked(False)
                self.currentlyEditing = (self.main.settings.getValue('layers/pijlen'), self.annotateArrow)
                self.main.utils.editInLayer(self.main.settings.getValue('layers/pijlen'))
                QObject.connect(self.main.iface.mapCanvas(), SIGNAL('mapToolSet(QgsMapTool*)'), self.mapToolChanged)
            else:
                QObject.disconnect(self.main.iface.mapCanvas(), SIGNAL('mapToolSet(QgsMapTool*)'), self.mapToolChanged)
                if self.currentlyEditing:
                    self.main.utils.stopEditInLayer(self.currentlyEditing[0])
                self.currentlyEditing = None

        def drawPolygon(start):
            if start:
                if self.currentlyEditing:
                    QObject.disconnect(self.main.iface.mapCanvas(), SIGNAL('mapToolSet(QgsMapTool*)'), self.mapToolChanged)
                    self.main.utils.stopEditInLayer(self.currentlyEditing[0])
                    self.currentlyEditing[1].setChecked(False)
                self.currentlyEditing = (self.main.settings.getValue('layers/polygonen'), self.annotatePolygon)
                self.main.utils.editInLayer(self.main.settings.getValue('layers/polygonen'))
                QObject.connect(self.main.iface.mapCanvas(), SIGNAL('mapToolSet(QgsMapTool*)'), self.mapToolChanged)
            else:
                QObject.disconnect(self.main.iface.mapCanvas(), SIGNAL('mapToolSet(QgsMapTool*)'), self.mapToolChanged)
                if self.currentlyEditing:
                    self.main.utils.stopEditInLayer(self.currentlyEditing[0])
                self.currentlyEditing = None

        self.main = main
        self.currentlyEditing = None

        self.annotateArrow = QAction(QIcon(':/icons/icons/pijlen.png'), 'Teken een pijl', self.main.iface)
        self.annotateArrow.setCheckable(True)
        QObject.connect(self.annotateArrow, SIGNAL('triggered(bool)'),  drawArrow)

        self.annotatePolygon = QAction(QIcon(':/icons/icons/polygonen.png'), 'Teken een polygoon', self.main.iface)
        self.annotatePolygon.setCheckable(True)
        QObject.connect(self.annotatePolygon, SIGNAL('triggered(bool)'), drawPolygon)

    def getActions(self):
        return (self.annotateArrow, self.annotatePolygon)

    def mapToolChanged(self, mt):
        QObject.disconnect(self.main.iface.mapCanvas(), SIGNAL('mapToolSet(QgsMapTool*)'), self.mapToolChanged)
        if self.currentlyEditing:
            self.main.utils.stopEditInLayer(self.currentlyEditing[0])
            self.currentlyEditing[1].setChecked(False)
            self.currentlyEditing = None

    def deactivate(self):
        if self.currentlyEditing:
            self.main.utils.stopEditInLayer(self.currentlyEditing[0]) # triggers mapToolChanged
