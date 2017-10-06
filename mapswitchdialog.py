# -*- coding: utf-8 -*-
"""Module containing the MapSwitchDialog and MapSwitchButton classes."""

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

import PyQt4.Qt as Qt
import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
import qgis.core as QGisCore

from ui_mapswitchdialog import Ui_MapSwitchDialog


class MapSwitchDialog(QtGui.QDialog, Ui_MapSwitchDialog):
    """Dialog to be able to switch the map view with two touches.

    By defining a few predefined map views (a combination of certain layers)
    and present these to the user by buttons, they can switch the map view
    with two touches.
    """

    def __init__(self, action):
        """Initialisation.

        Connect all clicked signals to the respective functions and populate.

        Parameters
        ----------
        action : MapSwitchButton
            Instance of MapSwitchButton used to open this MapSwitchDialog.

        """
        self.action = action
        self.main = self.action.main
        QtGui.QDialog.__init__(self)
        self.setupUi(self)

        self.visibleBase = set(['Overzichtskaart', 'percelenkaart_table',
                                'Topokaart'])
        self.allLayers = set(['Orthofoto', 'Afstromingskaart',
                              '2017 potentiele bodemerosie',
                              '2016 potentiele bodemerosie',
                              '2015 potentiele bodemerosie',
                              '2014 potentiele bodemerosie', 'watererosie30',
                              'dem_kul', 'dem_agiv', 'Overzichtskaart',
                              'percelenkaart_table', 'Topokaart', 'Bodemkaart',
                              'Erosiebestrijdingswerken'])
        self.activeDem = None

        QtCore.QObject.connect(self.btn_routekaart,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.toMapRoutekaart)
        QtCore.QObject.connect(self.btn_orthofoto,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.toMapOrthofoto)
        QtCore.QObject.connect(self.btn_erosie2014,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.toMapErosie2014)
        QtCore.QObject.connect(self.btn_erosie2015,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.toMapErosie2015)
        QtCore.QObject.connect(self.btn_erosie2016,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.toMapErosie2016)
        QtCore.QObject.connect(self.btn_erosie2017,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.toMapErosie2017)
        QtCore.QObject.connect(self.btn_watererosie_30,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.toMapWatererosie30)
        QtCore.QObject.connect(self.btn_afstromingskaart,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.toMapAfstromingskaart)
        QtCore.QObject.connect(self.btn_dem_kul,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.toMapDEMKul)
        QtCore.QObject.connect(self.btn_dem_agiv,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.toMapDEMAgiv)
        QtCore.QObject.connect(self.btn_bodemkaart,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.toMapBodemkaart)
        QtCore.QObject.connect(self.btn_erosiebestrijding,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.toMapErosiebestrijding)

        self.populate()

    def show(self):
        """Show the dialog."""
        self.populate()
        QtGui.QDialog.show(self)

    def populate(self):
        """Set the content dependent buttons to their correct value."""
        showOldAnnotations = self.main.qsettings.value(
            '/Qgis/plugins/Erosiebezwaren/map/oldAnnotations', '1')
        self.lbv_showOldAnnotations.setValue(int(showOldAnnotations))

    def toggleLayersGroups(self, enable=[], disable=[]):
        """Enable or disable specific layers or layergroups.

        Parameters
        ----------
        enable: list, optional
            Names of layers or layergroups to enable.
        disable: list, optional
            Names of layers or layergroups to disable.

        """
        legendInterface = self.main.iface.legendInterface()

        groups = legendInterface.groups()
        for i in range(0, len(groups)):
            if groups[i] in enable:
                legendInterface.setGroupVisible(i, True)
            if groups[i] in disable:
                legendInterface.setGroupVisible(i, False)

        for l in legendInterface.layers():
            if l.name() in enable:
                legendInterface.setLayerVisible(l, True)
            if l.name() in disable:
                legendInterface.setLayerVisible(l, False)

    def toMapView(self, mapView):
        """Switch to a certain map view.

        Parameters
        ----------
        mapView : dict
            Dictionary describing the map view to use, including:
            'autoDisable' : boolean
                Automatically disable the layers or layergroups that are not in
                enabledLayers.
            'enabledLayers' : list
                Names of layers or layergroups to enable.
            'disabledLayers' : list
                Names of layers or layergroups to disable.
            'label' : str
                Label to use on the MapSwitchButton to indicate this map view
                is active.

        """
        QtCore.QObject.disconnect(
            self.main.iface.mapCanvas(), QtCore.SIGNAL('extentsChanged()'),
            self.updateRasterColors)

        if mapView['autoDisable']:
            mapView['disabledLayers'] = self.allLayers - mapView[
                'enabledLayers']
        self.toggleLayersGroups(enable=mapView['enabledLayers'],
                                disable=mapView['disabledLayers'])
        self.action.setText(mapView['label'])

        if mapView['label'] == 'Watererosie 30':
            self.main.actions.pixelMeasureAction.setRasterLayerActive(True)
        else:
            self.main.actions.pixelMeasureAction.setRasterLayerActive(False)
            self.main.actions.pixelMeasureAction.stopMeasure()

        self.accept()

    def toMapRoutekaart(self):
        """Switch to the map view 'Routekaart'."""
        self.toMapView({
            'enabledLayers': self.visibleBase,
            'autoDisable': True,
            'label': 'Routekaart'
        })

    def toMapOrthofoto(self):
        """Switch to the map view 'Orthofoto'."""
        self.toMapView({
            'enabledLayers': (self.visibleBase - set(['Topokaart'])).union(
                ['Orthofoto']),
            'autoDisable': True,
            'label': 'Orthofoto'
        })

    def toMapErosie2014(self):
        """Switch to the map view 'Erosiekaart 2014'."""
        self.toMapView({
            'enabledLayers': self.visibleBase.union(
                ['2014 potentiele bodemerosie']),
            'autoDisable': True,
            'label': 'Erosiekaart 2014'
        })

    def toMapErosie2015(self):
        """Switch to the map view 'Erosiekaart 2015'."""
        self.toMapView({
            'enabledLayers': self.visibleBase.union(
                ['2015 potentiele bodemerosie']),
            'autoDisable': True,
            'label': 'Erosiekaart 2015'
        })

    def toMapErosie2016(self):
        """Switch to the map view 'Erosiekaart 2016'."""
        self.toMapView({
            'enabledLayers': self.visibleBase.union(
                ['2016 potentiele bodemerosie']),
            'autoDisable': True,
            'label': 'Erosiekaart 2016'
        })

    def toMapErosie2017(self):
        """Switch to the map view 'Erosiekaart 2017'."""
        self.toMapView({
            'enabledLayers': self.visibleBase.union(
                ['2017 potentiele bodemerosie']),
            'autoDisable': True,
            'label': 'Erosiekaart 2017'
        })

    def toMapWatererosie30(self):
        """Switch to the map view 'Watererosie 30'."""
        self.toMapView({
            'enabledLayers': self.visibleBase.union(
                ['watererosie30']),
            'autoDisable': True,
            'label': 'Watererosie 30'
        })

    def toMapAfstromingskaart(self):
        """Switch to the map view 'Afstromingskaart'."""
        self.toMapView({
            'enabledLayers': (self.visibleBase - set(
                ['percelenkaart_table', 'Overzichtskaart'])).union(
                    ['Afstromingskaart']),
            'autoDisable': True,
            'label': 'Afstromingskaart'
        })

    def toMapDEMKul(self):
        """Switch to the map view 'DEM KULeuven'."""
        self.activeDem = self.main.utils.getLayerByName('dem_kul')
        self.updateRasterColors()

        self.toMapView({
            'enabledLayers': self.visibleBase.union(['dem_kul']),
            'autoDisable': True,
            'label': 'DEM KULeuven'
        })

        QtCore.QObject.connect(self.main.iface.mapCanvas(),
                               QtCore.SIGNAL('extentsChanged()'),
                               self.updateRasterColors)

    def toMapDEMAgiv(self):
        """Switch to the map view 'DEM AGIV'."""
        self.activeDem = self.main.utils.getLayerByName('dem_agiv')
        self.updateRasterColors()

        self.toMapView({
            'enabledLayers': self.visibleBase.union(['dem_agiv']),
            'autoDisable': True,
            'label': 'DEM AGIV'
        })

        QtCore.QObject.connect(self.main.iface.mapCanvas(),
                               QtCore.SIGNAL('extentsChanged()'),
                               self.updateRasterColors)

    def toMapBodemkaart(self):
        """Switch to the map view 'Bodemkaart'."""
        self.toMapView({
            'enabledLayers': (self.visibleBase - set(['Topokaart'])).union(
                ['Bodemkaart']),
            'autoDisable': True,
            'label': 'Bodemkaart'
        })

    def toMapErosiebestrijding(self):
        """Switch to the map view 'Erosiebestrijdingswerken'."""
        self.toMapView({
            'enabledLayers': self.visibleBase.union(
                ['Erosiebestrijdingswerken']),
            'autoDisable': True,
            'label': 'Erosiebestrijdingswerken'
        })

    def updateRasterColors(self):
        """Update the style of the currently active DEM.

        If the current map view show a DEM, this method is triggered when the
        map canvas is changed by zooming or panning. It updates the style of
        the DEM to the minimum and maximum value of the DEM in the extent of
        the current map canvas.

        """
        if not self.activeDem:
            return

        currentExtent = self.main.iface.mapCanvas().extent()
        bandStats = self.activeDem.dataProvider() \
            .bandStatistics(1,
                            QGisCore.QgsRasterBandStats.Max |
                            QGisCore.QgsRasterBandStats.Min,
                            currentExtent, 1000)
        vmax = bandStats.maximumValue
        vmin = bandStats.minimumValue

        colorList = [QGisCore.QgsColorRampShader.ColorRampItem(
                         ((vmax-vmin)/4.0)*0+vmin, QtGui.QColor('#2b83ba')),
                     QGisCore.QgsColorRampShader.ColorRampItem(
                         ((vmax-vmin)/4.0)*1+vmin, QtGui.QColor('#abdda4')),
                     QGisCore.QgsColorRampShader.ColorRampItem(
                         ((vmax-vmin)/4.0)*2+vmin, QtGui.QColor('#ffffbf')),
                     QGisCore.QgsColorRampShader.ColorRampItem(
                         ((vmax-vmin)/4.0)*3+vmin, QtGui.QColor('#fdae61')),
                     QGisCore.QgsColorRampShader.ColorRampItem(
                         ((vmax-vmin)/4.0)*4+vmin, QtGui.QColor('#d7191c'))]

        rasterShader = QGisCore.QgsRasterShader()
        colorRampShader = QGisCore.QgsColorRampShader()
        colorRampShader.setColorRampItemList(colorList)
        colorRampShader.setColorRampType(
            QGisCore.QgsColorRampShader.INTERPOLATED)
        rasterShader.setRasterShaderFunction(colorRampShader)
        pseudoColorRenderer = QGisCore.QgsSingleBandPseudoColorRenderer(
            self.activeDem.dataProvider(), self.activeDem.type(), rasterShader)
        self.activeDem.setRenderer(pseudoColorRenderer)
        self.activeDem.triggerRepaint()


