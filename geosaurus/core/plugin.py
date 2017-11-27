# -*- coding: utf-8 -*-

import os

from PyQt4.QtCore import (pyqtSlot, QSize, QSettings, QTranslator, qVersion,
    QCoreApplication)
from PyQt4.QtGui import QAction, QIcon

from ..gui.dialog import GeosaurusDialog

# Get the path for the parent directory of this file.
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


class Geosaurus:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor."""
        self.iface = iface
        self.plugin_dir = __location__
        self.image_dir = os.path.join(__location__, "..", "images")

        # Initialise locale
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(
            __location__, "gui", "i18n", "Geosaurus_{}.qm".format(locale)
        )
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > "4.3.3":
                QCoreApplication.installTranslator(self.translator)

        # Initialise plugin toolbar
        self.toolbar = self.iface.addToolBar(u"Geosaurus")
        self.toolbar.setObjectName(u"Geosaurus")

        self.actions = []

        # Initialise QGIS menu item
        self.menu = self.tr(u"&Geosaurus")

        # Initialise plugin dialogs
        self.dlg = None

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.
        """
        return QCoreApplication.translate("Geosaurus", message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.add_geosaurus_action()

    def add_action(self, icon_filename, text, callback):
        """Creates an action with an icon, assigned to a QToolButton menu."""
        icon_path = os.path.join(self.image_dir, icon_filename)
        icon = QIcon()
        icon.addFile(icon_path, QSize(8, 8))
        action = QAction(icon, text, self.toolbar)
        action.triggered.connect(callback)
        self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        return action

    def add_geosaurus_action(self):
        """
        Creates the actions and tool button required for running tests
        within QGIS.
        """
        self.action = self.add_action(
            "geosaurus.png", "Open Geosaurus Dialog",
            self.open_dialog
        )
        self.toolbar.addAction(self.action)

    @pyqtSlot()
    def open_dialog(self):
        """Adds test data referred to in the test script to the map. Must
        be .shp (shapefile).
        """
        self.dlg = GeosaurusDialog()
        self.dlg.show()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u"&Geosaurus"), action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
