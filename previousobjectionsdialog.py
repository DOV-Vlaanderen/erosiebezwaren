# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_previousobjectionsdialog import Ui_PreviousObjectionsDialog

from previousobjectioninfodialog import PreviousObjectionInfoDialog
from qgsutils import SpatialiteIterator
from widgets import valuelabel

class PreviousObjectionsWidget(QWidget):
    def __init__(self, uniek_id, parent, previousObjectionsDialog):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.uniek_id = uniek_id
        self.previousObjectionsDialog = previousObjectionsDialog
        self.main = self.previousObjectionsDialog.main
        self.previousObjectionsLayer = self.main.utils.getLayerByName(self.main.settings.getValue('layers/oudebezwaren'))

        self.horMaxSizePolicy = QSizePolicy()
        self.horMaxSizePolicy.setHorizontalPolicy(QSizePolicy.Maximum)

        self.layout = QGridLayout(parent)
        self.setLayout(self.layout)

        lb_jaar = QLabel('<b>Jaar</b>')
        lb_jaar.setSizePolicy(self.horMaxSizePolicy)
        self.layout.addWidget(lb_jaar, 0, 0)
        self.layout.addWidget(QLabel('<b>Oorsprokelijk</b>'), 0, 1)
        self.layout.addWidget(QLabel('<b>Advies</b>'), 0, 2)
        self.layout.addWidget(QLabel('<b>Aanpassing</b>'), 0, 3)
        self.layout.addWidget(QLabel('<b>Details</b>'), 0, 4)
        self.__populate()

    def __populate(self):
        if not self.previousObjectionsLayer:
            return

        expr = '"bezwaar_2016" like \'%%%s%%\'' % (self.uniek_id)
        objectionList = []
        for i in self.previousObjectionsLayer.getFeatures(QgsFeatureRequest(QgsExpression(expr))):
            objectionList.append(i)

        for i in sorted(objectionList, key = lambda x: int(x.attribute('jaar'))):
            self.addObjection(i)

    def addObjection(self, feature):
        row = self.layout.rowCount()

        btnJaar = QPushButton(str(feature.attribute('jaar')), self)
        btnJaar.setSizePolicy(self.horMaxSizePolicy)
        QObject.connect(btnJaar, SIGNAL('clicked(bool)'), lambda: self.highlightObjection(feature))
        self.layout.addWidget(btnJaar, row, 0)

        lb1 = valuelabel.ValueLabel(self)
        lb1.setText(feature.attribute('voor'))
        self.layout.addWidget(lb1, row, 1)

        lb2 = valuelabel.ValueLabel(self)
        lb2.setText(feature.attribute('advies'))
        self.layout.addWidget(lb2, row, 2)

        lb3 = valuelabel.ValueLabel(self)
        lb3.setText(feature.attribute('na'))
        self.layout.addWidget(lb3, row, 3)

        if feature.attribute('jaar') == 2015:
            btnDetails = QPushButton('info', self)
            QObject.connect(btnDetails, SIGNAL('clicked(bool)'), lambda: self.showInfo(feature))
            btnDetails.setSizePolicy(self.horMaxSizePolicy)
            self.layout.addWidget(btnDetails, row, 4)

    def highlightObjection(self, feature):
        self.main.selectionManager.clearWithMode(mode=2, toggleRendering=False)
        self.main.selectionManager.select(feature, mode=2)

    def showInfo(self, feature):
        def clearHighlightedObjections():
            self.main.selectionManager.clearWithMode(mode=2)

        self.highlightObjection(feature)

        s = SpatialiteIterator(self.main.utils.getLayerByName('bezwaren_2015'))
        oldFt = s.queryExpression("uniek_id = '%s'" % feature.attribute('oud_bezwaar_id'))[0]

        d = PreviousObjectionInfoDialog(self.parent, self.main, oldFt)
        QObject.connect(d, SIGNAL('finished(int)'), clearHighlightedObjections)
        d.show()

class PreviousObjectionsDialog(QDialog, Ui_PreviousObjectionsDialog):
    def __init__(self, main, uniek_id):
        self.main = main
        self.uniek_id = uniek_id
        QDialog.__init__(self, self.main.iface.mainWindow())
        self.setupUi(self)

        QObject.connect(self, SIGNAL('finished(int)'), self.exit)

        self.lbv_uniek_id.setText('Oude bezwaren voor perceel %s' % self.uniek_id)
        self.scrollAreaLayout.insertWidget(0, PreviousObjectionsWidget(self.uniek_id, self.scrollAreaWidgetContents, self))

    def exit(self):
        self.main.selectionManager.clearWithMode(mode=2)