class MapSwitchButton(QtGui.QToolButton):
    """Class describing the toolbarbutton to open the MapSwitchDialog."""

    def __init__(self, main, parent):
        """Initialisation.

        Parameters
        ----------
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.
        parent : QtGui.QWidget
            Parent widget for the QtGui.QToolButton

        """
        self.main = main
        QtGui.QToolButton.__init__(self, parent)
        self.dialog = MapSwitchDialog(self)

        self.setText('Kies kaartbeeld')
        self.setToolButtonStyle(Qt.Qt.ToolButtonTextOnly)
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(),
                           QtGui.QSizePolicy.Fixed)
        self.setMinimumHeight(self.main.iface.mainWindow().iconSize().height())

        QtCore.QObject.connect(self, QtCore.SIGNAL('clicked(bool)'),
                               self.showDialog)
        QtCore.QObject.connect(self.dialog, QtCore.SIGNAL('finished(int)'),
                               self.dialogClosed)

    def showDialog(self):
        """Show the dialog at the top left of the screen."""
        self.dialog.move(0, 0)
        self.dialog.show()

    def dialogClosed(self, result):
        """Save the state of the toggle buttons.

        Parameters
        ----------
        result : int
            Result code of the dialog. 1 when closed with 'OK'.

        """
        if result == 1:
            self.main.qsettings.setValue(
                '/Qgis/plugins/Erosiebezwaren/map/oldAnnotations',
                str(self.dialog.lbv_showOldAnnotations.getValue()))
            oldAnnotations = ['Pijlen 2015', 'Polygonen 2015']
            if self.dialog.lbv_showOldAnnotations.getValue() == 1:
                self.dialog.toggleLayersGroups(enable=oldAnnotations)
            else:
                self.dialog.toggleLayersGroups(disable=oldAnnotations)

    def deactivate(self):
        """Deactivate by setting oldAnnotations visible."""
        self.main.qsettings.setValue(
            '/Qgis/plugins/Erosiebezwaren/map/oldAnnotations', '1')
