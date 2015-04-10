# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_parceldialog import Ui_ParcelDialog

class ParcelDialog(QDialog, Ui_ParcelDialog):
    def __init__(self, main, parcel):
        QDialog.__init__(self, main.iface.mainWindow())
        self.main = main
        self.parcel = parcel
        self.setupUi(self)

        QObject.connect(self, SIGNAL('finished(int)'), self.finished)

        self.led_gewas.setText(self.parcel.attribute('GWS_NAAM'))

    def finished(self, result):
        if result == self.Accepted:
            print "SAVED"
        elif result == self.Rejected:
            print "NOT SAVED"
