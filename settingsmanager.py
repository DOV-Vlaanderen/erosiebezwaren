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

class SettingsManager(object):
    def __init__(self, main):
        self.main = main

        self.map = {
            'layers/tempSelectionPolygons': 'bezwaren_selectie',
            'layers/tempSelectionPoints': 'bezwaren_puntselectie',
            'layers/bezwaren': 'percelenkaart_view',
            'layers/oudebezwaren': 'oude_bezwaren',
            'layers/pijlen': 'Pijlen',
            'layers/polygonen': 'Polygonen',
            'paths/bezwaren': 'bezwaren'
        }

    def setValue(self, key, value):
        self.map[key] = value

    def getValue(self, key):
        return self.map.get(key, None)
