# -*- coding: utf-8 -*-
"""
This script initializes the plugin, making it known to QGIS.
"""


def classFactory(iface):
    """Load ScriptAssistant class from file plugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """

    from .core.plugin import Geosaurus
    return Geosaurus(iface)
