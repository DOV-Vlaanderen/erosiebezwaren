# -*- coding: utf-8 -*-
"""Module containing the PreviousObjectionInfoDialog class."""

#  DOV Erosiebezwaren, QGis plugin to assess field erosion on tablets
#  Copyright (C) 2015-2017  Roel Huybrechts
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
import qgis.core as QGisCore

import os
import subprocess

from parcelinfowidget import ParcelInfoContentWidget
from ui_previousobjectioninfodialog import Ui_PreviousObjectionInfoDialog


class PreviousObjectionInfoDialog(QtGui.QDialog,
                                  Ui_PreviousObjectionInfoDialog):
    """Dialog showing more information about a previous objection."""

    def __init__(self, parent, main, feature, jaar):
        """Initialisation.

        Parameters
        ----------
        parent : QtGui.QWidget
            Widget to use as parent widget.
        main : erosiebezwaren.Erosiebezwaren
            Instance to main class.
        feature : QGisCore.QgsFeature
            Feature containing all information about the previous objection.
        jaar : int
            Year of the campagne of the previous objection. This is used to
            find the photos and objection form in the respective directories.

        """
        QtGui.QDialog.__init__(self, parent)
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
        """Add photo and/or objection form buttons to the toolbar."""
        self.addPhotoButton()
        self.addObjectionFormButton()
        if self.buttonBarLayout.count() > 1:
            self.buttonBarLayout.setContentsMargins(-1, 6, -1, 6)

    def addPhotoButton(self):
        """Add the 'show photo' button to the toolbar.

        Only adds the button if there are photos of this objection available.
        """
        self.photoPath = None
        if self.feature:
            # QGisCore.QgsProject.instance().fileName() returns path with
            # forward slashes, even on Windows. Append subdirectories with
            # forward slashes too and replace all of them afterwards with
            # backward slashes.
            fid = self.feature.attribute('uniek_id')
            if fid:
                photoPath = '/'.join([os.path.dirname(
                    QGisCore.QgsProject.instance().fileName()),
                                      'fotos_%i' % self.jaar, str(fid)])
                photoPath = photoPath.replace('/', '\\')
                if os.path.exists(photoPath) and \
                        len(os.listdir(photoPath)) > 0:
                    self.photoPath = photoPath
                    self.btn_showPhotos = QtGui.QPushButton()
                    self.btn_showPhotos.setIcon(
                        QtGui.QIcon(":/icons/icons/photo.png"))
                    self.btn_showPhotos.setIconSize(QtCore.QSize(64, 64))
                    self.btn_showPhotos.setSizePolicy(QtGui.QSizePolicy(
                        QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum))
                    QtCore.QObject.connect(self.btn_showPhotos,
                                           QtCore.SIGNAL('clicked(bool)'),
                                           self.showPhotos)
                    self.buttonBarLayout.addWidget(self.btn_showPhotos)

    def addObjectionFormButton(self):
        """Add the 'show objection form' button to the toolbar.

        Only adds the button if there are forms available for this objection.
        """
        if self.feature:
            try:
                cmdShow = os.environ['COMSPEC'] + ' /c start "" "%s"'
                cmdExplore = os.path.join(os.environ['SYSTEMROOT'],
                                          'explorer.exe') + ' "%s"'
            except KeyError:
                return

            objectionPath = '/'.join([os.path.dirname(
                QGisCore.QgsProject.instance().fileName()),
                                      'bezwaren_%i' % self.jaar,
                                      str(self.feature.attribute(
                                          'producentnr'))])
            objectionPath = objectionPath.replace('/', '\\')
            self.objectionPath = []
            if os.path.exists(objectionPath):
                fileList = [i.lower() for i in os.listdir(objectionPath)]
                exts = set([f[f.rfind('.')+1:] for f in fileList])
                if len(exts) == 1 and 'pdf' in exts:
                    # only pdfs
                    for f in fileList:
                        self.objectionPath.append(cmdShow % (objectionPath +
                                                             '/' + f))
                elif len(exts) > 0:
                    # other thing(s)
                    self.objectionPath.append(cmdExplore % objectionPath)

                self.btn_bezwaarformulier = QtGui.QPushButton()
                self.btn_bezwaarformulier.setIcon(
                    QtGui.QIcon(":/icons/icons/pdf.png"))
                self.btn_bezwaarformulier.setIconSize(QtCore.QSize(64, 64))
                self.btn_bezwaarformulier.setSizePolicy(
                    QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum,
                                      QtGui.QSizePolicy.Maximum))
                QtCore.QObject.connect(self.btn_bezwaarformulier,
                                       QtCore.SIGNAL('clicked(bool)'),
                                       self.showObjectionForm)
                self.buttonBarLayout.addWidget(self.btn_bezwaarformulier)

    def showPhotos(self):
        """Open the directory containing the photos of this parcel in Explorer.

        Used as callback for the 'show photos' button.
        """
        if not self.photoPath:
            return

        cmd = os.path.join(os.environ['SYSTEMROOT'], 'explorer.exe')
        cmd += ' "%s"' % self.photoPath
        subprocess.Popen(cmd)

    def showObjectionForm(self):
        """Open all objection paths (folders or files) in Windows Explorer.

        Used as a callback for the 'show objection' button.
        """
        for o in self.objectionPath:
            subprocess.Popen(o)
