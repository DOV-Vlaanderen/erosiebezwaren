# -*- coding: utf-8 -*-
"""Module for the parcel identify maptool.

Contains the classes MapToolParcelIdentifier and ParcelIdentifyAction.
"""

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
import qgis.gui as QGisGui


class MapToolParcelIdentifier(QGisGui.QgsMapToolIdentify):
    """Custom QgsMapToolIdentify to identify parcels."""

    def __init__(self, main):
        """Initialisation.

        Parameters
        ----------
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.

        """
        self.main = main
        QGisGui.QgsMapToolIdentify.__init__(self, self.main.iface.mapCanvas())
        self.previousActiveLayer = None

    def activate(self):
        """Activate the selectionmanager and the maptool."""
        self.main.selectionManagerPolygons.activate()
        QGisGui.QgsMapToolIdentify.activate(self)

    def canvasReleaseEvent(self, mouseEvent):
        """Identify parcels at the point the user clicked the map canvas.

        Called when the user clicks the map canvas. Identify parcels at this
        location and select one on them (prefer the ones that have a
        complaint).

        Marks the selected parcel in a distinctive color by selecting it using
        the polygon selection manager, and show the information about the
        selected parcel in the parcelinfowidget.

        Parameters
        ----------
        mouseEvent : QGisGui.QgsMapMouseEvent
            Event describing the point on the map canvas the user clicked.

        """
        table = self.main.utils.getLayerByName('percelenkaart_table')
        view = self.main.utils.getLayerByName('percelenkaart_view')
        if table and view:
            self.main.iface.setActiveLayer(table)
            results = self.identify(mouseEvent.x(), mouseEvent.y(),
                                    self.ActiveLayer, self.VectorLayer)
            resultFid = None

            # Check for overlapping features:
            #   - if one of them is an objection, select that
            #   - if none of them is an objection, sort them to always select
            #     the same feature
            if len(results) == 1:
                resultFid = results[0].mFeature.id()
            elif len(results) > 1:
                fts = sorted([r.mFeature for r in results],
                             key=lambda x: x.attribute('uniek_id'))
                fts_objections = [ft for ft in fts if ft.attribute(
                    'datum_bezwaar')]

                if len(fts_objections) == 1:
                    resultFid = fts_objections[0].id()
                elif len(fts_objections) == 0:
                    resultFid = fts[0].id()

            if resultFid:
                fr = QGisCore.QgsFeatureRequest()
                fr.setFilterFid(resultFid)
                feature = view.getFeatures(fr).next()
                self.main.parcelInfoWidget.setLayer(view)
                self.main.parcelInfoWidget.setFeature(feature)
                self.main.parcelInfoWidget.parent.show()
            else:
                self.main.parcelInfoWidget.clear()

        if self.previousActiveLayer:
            self.main.iface.setActiveLayer(self.previousActiveLayer)


class ParcelIdentifyAction(QtGui.QAction):
    """Class describing the QAction to enable and disable the maptool.

    Used on the toolbar to switch to the maptool to identify parcels.
    """

    def __init__(self, main, parent):
        """Initialisation.

        Parameters
        ----------
        main : erosiebezwaren.Erosiebezwaren
            Instance of main class.
        parent : QtGui.QWidget
            Parent widget of this action.

        """
        self.main = main
        QtGui.QAction.__init__(self, QtGui.QIcon(':/icons/icons/identify.png'),
                               'Identificeer perceel', parent)

        self.mapCanvas = self.main.iface.mapCanvas()
        self.previousMapTool = None
        self.parcelMapTool = MapToolParcelIdentifier(self.main)

        self.setCheckable(True)
        QtCore.QObject.connect(self, QtCore.SIGNAL('triggered(bool)'),
                               self.identifyParcel)

    def mapToolChanged(self, mt=None):
        """Disable the maptool to identify parcels.

        Called when the users switched to another maptool while the parcel
        identification maptool was active.

        Parameters
        ----------
        mt : QGisGui.QgsMapTool, optional
            Currently selected maptool.

        """
        QtCore.QObject.disconnect(self.main.iface.mapCanvas(),
                                  QtCore.SIGNAL('mapToolSet(QgsMapTool*)'),
                                  self.mapToolChanged)
        self.setChecked(False)

    def identifyParcel(self, start):
        """Enable or disable the maptool to identify parcels.

        Parameters
        ----------
        start : boolean
            If `True`: switch to the map tool to identify parcels, if `False`
            restore the previously enabled maptool.

        """
        if start:
            self.previousMapTool = self.mapCanvas.mapTool()
            self.mapCanvas.setMapTool(self.parcelMapTool)
            QtCore.QObject.connect(self.mapCanvas,
                                   QtCore.SIGNAL('mapToolSet(QgsMapTool*)'),
                                   self.mapToolChanged)
        else:
            QtCore.QObject.disconnect(self.mapCanvas,
                                      QtCore.SIGNAL('mapToolSet(QgsMapTool*)'),
                                      self.mapToolChanged)
            if self.previousMapTool:
                self.mapCanvas.setMapTool(self.previousMapTool)

    def deactivate(self):
        """Deactivate by stopping listening to the mapToolChanged event."""
        QtCore.QObject.disconnect(self.main.iface.mapCanvas(),
                                  QtCore.SIGNAL('mapToolSet(QgsMapTool*)'),
                                  self.mapToolChanged)
