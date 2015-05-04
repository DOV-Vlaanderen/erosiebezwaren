# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

# https://github.com/NathanW2/qmap/blob/master/src/qmap/gps_action.py

def detectedGPS(conn):
    QgsGPSConnectionRegistry().instance().registerConnection(conn)
    print "registered gps connection", conn

def detectionFailed():
    print "detection failed"

d = QgsGPSDetector('\\\\.\\COM7')
d.detected.connect(detectedGPS)
d.detected.detectionFailed(detectionFailed)
d.advance()
