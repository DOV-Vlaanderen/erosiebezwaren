# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_previousobjectionsdialog import Ui_PreviousObjectionsDialog
from widgets import valuelabel

class PreviousObjectionsWidget(QWidget):
    def __init__(self, uniek_id, parent, previousObjectionsDialog):
        QWidget.__init__(self, parent)
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
        self.layout.addWidget(QLabel('<b>Aanpassing</b>'), 0, 1)
        self.__populate()

    def __populate(self):
        if not self.previousObjectionsLayer:
            return

        expr = '"uniek_id_2015" = \'%s\'' % (self.uniek_id)
        objectionList = []
        for i in self.previousObjectionsLayer.getFeatures(QgsFeatureRequest(QgsExpression(expr))):
            objectionList.append(i)

        for i in sorted(objectionList, key = lambda x: int(x.attribute('jaar'))):
            self.addObjection(i)

    def addObjection(self, feature):
        row = self.layout.rowCount()

        btn = QPushButton(str(feature.attribute('jaar')), self)
        btn.setSizePolicy(self.horMaxSizePolicy)
        QObject.connect(btn, SIGNAL('clicked(bool)'), lambda: self.highlightObjection(feature))
        self.layout.addWidget(btn, row, 0)

        lb1 = valuelabel.ValueLabel(self)
        lb1.setText(feature.attribute('aanpassing'))
        self.layout.addWidget(lb1, row, 1)

    def highlightObjection(self, feature):
        self.main.selectionManager.clearWithMode(mode=3, toggleRendering=False)
        self.main.selectionManager.select(feature, mode=3)

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
        self.main.selectionManager.clearWithMode(mode=3)
