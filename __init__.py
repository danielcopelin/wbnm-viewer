# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WBNMViewer
                                 A QGIS plugin
 View and analyse WBNM hydrology model results
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-09-04
        copyright            : (C) 2020 by Dan Copelin
        email                : danielcopelin@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load WBNMViewer class from file WBNMViewer.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .wbnm_viewer import WBNMViewer
    return WBNMViewer(iface)