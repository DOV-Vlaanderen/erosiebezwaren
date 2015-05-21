class SettingsManager(object):
    def __init__(self, main):
        self.main = main

        self.map = {
            'layers/tempSelection': 'bezwaren_selectie',
            'layers/bezwaren': 'bezwarenkaart',
            'layers/oudebezwaren': 'oude_bezwaren',
            'layers/percelen': 'percelenkaart',
            'layers/pijlen': 'Pijlen',
            'layers/polygonen': 'Polygonen',
            'paths/bezwaren': 'bezwaren'
        }

    def setValue(self, key, value):
        self.map[key] = value

    def getValue(self, key):
        return self.map.get(key, None)
