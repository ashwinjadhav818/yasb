from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.volume import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QWheelEvent
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import ctypes

# Constants from the Windows API
VK_VOLUME_UP = 0xAF
VK_VOLUME_DOWN = 0xAE
KEYEVENTF_KEYUP = 0x0002

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

class VolumeWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
        self,
        label: str,
        label_alt: str,
        volume_icons: list[str],
        update_interval: int,
        callbacks: dict[str, str]
    ):
        super().__init__(class_name="volume-widget")
        self._show_alt_label = False
        self._label_content = label
        self._label_alt_content = label_alt

        self._label = QLabel()
        self._label_alt = QLabel()
        self._label.setProperty("class", "label")
        self._label_alt.setProperty("class", "label alt")
        self._volume_icons = volume_icons 
        self.widget_layout.addWidget(self._label)
        self.widget_layout.addWidget(self._label_alt)

        self.register_callback("toggle_label", self._toggle_label)
        self.register_callback("update_label", self._update_label)
        self.register_callback("toggle_mute", self.toggle_mute)  # Register the toggle_mute callback

        self.callback_left = callbacks["on_left"]
        self.callback_right = callbacks["on_right"]
        self.callback_middle = callbacks["on_middle"]
        self.callback_timer = "update_label"
        self.timer_interval = update_interval

        self._label.show()
        self._label_alt.hide()
        
        self.start_timer()

    def _toggle_label(self):
        self._show_alt_label = not self._show_alt_label

        if self._show_alt_label:
            self._label.hide()
            self._label_alt.show()
        else:
            self._label.show()
            self._label_alt.hide()
        
        self._update_label()

    def _update_label(self):
        active_label = self._label_alt if self._show_alt_label else self._label
        active_label_content = self._label_alt_content if self._show_alt_label else self._label_content
        active_label.setText(active_label_content)
        
        try:
            current_mute_status = volume.GetMute()
            volume_level = round(volume.GetMasterVolumeLevelScalar() * 100)
            self.setToolTip(f'Volume {volume_level}')

            volume_icon = ""
            if self._volume_icons:
                if current_mute_status == 1 and len(self._volume_icons) > 0:
                    volume_icon = self._volume_icons[0]
                elif volume_level == 0 and len(self._volume_icons) > 1:
                    volume_icon = self._volume_icons[1]
                elif len(self._volume_icons) > 2:
                    idx = int(volume_level/(100/(len(self._volume_icons) - 2))) + 2
                    if idx >= len(self._volume_icons):
                        idx = len(self._volume_icons) - 1
                    volume_icon = self._volume_icons[idx]
                active_label.setText(active_label_content.format(volume_icon=volume_icon, volume_level=volume_level))
            
        except Exception:
            active_label.setText(active_label_content)

    def _simulate_key_press(self, vk_code):
        # Simulate key press
        ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
        # Simulate key release
        ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)

    def _increase_volume(self):
        self._update_label()
        self._simulate_key_press(VK_VOLUME_UP)

    def _decrease_volume(self):
        self._update_label()
        self._simulate_key_press(VK_VOLUME_DOWN)

    def wheelEvent(self, event: QWheelEvent):
        if event.angleDelta().y() > 0:
            self._increase_volume()
        elif event.angleDelta().y() < 0:
            self._decrease_volume()

    def toggle_mute(self):
        current_mute_status = volume.GetMute()
        volume.SetMute(not current_mute_status, None)
        self._update_label()
