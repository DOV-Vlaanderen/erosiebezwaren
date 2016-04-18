# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_previousobjectioninfodialog import Ui_PreviousObjectionInfoDialog

class PreviousObjectionInfoDialog(QDialog, Ui_PreviousObjectionInfoDialog):
    def __init__(self, parent, main, feature):
        from parcelinfowidget import ParcelInfoContentWidget
        QDialog.__init__(self, parent)
        self.main = main
        self.feature = feature
        self.setupUi(self)

        contentWidget = ParcelInfoContentWidget(self, self.main, self.feature)
        self.layout().insertWidget(1, contentWidget)

        self.setWindowTitle('Bezwaar %s' % self.feature.attribute('uniek_id'))

        contentWidget.tabWidget.setCurrentIndex(2)
