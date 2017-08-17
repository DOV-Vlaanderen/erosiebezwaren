#-*- coding: utf-8 -*-

#  DOV Erosiebezwaren, QGis plugin to assess field erosion on tablets
#  Copyright (C) 2015-2017  Roel Huybrechts
#
#  Partly based on the loop visible layers plugin (https://github.com/etiennesky/loopvisiblelayers)
#  Copyright (C) 2012 Etienne Tourigny
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

from PyQt4.QtCore import *
from PyQt4 import QtGui
from PyQt4.QtGui import QIcon, QPixmap
from qgis.core import *
from qgis.gui import *

import resources_rc
from ui_erosiebezwarenwidget import Ui_ErosiebezwarenWidget as Ui_Widget

# create the widget
class ErosiebezwarenWidget(QtGui.QWidget, Ui_Widget):
    def __init__(self, iface):

        QtGui.QWidget.__init__(self)
        # Set up the user interface from Designer.
        self.setupUi(self)

        # Save reference to the QGIS interface
        self.iface = iface
        self.settings = QSettings()

        # Variables
        self.groupNames = None
        self.groupRels = None
        self.bakLayerIds = None
        self.count = 0
        self.freeze = True
        self.updateCount = 0
        self.signalsLegendIface = False # are the new legendInterface() signals available?
        self.visibleDock = False
        self.state = 'stop'
        self.inSelection = False
        
        # layers
        self.lyr_alv = None

        # signals/slots
        QObject.connect( self, SIGNAL('topLevelChanged(bool)'), self.resizeMin)
        QObject.connect( self, SIGNAL( 'visibilityChanged( bool )' ), self.checkGroupsChanged )
        QObject.connect( self.iface.legendInterface(), SIGNAL( 'itemAdded( QModelIndex )' ), self.checkGroupsChangedLegendIface )
        QObject.connect( self.iface.legendInterface(), SIGNAL( 'itemRemoved()' ), self.checkGroupsChangedLegendIface )
        QObject.connect( self.iface.legendInterface(), SIGNAL( 'groupRelationsChanged()' ), self.checkGroupsChangedLegendIface )
        QObject.connect( self.iface.mapCanvas(), SIGNAL( 'stateChanged( int )' ), self.checkGroupsChanged )
        
        QObject.connect( self.editorEdit, SIGNAL ('editingFinished()' ), self.saveEditor )
        QObject.connect( self.selecteerPercelenBtn, SIGNAL('clicked(bool)'), self.selecteerPercelenClicked )
        
        # Set up UI
        self.editorEdit.setText(self.settings.value("erosiebezwaren/editor"))

        # update groups on init
        self.checkGroupsChanged()
        
    def saveEditor(self):
        self.settings.setValue("erosiebezwaren/editor", self.editorEdit.text())
        
    def selecteerPercelenClicked(self, selected):
        if not self.lyr_alv and self.iface.activeLayer():
            self.lyr_alv = self.iface.activeLayer()

        if not self.lyr_alv:
            return
            
        if selected:
            self.iface.actionSelect().trigger()
            self.percelenSelectionChanged()
            QObject.connect(self.lyr_alv, SIGNAL('selectionChanged()'), self.percelenSelectionChanged)
        else:
            self.iface.actionPan().trigger()
            QObject.disconnect(self.lyr_alv, SIGNAL('selectionChanged()'), self.percelenSelectionChanged)
            
    def percelenSelectionChanged(self):
        if self.inSelection:
            return

        self.inSelection = True
        selected_prds = set()
        for feat in self.lyr_alv.selectedFeatures():
            selected_prds.add(feat.attribute('PRD_NMR'))
        
        expr = 'PRD_NMR in (%s)' % ', '.join(selected_prds)
        to_select = []
        for feat in self.lyr_alv.getFeatures(QgsFeatureRequest(QgsExpression(expr))):
            to_select.append(feat.id())
        self.lyr_alv.select(to_select)
        self.inSelection = False
        
    # this slot triggered by iface.legendInterface(), i.e. when items are added, moved or removed
    # these signals are not yet part of qgis, so enterEvent() is used as a fallback
    def checkGroupsChangedLegendIface(self):
       # when we get this signal for the first time, set signalsLegendIface=True so enterEvent() does nothing 
        if not self.signalsLegendIface:
            self.signalsLegendIface = True
        self.checkGroupsChanged()

    # this does the real work
    def checkGroupsChanged(self):
        newGroupNames = self.iface.legendInterface().groups()
        newGroupRels = self.iface.legendInterface().groupLayerRelationship()
        if ( newGroupNames == self.groupNames ) and ( newGroupRels == self.groupRels ):
            return
        
        self.groupNames = newGroupNames
        self.groupRels = self.iface.legendInterface().groupLayerRelationship()
        self.updateCount = self.updateCount+1

    def setGroupVisible(self,layerId,layerVisible):

        for grp, rels in self.groupRels:
            if ( grp == '' and layerId == '<Root>' ) or ( grp == layerId ):
                for tmpLayerId in rels:
                    if tmpLayerId in self.groupNames:
                        self.setGroupVisible(tmpLayerId,layerVisible)
                    else:
                        layer = QgsMapLayerRegistry.instance().mapLayers()[str(tmpLayerId)]
                        self.iface.legendInterface().setLayerVisible( layer, layerVisible )

    # minimize widget
    def resizeMin(self):
        if self.isFloating():
            self.resize( self.minimumSize() )

    def freezeCanvas(self, setFreeze):
        if self.freeze:
            if setFreeze:
                if not self.iface.mapCanvas().isFrozen():
                    self.iface.mapCanvas().freeze( True )
            else:
                if self.iface.mapCanvas().isFrozen():
                    self.iface.mapCanvas().freeze( False )
                    self.iface.mapCanvas().refresh()

    def enterEvent(self, event):
        # workaround, if signalsLegendIface=False, check groups changed
        if not self.signalsLegendIface:
            self.checkGroupsChanged()
        QtGui.QWidget.enterEvent(self, event)

    def sizeHint(self):
        return self.minimumSize()
        
    def onVisibilityChanged(self,visible):
        self.visibleDock = visible
        if self.state=='start' or self.state=='pause':
            if visible:
                # set override cursor
                QtGui.QApplication.setOverrideCursor( self.loopCursor )
            else:
                # restore override cursor
                QtGui.QApplication.restoreOverrideCursor()
