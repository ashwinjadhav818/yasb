import logging
import yaml
import json
from core.utils.komorebi.client import KomorebiClient
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
import core.utils.alert_dialog

class KomorebiConfig():
    def __init__(self):
        self.komorebic = KomorebiClient()
        try:
            self.config_path = self.komorebic.configuration()
            if not self.config_path:
                raise Exception("Configuration could not be opened")
        except Exception:
            logging.exception(f"Could not open Komorebi configuration")
            return

        with open(self.config_path) as f:
            # since 3.7 dicts are guaranteed to keep insertion order
            # We use yaml to load json because json is subset of yaml and
            # yaml handles trailing commas, which komorebi allows
            self.config = yaml.load(f, yaml.CLoader)
            if type(self.config) != dict:
                logging.error("self.config is not JSON object")
                return

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value

    def save(self):
        if "yasb_save_confirmed" in self.config and self.config["yasb_save_confirmed"] == True:
            self._save()
        else:
            mb = QMessageBox()
            mb.setStyleSheet(core.utils.alert_dialog.dialog_stylesheet)
            mb.setProperty("class", "dialog")
            mb.setWindowTitle("")
            mb.setText("Warning: This will overwrite the komorebi.json "
                       "configuration, removing any custom formatting "
                       "it might have.\n"
                       "\n"
                       "If you only want to change the workspace name "
                       "temporarily, you can use 'rename_temporary' "
                       "callback. (Default middle button.)\n"
                       "\n"
                       "Do you want write the configuration?")
            mb.addButton(QMessageBox.StandardButton.Yes)
            mb.addButton(QMessageBox.StandardButton.No)
            mb.setWindowModality(Qt.WindowModality.ApplicationModal)
            mb.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
            reply = mb.exec()
            if reply == QMessageBox.StandardButton.Yes:
                self.config["yasb_save_confirmed"] = True
                self._save()

    def _save(self):
        if self.config_path is not None:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)

    def workspace_name(self, ws_monitor, ws_index, ws_name):
        if "monitors" not in self.config:
            self.config["monitors"] = list()
        monitors = self.config["monitors"]
        while len(monitors) <= ws_monitor:
            monitors.append({})
        monitor = monitors[ws_monitor]
        if "workspaces" not in monitor:
            monitor["workpaces"] = list()
        workspaces = monitor["workspaces"]

        i = 1
        while len(workspaces) <= ws_index:
            ws = {}
            ws["name"] = str(i)
            ws["layout"] = "BSP"
            workspaces.append(ws)
            i += 1

        workspaces[ws_index]["name"] = ws_name

