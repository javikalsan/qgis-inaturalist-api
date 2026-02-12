import os
from typing import Optional

from PyQt5.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon

from .inaturalist_dialog import InaturalistDialog


class Inaturalist:
    def __init__(self, iface) -> None:
        self.iface = iface
        self.dialog: InaturalistDialog = InaturalistDialog()
        self.action: Optional[QAction] = None

    def initGui(self) -> None:
        icon: str = os.path.join(os.path.dirname(__file__), "icons", "iNaturalist.png")
        self.action = QAction(
            QIcon(icon), "iNaturalist Observations", self.iface.mainWindow()
        )
        self.action.setToolTip("<b>iNaturalist Observations</b>")
        self.action.setStatusTip("Load iNaturalist Observations")
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("iNaturalist", self.action)

    def unload(self) -> None:
        if self.action is not None:
            self.iface.removeToolBarIcon(self.action)
            self.iface.removePluginMenu("iNaturalist", self.action)
            del self.action

    def run(self) -> None:
        self.dialog.show()
        self.dialog.exec_()
