# -*- coding: utf-8 -*-
"""Initialisation module for QGis plugin.

This module contains a classFactory for QGis to be able to initialise the
plugin.
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


def classFactory(iface):
    """Initialise the plugin returning an instance of the main class.

    Parameters
    ----------
    iface : QGisInterface
            The instance of the QGis interface we're running in.

    Returns
    -------
    erosiebezwaren.Erosiebezwaren
        An instance of the main class of this plugin (Erosiebezwaren).

    """
    from erosiebezwaren import Erosiebezwaren
    return Erosiebezwaren(iface)
