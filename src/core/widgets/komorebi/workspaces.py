import logging
import time
from PyQt6.QtWidgets import QPushButton, QWidget, QHBoxLayout, QLabel, QLineEdit, QApplication
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, pyqtSlot, Qt, QPoint
from PyQt6.QtGui import QMouseEvent, QKeyEvent
from typing import Literal
from contextlib import suppress
from core.utils.win32.utilities import get_monitor_hwnd
from core.event_service import EventService
from core.event_enums import KomorebiEvent
from core.widgets.base import BaseWidget
from core.utils.komorebi.client import KomorebiClient
from core.utils.komorebi.config import KomorebiConfig
from core.validation.widgets.komorebi.workspaces import VALIDATION_SCHEMA
from ctypes import windll
import win32con

try:
    from core.utils.komorebi.event_listener import KomorebiEventListener
except ImportError:
    KomorebiEventListener = None
    logging.warning("Failed to load Komorebi Event Listener")

WorkspaceStatus = Literal["EMPTY", "POPULATED", "ACTIVE"]
WORKSPACE_STATUS_EMPTY: WorkspaceStatus = "EMPTY"
WORKSPACE_STATUS_POPULATED: WorkspaceStatus = "POPULATED"
WORKSPACE_STATUS_ACTIVE: WorkspaceStatus = "ACTIVE"

class RenameWidget(QWidget):
    def __init__(self, launch_widget, permanent:bool, ws_monitor:int, ws_index:int, ws_name:str):
        super().__init__()
        button_pos = launch_widget.mapToGlobal(QPoint(0,0))
        # we don't set parent, so we need to fetch the style sheet
        self.setStyleSheet(launch_widget.window().styleSheet())
        self.permanent = permanent
        self.widget_layout = QHBoxLayout()
        self.setLayout(self.widget_layout)
        self.setProperty("class", "rename-widget")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.ws_monitor = ws_monitor
        self.ws_index = ws_index
        self.komorebic = KomorebiClient()

        self.edit_widget = QLineEdit()
        self.edit_widget.setProperty("class", "line-edit")
        self.edit_widget.returnPressed.connect(self.submit)
        self.edit_widget.setText(ws_name)
        self.edit_widget.editingFinished.connect(self.close)
        self.widget_layout.addWidget(self.edit_widget)
        self.show()
        screen_geometry = self.edit_widget.screen().geometry();
        dx = 0 
        dy = 0
        if button_pos.x() + self.width() > screen_geometry.right():
            dx = button_pos.x() + self.width() - screen_geometry.right()
        if button_pos.y() + self.height() > screen_geometry.bottom():
            dy = button_pos.y() + self.height() - screen_geometry.bottom()
        button_pos.setX(button_pos.x() - dx)
        button_pos.setY(button_pos.y() - dy)
        self.move(button_pos)
        hwnd = int(self.winId())
        exStyle = windll.user32.GetWindowLongPtrW(hwnd, win32con.GWL_EXSTYLE)
        windll.user32.SetWindowLongPtrW(hwnd, win32con.GWL_EXSTYLE, exStyle & ~win32con.WS_EX_NOACTIVATE & ~win32con.WS_EX_TOPMOST)
        self.edit_widget.selectAll()
        self.edit_widget.setFocus()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def submit(self):
        new_name = self.edit_widget.text()
        self.komorebic.workspace_name(self.ws_monitor, self.ws_index, new_name)
        if self.permanent:
            config = KomorebiConfig()
            config.workspace_name(self.ws_monitor, self.ws_index, new_name)
            config.save()

        self.close()

