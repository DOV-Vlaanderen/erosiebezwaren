# -*- coding: utf-8 -*-
"""Module for utilities extending QGis capabilities.

Contains the SpatialiteIterator class.
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

import qgis.core as QGisCore

from pyspatialite import dbapi2 as sl


class SpatialiteIterator(object):
    """Class to query a Spatialite layer through a direct db connection."""

    def __init__(self, layer):
        """Initialisation.

        Parameters
        ----------
        layer : QGisCore.QgsVectorLayer
            Layer to query. The connection to the Spatialite is derived from
            the datasource of the layer.

        """
        self.layer = layer
        self.ds = QGisCore.QgsDataSourceURI(self.layer.source())

    def rawQuery(self, sql):
        """Execute a SQL query and return the raw results.

        Parameters
        ----------
        sql : str
            Query to execute.

        Returns
        -------
        results : iterable
            All results of the query.

        """
        conn = sl.connect(self.ds.database())
        cursor = conn.execute(sql)
        r = cursor.fetchall()
        cursor.close()
        conn.close()
        return r

    def query(self, sql, attributes=None):
        """Execute a SQL query and return the results as QGis Features.

        Parameters
        ----------
        sql : str
            Query to execute.
        attributes : list, optional
            Subset of attributes to include in the returned QgsFeature's.
            Defaults to all attributes.

        Returns
        -------
        list of QgsFeature
            List of QgsFeatures matching the query.

        """
        fids = [i[0] for i in self.rawQuery(sql)]
        if len(fids) < 1:
            return []

        fr = QGisCore.QgsFeatureRequest()
        fts = []
        if attributes is not None:
            fr.setSubsetOfAttributes(attributes)

        for fid in fids:
            fr.setFilterFid(fid)
            fts.append(self.layer.getFeatures(fr).next())

        return fts

    def queryExpression(self, expression, attributes=None):
        """Execute an expression and return the results as QGis Features.

        Parameters
        ----------
        expression : str
            Expression used as the WHERE clause of the query.
        attributes : list, optional
            Subset of attributes to include in the returned QgsFeature's.
            Defaults to all attributes.

        Returns
        -------
        list of QgsFeature
            List of QgsFeatures matching the expression.

        """
        stmt = "SELECT ogc_fid FROM %s WHERE " % self.ds.table()
        stmt += expression
        return self.query(stmt, attributes)
