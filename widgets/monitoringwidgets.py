# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

class MonitoringItemWidget(QWidget):
    valueChanged = pyqtSignal()

    def __init__(self, parent):
        QWidget.__init__(self, parent)

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

class BasisPakketWidget(MonitoringItemWidget):
    def __init__(self, parent):
        MonitoringItemWidget.__init__(self, parent)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.horMaxSizePolicy = QSizePolicy()
        self.horMaxSizePolicy.setHorizontalPolicy(QSizePolicy.Maximum)

        self.geenMtrglEnabled = True

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
            label = QLabel(self.periods[i][1])
            label.setSizePolicy(self.horMaxSizePolicy)
            self.layout.addWidget(label, 0, i+1)

        for i in range(len(self.options)):
            label = QLabel(self.options[i][1])
            label.setSizePolicy(self.horMaxSizePolicy)
            self.layout.addWidget(label, i+1, 0)

        for i in range(len(self.options)):
            for j in range(len(self.periods)):
                option = self.options[i]
                period = self.periods[j]
                cell = CheckableCell('%s_%s' % (period[0], option[0]), '', self)
                QObject.connect(cell, SIGNAL('toggled(bool)'), self._validate)
                QObject.connect(cell, SIGNAL('toggled(bool)'), lambda x: self.valueChanged.emit())
                self.cells[period[0]][option[0]] = cell
                self.layout.addWidget(self.cells[period[0]][option[0]], i+1, j+1)

    def _validate(self, *args):
        for p in self.periods:
            geenChecked = [self.cells[p[0]][i] for i in self.cells[p[0]] if i.startswith('geen') and self.cells[p[0]][i].isChecked()]
            geenMtrgl = [self.cells[p[0]][i] for i in self.cells[p[0]] if i == 'geenmtrgl'][0]
            if len(geenChecked) > 0:
                for c in self.cells[p[0]].values():
                    if c != geenChecked[0]:
                        c.setValue(False)
                        c.setEnabled(False)
            else:
                for c in self.cells[p[0]].values():
                    if not self.geenMtrglEnabled and c == geenMtrgl:
                        c.setEnabled(False)
                    else:
                        c.setEnabled(True)

    def setGeenMtrglEnabled(self, enabled):
        self.geenMtrglEnabled = enabled
        self._validate()

    def setValue(self, value):
        if value:
            ls = [i.strip() for i in value.strip().split(';')]
        else:
            ls = []

        for p in self.cells:
            for o in self.cells[p]:
                self.cells[p][o].setValue('%s_%s' % (p, o) in ls)

    def getValue(self):
        return '; '.join(
            sorted(['voor_'+c for c in self.cells['voor'] if self.cells['voor'][c].isChecked()]) + \
            sorted(['na_'+c for c in self.cells['na'] if self.cells['na'][c].isChecked()])
        )

class TeeltTechnischWidget(MonitoringItemWidget):
    def __init__(self, parent):
        MonitoringItemWidget.__init__(self, parent)

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.options = [
            ('nietkerend', 'Niet-kerende'),
            ('directinzaai', 'Direct inzaai'),
            ('strip-till', 'Strip-till'),
            ('drempeltjes', 'Drempeltjes'),
            ('bioaardappel', 'Bio-aardappel'),
            ('diepetandbew', 'Diepe tandbewerking'),
            ('hoogtelijnen', 'Hoogtelijnen'),
            ('graszones', 'Graszones'),
            ('geenmtrgl', 'Geen maatregel'),
            ('geeninfo', 'Geen info')
        ]

        self.cells = {}
        self.disabledCells = []

        for i in range(len(self.options)):
            self.layout.addWidget(QLabel(self.options[i][1]), i+1, 0)

        for i in range(len(self.options)):
            option = self.options[i]
            cell = CheckableCell(option[0], '', self)
            QObject.connect(cell, SIGNAL('toggled(bool)'), self._validate)
            QObject.connect(cell, SIGNAL('toggled(bool)'), lambda x: self.valueChanged.emit())
            self.cells[option[0]] = cell
            self.layout.addWidget(self.cells[option[0]], i+1, 1)

    def _validate(self, *args):
        geenChecked = [self.cells[i] for i in self.cells if i.startswith('geen') and self.cells[i].isChecked()]
        if len(geenChecked) > 0:
            for c in self.cells.values():
                if c != geenChecked[0]:
                    c.setValue(False)
                    c.setEnabled(False)
        else:
            for c in self.cells:
                if c in self.disabledCells:
                    self.cells[c].setValue(False)
                    self.cells[c].setEnabled(False)
                else:
                    self.cells[c].setEnabled(True)

    def setValue(self, value):
        if value:
            ls = [i.strip() for i in value.strip().split(';')]
        else:
            ls = []

        for p in self.cells:
            self.cells[p].setValue(p in ls)

    def getValue(self):
        return '; '.join(sorted([c for c in self.cells if self.cells[c].isChecked()]))

    def setDisabledOptions(self, options):
        self.disabledCells = options
        self._validate()

class BufferStrookHellingWidget(MonitoringItemWidget):
    def __init__(self, parent):
        MonitoringItemWidget.__init__(self, parent)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.options = [
            ['Uniform', ['Parallel', 'Waterscheiding', 'Schuin']],
            ['1 droge vallei', []],
            ['Complex', []]
        ]

        self.widgets = {}

        gb = QGroupBox(self)
        bg = QButtonGroup(self)
        gb.setLayout(QVBoxLayout(gb))
        self.layout.addWidget(gb)

        for i in self.options:
            radio = QRadioButton(i[0], gb)
            QObject.connect(radio, SIGNAL('toggled(bool)'), self._updateParentChild)
            QObject.connect(radio, SIGNAL('toggled(bool)'), lambda x: self.valueChanged.emit())
            gb.layout().addWidget(radio)
            bg.addButton(radio)
            bgx = None

            if len(i[1]) > 0:
                gbx = QGroupBox(gb)
                bgx = QButtonGroup(gb)
                gbx.setLayout(QVBoxLayout(gbx))
                for j in i[1]:
                    radiox = QRadioButton(j, gbx)
                    radiox.setEnabled(False)
                    QObject.connect(radiox, SIGNAL('toggled(bool)'), self._updateParentChild)
                    QObject.connect(radiox, SIGNAL('toggled(bool)'), lambda x: self.valueChanged.emit())
                    self.widgets[j] = (radiox, None, radio)
                    gbx.layout().addWidget(radiox)
                    bgx.addButton(radiox)

                gb.layout().addWidget(gbx)

            self.widgets[i[0]] = (radio, bgx, None)

    def _updateParentChild(self, toggled):
        if toggled:
            w = self.widgets[self.sender().text()]
            if w[1]:
                for b in w[1].buttons():
                    b.setEnabled(True)
        else:
            w = self.widgets[self.sender().text()]
            if w[1]:
                w[1].setExclusive(False)
                for b in w[1].buttons():
                    b.setChecked(False)
                    b.setEnabled(False)
                w[1].setExclusive(True)

    def getValue(self):
        checkedWidgets = [w[0] for w in self.widgets.values() if (
            w[0].isChecked() and w[0].isEnabled() and w[0].text() != 'Uniform')]

        if len(checkedWidgets) == 1:
            return checkedWidgets[0].text()

    def setValue(self, value):
        if value:
            self.widgets[value][0].setChecked(True)

        if value in ('Parallel', 'Waterscheiding', 'Schuin'):
            self.widgets['Uniform'][0].setChecked(True)