class WorkspaceButton(QPushButton):

    def __init__(self, workspace_index: int, label: str | None = None, preview_workspace: bool = False, callbacks: dict[str, str] = {}):
        super().__init__()
        self.komorebic = KomorebiClient()
        self.workspace_name = ""
        self.workspace_monitor = -1
        self.workspace_index = -1

        # XXX TODO: this is disabled for now
        self._preview_workspace = False # preview_workspace

        self.hover_enter_debounce = QTimer()
        self.hover_enter_debounce.setInterval(500)
        self.hover_enter_debounce.setSingleShot(True)
        self.hover_enter_debounce.timeout.connect(self.sendHoverEnter)

        self.callbacks = dict()

        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']

        self.register_callback("activate", self.activate_workspace)
        self.register_callback("rename_temporary", self.rename_temporary)
        self.register_callback("rename_permanent", self.rename_permanent)
        self.register_callback("do_nothing", self.do_nothing)

        self.event_service = EventService()
        self.workspace_index = workspace_index
        self.status = WORKSPACE_STATUS_EMPTY
        self.setProperty("class", "ws-btn")
        self.setText(label if label else str(workspace_index + 1))
        self.clicked.connect(self.activate_workspace)
        self.hide()
        self.isPressed = False

    def register_callback(self, callback_name, fn):
        self.callbacks[callback_name] = fn

    def update_and_redraw(self, status: WorkspaceStatus):
        self.status = status
        self.setProperty("class", f"ws-btn {status.lower()}")
        self.setStyleSheet('')

    def activate_workspace(self):
        try:
            self.komorebic.activate_workspace(self.workspace_index)
        except Exception:
            logging.exception(f"Failed to focus workspace at index {self.workspace_index}")

    def rename_temporary(self):
        self.rename_widget = RenameWidget(self, False, self.workspace_monitor, self.workspace_index, self.workspace_name)

    def rename_permanent(self):
        self.rename_widget = RenameWidget(self, True, self.workspace_monitor, self.workspace_index, self.workspace_name)

    def do_nothing(self):
        pass

    def sendHoverEnter(self):
        self.event_service.emit_event(
            WorkspaceButtonEvent.HoverEnter,
            self.workspace_index,
            self.parent().parent().parent()
        )

    def sendHoverLeave(self):
        self.event_service.emit_event(
            WorkspaceButtonEvent.HoverLeave,
            self.workspace_index,
            self.parent().parent().parent(),
            self.isPressed
        )

    def enterEvent(self, event) -> None:
        if not self._preview_workspace:
            return super().enterEvent(event)

        if self.status is not WORKSPACE_STATUS_ACTIVE:
            self.hover_enter_debounce.start()

        return super().enterEvent(event)

    def leaveEvent(self, a0) -> None:
        if not self._preview_workspace:
            return super().leaveEvent(a0)

        self.hover_enter_debounce.stop()
        self.sendHoverLeave()

        if self.isPressed:
            self.isPressed = False

        return super().leaveEvent(a0)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.callbacks[self.callback_left]()
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.callbacks[self.callback_middle]()
        elif event.button() == Qt.MouseButton.RightButton:
            self.callbacks[self.callback_right]()

