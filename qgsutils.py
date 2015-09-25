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
        if attributes is not None:
            fr.setSubsetOfAttributes(attributes)
        fr.setFilterFids(fids)
        return self.layer.getFeatures(fr)

    def queryExpression(self, expression, attributes=None):
        stmt = "SELECT ogc_fid FROM %s WHERE " % self.ds.table()
        stmt += expression
        return self.query(stmt, attributes)
