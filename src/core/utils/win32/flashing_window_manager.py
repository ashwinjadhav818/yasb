import functools
from collections import OrderedDict
from PyQt6.QtCore import QObject, pyqtSignal
from win32gui import GetForegroundWindow
from core.utils.win32.windows import ShellEvent, WinEvent, FlashListEvent
from core.event_service import EventService
from core.utils.win32.utilities import get_hwnd_info


class FlashingWindowManager(QObject):
    flashing = pyqtSignal(int, ShellEvent)
    window_name_change = pyqtSignal(int, WinEvent)
    remove_flashing = pyqtSignal(int)
    foreground_change = pyqtSignal(int, WinEvent)

    def __init__(self):
        super().__init__()
        self._event_service = EventService()

        self.flashing.connect(self._on_flashing_event)
        self._event_service.register_event(ShellEvent.Flashing, self.flashing)

        self.remove_flashing.connect(self._on_remove_flashing_event)
        self._event_service.register_event(FlashListEvent.Remove, self.remove_flashing)

        self.foreground_change.connect(self._on_focus_change_event)
        self._event_service.register_event(WinEvent.EventSystemForeground, self.foreground_change)
        # self._event_service.register_event(WinEvent.EventSystemMoveSizeEnd, self.foreground_change)
        # self._event_service.register_event(WinEvent.EventSystemCaptureEnd, self.foreground_change)

        self.window_name_change.connect(self._on_window_name_change_event)
        self._event_service.register_event(WinEvent.EventObjectNameChange, self.window_name_change)

        self._window_list = OrderedDict()

    def _on_flashing_event(self, hwnd: int, event: ShellEvent) -> None:
        if hwnd != GetForegroundWindow() and hwnd not in self._window_list:
            win_info = get_hwnd_info(hwnd)
            if win_info:
                self._window_list[hwnd] = win_info
                self._publish_window_list()

    def _on_window_name_change_event(self, hwnd: int, event: WinEvent) -> None:
        if hwnd in self._window_list:
            win_info = get_hwnd_info(hwnd)
            if win_info:
                self._window_list[hwnd] = win_info
                self._publish_window_list()

    def _on_remove_flashing_event(self, hwnd: int) -> None:
        if hwnd in self._window_list:
            del self._window_list[hwnd]
            self._publish_window_list()

    def _on_focus_change_event(self, hwnd: int, event: WinEvent) -> None:
        if hwnd in self._window_list:
            del self._window_list[hwnd]
            self._publish_window_list()

    def _publish_window_list(self) -> None:
        publish_list = list()
        for hwnd in self._window_list:
            win_info = get_hwnd_info(hwnd)
            if win_info:
                publish_list.append(win_info)

        self._event_service.emit_event(FlashListEvent.Publish, publish_list)