class WorkspaceWidget(BaseWidget):
    k_signal_connect = pyqtSignal(dict)
    k_signal_update = pyqtSignal(dict, dict)
    k_signal_disconnect = pyqtSignal()

    validation_schema = VALIDATION_SCHEMA
    event_listener = KomorebiEventListener

    def __init__(
            self,
            label_offline: str,
            label_workspace_btn: str,
            label_default_name: str,
            label_zero_index: bool,
            hide_empty_workspaces: bool,
            preview_workspace: bool,
            callbacks: dict[str, str]
    ):
        super().__init__(class_name="komorebi-workspaces")

        self._event_service = EventService()
        self._komorebic = KomorebiClient()
        self._label_workspace_btn = label_workspace_btn
        self._label_default_name = label_default_name
        self._label_zero_index = label_zero_index
        self._komorebi_screen = None
        self._komorebi_workspaces = []
        self._prev_workspace_index = None
        self._curr_workspace_index = None
        self._workspace_buttons: list[WorkspaceButton] = []
        self._hide_empty_workspaces = hide_empty_workspaces
        self.callbacks = callbacks
        # XXX TODO: this is disabled for now
        self._preview_workspace = False # preview_workspace
        self._prev_workspace_on_mouse_index = None
        self._workspace_on_mouse_index = None

        self._workspace_focus_events = [
            KomorebiEvent.CycleFocusWorkspace.value,
            KomorebiEvent.CycleFocusMonitor.value,
            KomorebiEvent.FocusMonitorWorkspaceNumber.value,
            KomorebiEvent.FocusMonitorNumber.value,
            KomorebiEvent.FocusWorkspaceNumber.value
        ]

        self._update_buttons_event_watchlist = [
            KomorebiEvent.EnsureWorkspaces.value,
            KomorebiEvent.Manage.value,
            KomorebiEvent.MoveContainerToWorkspaceNumber.value,
            KomorebiEvent.NewWorkspace.value,
            KomorebiEvent.ReloadConfiguration.value,
            KomorebiEvent.SendContainerToMonitorNumber.value,
            KomorebiEvent.SendContainerToWorkspaceNumber.value,
            KomorebiEvent.Unmanage.value,
            KomorebiEvent.WatchConfiguration.value,
            KomorebiEvent.WorkspaceName.value
        ]

        # Disable default mouse event handling inherited from BaseWidget
        self.mousePressEvent = None

        # Status text shown when komorebi state can't be retrieved
        self._offline_text = QLabel()
        self._offline_text.setText(label_offline)
        self._offline_text.setProperty("class", "offline-status")

        self._callbacks = callbacks

        # Construct container which holds workspace buttons
        self._workspace_container_layout: QHBoxLayout = QHBoxLayout()
        self._workspace_container_layout.setSpacing(0)
        self._workspace_container_layout.setContentsMargins(0, 0, 0, 0)
        self._workspace_container_layout.addWidget(self._offline_text)
        self._workspace_container: QWidget = QWidget()
        self._workspace_container.setLayout(self._workspace_container_layout)
        self._workspace_container.setProperty("class", "komorebi-workspaces-container")
        self._workspace_container.hide()

        self.widget_layout.addWidget(self._offline_text)
        self.widget_layout.addWidget(self._workspace_container)
        self._register_signals_and_events()

    def _register_signals_and_events(self):
        self.k_signal_connect.connect(self._on_komorebi_connect_event)
        self.k_signal_update.connect(self._on_komorebi_update_event)
        self.k_signal_disconnect.connect(self._on_komorebi_disconnect_event)

        self._event_service.register_event(KomorebiEvent.KomorebiConnect, self.k_signal_connect)
        self._event_service.register_event(KomorebiEvent.KomorebiDisconnect, self.k_signal_disconnect)
        self._event_service.register_event(KomorebiEvent.KomorebiUpdate, self.k_signal_update)

    def _reset(self):
        self._komorebi_state = None
        self._komorebi_screen = None
        self._komorebi_workspaces = []
        self._curr_workspace_index = None
        self._prev_workspace_index = None
        self._workspace_buttons = []
        self._clear_container_layout()

    def _on_komorebi_connect_event(self, state: dict) -> None:
        self._reset()
        self._hide_offline_status()

        if self._update_komorebi_state(state):
            self._add_or_update_buttons()

    def _on_komorebi_disconnect_event(self) -> None:
        self._show_offline_status()

    def _on_komorebi_update_event(self, event: dict, state: dict) -> None:
        if self._update_komorebi_state(state):
            if event['type'] == KomorebiEvent.MoveWorkspaceToMonitorNumber.value:
                if event['content'] != self._komorebi_screen['index']:
                    workspaces = self._komorebic.get_workspaces(self._komorebi_screen)
                    screen_workspace_indexes = list(map(lambda ws: ws['index'], workspaces))
                    button_workspace_indexes = list(map(lambda ws: ws.workspace_index, self._workspace_buttons))
                    unknown_indexes = set(button_workspace_indexes) - set(screen_workspace_indexes)

                    if len(unknown_indexes) >= 0:
                        for workspace_index in unknown_indexes:
                            self._try_remove_workspace_button(workspace_index)

                self._add_or_update_buttons()

            elif event['type'] in self._workspace_focus_events or self._has_active_workspace_index_changed():
                try:
                    prev_workspace_button = self._workspace_buttons[self._prev_workspace_index]
                    self._update_button(prev_workspace_button)
                    new_workspace_button = self._workspace_buttons[self._curr_workspace_index]
                    self._update_button(new_workspace_button)
                except (IndexError, TypeError):
                    self._add_or_update_buttons()

            elif event['type'] in self._update_buttons_event_watchlist:
                self._add_or_update_buttons()

    def _clear_container_layout(self):
        for i in reversed(range(self._workspace_container_layout.count())):
            old_workspace_widget = self._workspace_container_layout.itemAt(i).widget()
            self._workspace_container_layout.removeWidget(old_workspace_widget)
            old_workspace_widget.setParent(None)

    def _update_komorebi_state(self, komorebi_state: dict) -> bool:
        try:
            self._screen_hwnd = get_monitor_hwnd(int(QWidget.winId(self)))
            self._komorebi_state = komorebi_state
            if self._komorebi_state:
                self._komorebi_screen = self._komorebic.get_screen_by_hwnd(self._komorebi_state, self._screen_hwnd)
                self._komorebi_workspaces = self._komorebic.get_workspaces(self._komorebi_screen)

                focused_workspace = self._get_focused_workspace()

                if focused_workspace:
                    self._prev_workspace_index = self._curr_workspace_index
                    self._curr_workspace_index = focused_workspace['index']

                return True
        except TypeError:
            return False

    def _get_focused_workspace(self):
        return self._komorebic.get_focused_workspace(self._komorebi_screen)

    def _has_active_workspace_index_changed(self):
        return self._prev_workspace_index != self._curr_workspace_index

    def _get_workspace_new_status(self, workspace) -> WorkspaceStatus:
        if self._curr_workspace_index == workspace['index']:
            return WORKSPACE_STATUS_ACTIVE
        elif self._komorebic.get_num_windows(workspace) > 0:
            return WORKSPACE_STATUS_POPULATED
        else:
            return WORKSPACE_STATUS_EMPTY

    def _update_button(self, workspace_btn: WorkspaceButton) -> None:
        workspace_index = workspace_btn.workspace_index
        workspace = self._komorebic.get_workspace_by_index(self._komorebi_screen, workspace_index)
        workspace_status = self._get_workspace_new_status(workspace)

        if self._hide_empty_workspaces and workspace_status == WORKSPACE_STATUS_EMPTY:
            workspace_btn.hide()
        else:
            workspace_btn.workspace_name = workspace["name"]
            workspace_btn.workspace_index = workspace_index
            workspace_btn.workspace_monitor = self._komorebi_screen["index"]
            label = self._format_workspace_label(workspace)
            workspace_btn.setText(label if label else str(workspace_index + 1))
            workspace_btn.show()
            if workspace_btn.status != workspace_status:
                workspace_btn.update_and_redraw(workspace_status)

    def _add_or_update_buttons(self) -> None:
        buttons_added = False
        for workspace_index, workspace in enumerate(self._komorebi_workspaces):
            try:
                button = self._workspace_buttons[workspace_index]
            except IndexError:
                button = self._try_add_workspace_button(workspace_index)
                buttons_added = True
            self._update_button(button)

        if buttons_added:
            self._workspace_buttons.sort(key=lambda btn: btn.workspace_index)
            self._clear_container_layout()

            for workspace_btn in self._workspace_buttons:
                self._workspace_container_layout.addWidget(workspace_btn)

    def _get_workspace_label(self, workspace_index):
        workspace = self._komorebic.get_workspace_by_index(self._komorebi_screen, workspace_index)
        return self._format_workspace_label(workspace)

    def _format_workspace_label(self, workspace) -> str:
        monitor_index = self._komorebi_screen['index']
        ws_index = workspace['index'] if self._label_zero_index else workspace['index'] + 1
        ws_monitor_index = monitor_index if self._label_zero_index else monitor_index + 1
        ws_name = workspace['name'] if workspace['name'] else self._label_default_name.format(
            index=ws_index,
            monitor_index=ws_monitor_index
        )
        return self._label_workspace_btn.format(
            name=ws_name,
            index=ws_index,
            monitor_index=ws_monitor_index
        )

    def _try_add_workspace_button(self, workspace_index: int) -> WorkspaceButton:
        workspace_button_indexes = [ws_btn.workspace_index for ws_btn in self._workspace_buttons]

        if workspace_index not in workspace_button_indexes:
            ws_label = self._get_workspace_label(workspace_index)
            workspace_btn = WorkspaceButton(workspace_index, ws_label, self._preview_workspace, self.callbacks)

            self._workspace_buttons.append(workspace_btn)

            return workspace_btn

    def _try_remove_workspace_button(self, workspace_index: int) -> None:
        with suppress(IndexError):
            workspace_button = self._workspace_buttons[workspace_index]
            workspace_button.hide()

    def _show_offline_status(self):
        self._offline_text.show()
        self._workspace_container.hide()

    def _hide_offline_status(self):
        self._offline_text.hide()
        self._workspace_container.show()
