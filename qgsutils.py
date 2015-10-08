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
            fts.append([i for i in self.layer.getFeatures(fr)][0])

        return fts

    def queryExpression(self, expression, attributes=None):
        stmt = "SELECT ogc_fid FROM %s WHERE " % self.ds.table()
        stmt += expression
        return self.query(stmt, attributes)
