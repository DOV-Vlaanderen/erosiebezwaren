#-*- coding: utf-8 -*-

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

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from pyspatialite import dbapi2 as sl

class SpatialiteIterator(object):
    def __init__(self, layer):
        self.layer = layer
        self.ds = QgsDataSourceURI(self.layer.source())

    def rawQuery(self, sql):
        conn = sl.connect(self.ds.database())
        cursor = conn.execute(sql)
        r = cursor.fetchall()
        cursor.close()
        conn.close()
        return r

    def query(self, sql, attributes=None):
        fids = [i[0] for i in self.rawQuery(sql)]
        if len(fids) < 1:
            return []

        fr = QgsFeatureRequest()
        fts = []
        if attributes is not None:
            fr.setSubsetOfAttributes(attributes)

        for fid in fids:
            fr.setFilterFid(fid)
            fts.append(self.layer.getFeatures(fr).next())

        return fts

    def queryExpression(self, expression, attributes=None):
        stmt = "SELECT ogc_fid FROM %s WHERE " % self.ds.table()
        stmt += expression
        return self.query(stmt, attributes)
