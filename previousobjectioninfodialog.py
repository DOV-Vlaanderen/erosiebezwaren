# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os
import subprocess

from ui_previousobjectioninfodialog import Ui_PreviousObjectionInfoDialog

class PreviousObjectionInfoDialog(QDialog, Ui_PreviousObjectionInfoDialog):
    def __init__(self, parent, main, feature, jaar):
        from parcelinfowidget import ParcelInfoContentWidget
        QDialog.__init__(self, parent)
        self.main = main
        self.feature = feature
        self.jaar = jaar
        self.setupUi(self)

        contentWidget = ParcelInfoContentWidget(self, self.main, self.feature)
        self.layout().insertWidget(2, contentWidget)
        self.addToolbarButtons()

        self.setWindowTitle('Bezwaar %s' % self.feature.attribute('uniek_id'))

        contentWidget.tabWidget.setCurrentIndex(2)

    def addToolbarButtons(self):
        self.addPhotoButton()
        self.addObjectionFormButton()
        if self.buttonBarLayout.count() > 1:
            self.buttonBarLayout.setContentsMargins(-1, 6, -1, 6)

    def addPhotoButton(self):
        self.photoPath = None
        if self.feature:
            # QgsProject.instance().fileName() returns path with forward slashes, even on Windows. Append subdirectories with forward slashes too
            # and replace all of them afterwards with backward slashes.
            fid = self.feature.attribute('uniek_id')
            if fid:
                photoPath = '/'.join([os.path.dirname(QgsProject.instance().fileName()), 'fotos_%i' % self.jaar,
                                      str(fid)])
                photoPath = photoPath.replace('/', '\\')
                if os.path.exists(photoPath) and len(os.listdir(photoPath)) > 0:
                    self.photoPath = photoPath
                    self.btn_showPhotos = QPushButton()
                    self.btn_showPhotos.setIcon(QIcon(":/icons/icons/photo.png"))
                    self.btn_showPhotos.setIconSize(QSize(64, 64))
                    self.btn_showPhotos.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
                    QObject.connect(self.btn_showPhotos, SIGNAL('clicked(bool)'), self.showPhotos)
                    self.buttonBarLayout.addWidget(self.btn_showPhotos)

    def addObjectionFormButton(self):
        if self.feature:
            try:
                cmdShow = os.environ['COMSPEC'] + ' /c start "" "%s"'
                cmdExplore = os.path.join(os.environ['SYSTEMROOT'], 'explorer.exe') + ' "%s"'
            except KeyError:
                return

            objectionPath = '/'.join([os.path.dirname(QgsProject.instance().fileName()), 'bezwaren_%i' % jaar,
                                      str(self.feature.attribute('producentnr'))])
            objectionPath = objectionPath.replace('/', '\\')
            self.objectionPath = []
            if os.path.exists(objectionPath):
                fileList = [i.lower() for i in os.listdir(objectionPath)]
                exts = set([f[f.rfind('.')+1:] for f in fileList])
                if len(exts) == 1 and 'pdf' in exts:
                    # only pdfs
                    for f in fileList:
                        self.objectionPath.append(cmdShow % (objectionPath + '/' + f))
                elif len(exts) > 0:
                    # other thing(s)
                    self.objectionPath.append(cmdExplore % objectionPath)

                self.btn_bezwaarformulier = QPushButton()
                self.btn_bezwaarformulier.setIcon(QIcon(":/icons/icons/pdf.png"))
                self.btn_bezwaarformulier.setIconSize(QSize(64, 64))
                self.btn_bezwaarformulier.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
                QObject.connect(self.btn_bezwaarformulier, SIGNAL('clicked(bool)'), self.showObjectionForm)
                self.buttonBarLayout.addWidget(self.btn_bezwaarformulier)

    def showPhotos(self):
        if not self.photoPath:
            return

        cmd = os.path.join(os.environ['SYSTEMROOT'], 'explorer.exe')
        cmd += ' "%s"' % self.photoPath
        subprocess.Popen(cmd)

    def showObjectionForm(self):
        for o in self.objectionPath:
            subprocess.Popen(o)
