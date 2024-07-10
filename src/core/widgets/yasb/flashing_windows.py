import logging
from copy import deepcopy
from typing import Union

from win32gui import SetForegroundWindow
from settings import APP_BAR_TITLE
from core.utils.win32.windows import FlashListEvent, WinEvent
from core.utils.win32.utilities import show_window
from core.event_service import EventService
from PyQt6.QtCore import pyqtSignal, Qt, QEvent
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.flashing_windows import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QMouseEvent

IGNORED_TITLES = ['', ' ']
IGNORED_CLASSES = ['WorkerW']
IGNORED_PROCESSES = ['SearchHost.exe']
IGNORED_YASB_TITLES = [APP_BAR_TITLE]
IGNORED_YASB_CLASSES = [
    'Qt662QWindowIcon',
    'Qt662QWindowIcon',
    'Qt662QWindowToolSaveBits',
    'Qt662QWindowToolSaveBits'
]

try:
    from core.utils.win32.event_listener import SystemEventListener
except ImportError:
    SystemEventListener = None
    logging.warning("Failed to load Win32 System Event Listener")

class FlashingWindowsWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA
    foreground_change = pyqtSignal(int, WinEvent)
    flash_list_publish = pyqtSignal(list)
    event_listener = SystemEventListener

    def __init__(
            self,
            label: str,
            label_alt: str,
            callbacks: dict[str, str],
            ignore_window: dict[str, list[str]],
            max_length: int,
            max_length_ellipsis: str
    ):
        super().__init__(class_name="flashing-windows-widget")

        self._win_info = None
        self._show_alt = False
        self._label = label
        self._label_alt = label_alt
        self._max_length = max_length
        self._max_length_ellipsis = max_length_ellipsis
        self._event_service = EventService()
        self.register_callback("activate_window", self._activate_window)
        self.register_callback("toggle_label", self._toggle_title_text)
        self.register_callback("remove_window", self._remove_window)
        self.register_callback("do_nothing", self._do_nothing)
        self._ignore_window = ignore_window

        if not callbacks:
            callbacks = {
                "on_left": "activate_window",
                "on_middle": "toggle_label",
                "on_right": "remove_window"
            }

        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']

        self.flash_list_publish.connect(self._on_flash_list_publish)
        self._event_service.register_event(FlashListEvent.Publish, self.flash_list_publish)

    def _on_flash_list_publish(self, win_list: list):
        self.clearLayout(self.widget_layout)

        for win_info in win_list:
            widget = QLabel()
            widget.setProperty("class", "label")
            widget.setProperty("win_info", win_info)
            widget.setProperty("show_alt", False)
            widget.installEventFilter(self)
            widget.setText("foo")
            self.widget_layout.addWidget(widget)
            # This needs to come after the layout, otherwise it will call show and create a window
            self._update_window_title(widget, win_info)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self._run_label_callback(self.callback_left, source)
            elif event.button() == Qt.MouseButton.MiddleButton:
                self._run_label_callback(self.callback_middle, source)
            elif event.button() == Qt.MouseButton.RightButton:
                self._run_label_callback(self.callback_right, source)
        return False

    def _run_label_callback(self, callback_str: str, source: QLabel):
        try:
            self.callbacks[callback_str](source)
        except Exception:
            logging.exception(f"Failed to execute callback of type '{callback_str}' with args: {source}")

    # override
    def _handle_mouse_events(self, event: QMouseEvent):
        # don't handle mouse events in the base widget
        pass

    def _toggle_title_text(self, source: QLabel) -> None:
        source.setProperty("show_alt", not source.property("show_alt"))
        self._update_window_title(source, source.property("win_info"))

    def _activate_window(self, source: QLabel) -> None:
        # just setting the foreground window should in theory be enough, but maybe the window was closed
        self._event_service.emit_event(FlashListEvent.Remove, source.property("win_info")["hwnd"])
        show_window(source.property("win_info")["hwnd"])

    def _remove_window(self, source: QLabel) -> None:
        self._event_service.emit_event(FlashListEvent.Remove, source.property("win_info")["hwnd"])

    def _do_nothing(self, source: QLabel) -> None:
        pass

    def _update_window_title(self, widget: QLabel, win_info: dict) -> None:
        try:
            win_info = deepcopy(win_info)
            title = win_info['title']
            process = win_info['process']
            class_name = win_info['class_name']

            if (title.strip() in self._ignore_window['titles'] or
                    class_name in self._ignore_window['classes'] or
                    process in self._ignore_window['processes']):
                widget.hide()
                return
            else:
                if self._max_length and len(win_info['title']) > self._max_length:
                    truncated_title = f"{win_info['title'][:self._max_length]}{self._max_length_ellipsis}"
                    win_info['title'] = truncated_title
                    widget.setText(" ")

                self._update_text(widget, win_info)

                if widget.isHidden():
                    widget.show()
        except Exception:
            logging.exception(
                f"Failed to update active window title for window with HWND {win_info['hwnd']} emitted by event {event}"
            )

    def _update_text(self, widget: QLabel, win_info: dict):
        if widget.property("show_alt"):
            try:
                widget.setText(self._label_alt.format(win=win_info))
            except Exception:
                widget.setText(self._label_alt)
        else:
            try:
                widget.setText(self._label.format(win=win_info))
            except Exception:
                widget.setText(self._label)
