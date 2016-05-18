# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui_monitoringwidget import Ui_MonitoringWidget
from widgets.elevatedfeaturewidget import ElevatedFeatureWidget

class CheckableCell(QPushButton):
    def __init__(self, objectName, label, parent):
        QPushButton.__init__(self, label, parent)
        self.setObjectName(objectName)

        self.setCheckable(True)
        self.__setStyleSheet()

        QObject.connect(self, SIGNAL('clicked()'), self.__updateValue)

    def setValue(self, checked):
        self.setChecked(checked)
        self.setText('X') if checked else self.setText('')

    def __updateValue(self):
        self.setValue(self.isChecked())

    def __setStyleSheet(self):
        style = "QPushButton, QPushButton:checked, QPushButton:disabled {"
        style += "border: none;"
        style += "background-color: white;"
        style += "border-radius: 4px;"
        style += "padding: 2px;"
        style += "}"

        style += "QPushButton:disabled {"
        style += "background-color: none;"
        style += "}"
        self.setStyleSheet(style)

class BasisPakketWidget(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.options = [
            ('groen', 'Groenbedekker'),
            ('voor112', 'Teelt voor 1/12'),
            ('nietkerend', 'Niet-kerende'),
            ('ploegen', 'Ploegen'),
            ('mulch', 'Mulch'),
            ('resten', 'Teeltresten'),
            ('geenmtrgl', 'Geen maatregel'),
            ('geeninfo', 'Geen info')
        ]

        self.periods = [
            ('voor', 'Voor hoofdteelt'),
            ('na', 'Na hoofdteelt')
        ]

        self.cells = dict(zip([p[0] for p in self.periods], [{} for i in range(len(self.periods))]))

        for i in range(len(self.periods)):
            self.layout.addWidget(QLabel(self.periods[i][1]), 0, i+1)

        for i in range(len(self.options)):
            self.layout.addWidget(QLabel(self.options[i][1]), i+1, 0)

        for i in range(len(self.options)):
            for j in range(len(self.periods)):
                option = self.options[i]
                period = self.periods[j]
                cell = CheckableCell('%s_%s' % (period[0], option[0]), '', self)
                QObject.connect(cell, SIGNAL('toggled(bool)'), self._validate)
                self.cells[period[0]][option[0]] = cell
                self.layout.addWidget(self.cells[period[0]][option[0]], i+1, j+1)

    def _validate(self, *args):
        for p in self.periods:
            geenChecked = [self.cells[p[0]][i] for i in self.cells[p[0]] if i.startswith('geen') and self.cells[p[0]][i].isChecked()]
            if len(geenChecked) > 0:
                for c in self.cells[p[0]].values():
                    if c != geenChecked[0]:
                        c.setValue(False)
                        c.setEnabled(False)
            else:
                for c in self.cells[p[0]].values():
                    c.setEnabled(True)

    def setValue(self, value):
        ls = [i.strip() for i in value.strip().split(';')]
        for p in self.cells:
            for o in self.cells[p]:
                self.cells[p][o].setValue('%s_%s' % (p, o) in ls)

    def getValue(self):
        return '; '.join(
            sorted(['voor_'+c for c in self.cells['voor'] if self.cells['voor'][c].isChecked()]) + \
            sorted(['na_'+c for c in self.cells['na'] if self.cells['na'][c].isChecked()])
        )

class BufferStrookHellingWidget(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.options = [
            ['Uniform', ['Parallel', 'Waterscheiding', 'Schuin']],
            ['1 droge vallei', []],
            ['Complex', []]
        ]

        self.widgets = {}

        gb = QGroupBox(self)
        gb.setLayout(QVBoxLayout(gb))
        self.layout.addWidget(gb)

        for i in self.options:
            radio = QRadioButton(i[0], gb)
            radio.setAutoExclusive(True)
            #QObject.connect(radio, SIGNAL('toggled(bool)'), self._updateParentChild)
            gb.layout().addWidget(radio)
            gbx = None

            if len(i[1]) > 0:
                gbx = QGroupBox(gb)
                gbx.setLayout(QVBoxLayout(gbx))
                for j in i[1]:
                    radiox = QRadioButton(j, gbx)
                    radiox.setAutoExclusive(True)
                    #QObject.connect(radiox, SIGNAL('toggled(bool)'), self._updateParentChild)
                    self.widgets[j] = (radiox, None, radio)
                    gbx.layout().addWidget(radiox)

                gb.layout().addWidget(gbx)
                #gbx.setEnabled(False)

            self.widgets[i[0]] = (radio, gbx, None)

    def _updateParentChild(self, toggled):
        if toggled:
            w = self.widgets[self.sender().text()]
            if w[1]:
                w[1].setEnabled(True)
            #if w[2]:
            #    w[2].setChecked(True)
        else:
            w = self.widgets[self.sender().text()]
            if w[1]:
                w[1].setEnabled(False)

class MonitoringWidget(ElevatedFeatureWidget, Ui_MonitoringWidget):
    def __init__(self, parent, main, feature):
        ElevatedFeatureWidget.__init__(self, parent, feature)
        self.main = main
        self.setupUi(self)

        QObject.connect(self.btn_save, SIGNAL('clicked()'), self.save)
        QObject.connect(self.btn_cancel, SIGNAL('clicked()'), self.stop)

        self.basisPakketWidget = BasisPakketWidget(self)
        self.lyt_basispakket.addWidget(self.basisPakketWidget)

        self.bufferStrookHellingWidget = BufferStrookHellingWidget(self)
        self.lyt_bufferstrook.addWidget(self.bufferStrookHellingWidget)

    def save(self):
        print "basispakket =", self.basisPakketWidget.getValue()
        success = self.saveFeature()
        if success:
            self.stop()

    def stop(self):
        self.btn_save.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        QCoreApplication.processEvents()
        self.btn_save.repaint()
        self.btn_cancel.repaint()
        self.parent.close()

class MonitoringWindow(QMainWindow):
    def __init__(self, main, feature):
        QMainWindow.__init__(self, main.iface.mainWindow())
        self.main = main
        self.feature = feature

        self.monitoringWidget = MonitoringWidget(self, self.main, self.feature)
        self.setCentralWidget(self.monitoringWidget)

        self.setMinimumSize(1200, 1000)
