from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.volume import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

class VolumeWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
        self,
        label: str,
        label_alt: str,
        update_interval: int,
        volume_icons: list[str],  # Adjusted for volume icons
        callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="volume-widget")
        self._show_alt_label = False
        self._label_content = label
        self._label_alt_content = label_alt
        self._volume_icons = volume_icons  # Store the volume icons

        self._label = QLabel()
        self._label_alt = QLabel()
        self._label.setProperty("class", "label")
        self._label_alt.setProperty("class", "label alt")
        self.widget_layout.addWidget(self._label)
        self.widget_layout.addWidget(self._label_alt)

        self.register_callback("toggle_label", self._toggle_label)
        self.register_callback("update_label", self._update_label)

        self.callback_left = callbacks.get("on_left", "toggle_label")  # Default callback for left click
        self.callback_right = callbacks.get("on_right", "do_nothing")  # Default callback for right click
        self.callback_middle = callbacks.get("on_middle", "do_nothing")  # Default callback for middle click
        self.callback_timer = "update_label"

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
        # Determine which label is active
        active_label = self._label_alt if self._show_alt_label else self._label
        active_label_content = self._label_alt_content if self._show_alt_label else self._label_content

        volume_info = self._get_volume_info()
        volume_level = volume_info['percent']
        volume_icon = volume_info['icon']

        label_options = [
            ("{volume_icon}", volume_icon),
            ("{volume_level}", volume_level),
        ]

        # Format the label content
        updated_content = self._label_alt_content if self._show_alt_label else self._label_content
        for label_option in label_options:
            updated_content = updated_content.replace(
                label_option[0], str(label_option[1])
            )

        active_label.setText(updated_content)

    def _get_volume_info(self):
        if volume.GetMute() == 1:
            volume_percent = ''
            volume_icon = self._volume_icons[0]  # Default to first icon for muted state
        else:
            volume_level = volume.GetMasterVolumeLevelScalar()
            volume_percent = round(volume_level * 100, 2)

            if volume_percent == 0:
                volume_icon = self._volume_icons[1]  # Icon for 0-25% volume
            elif volume_percent <= 25.0:
                volume_icon = self._volume_icons[2]  # Icon for 0-25% volume
            elif volume_percent <= 50.0:
                volume_icon = self._volume_icons[3]  # Icon for 26-50% volume
            elif volume_percent <= 75.0:
                volume_icon = self._volume_icons[4]  # Icon for 51-75% volume
            else:
                volume_icon = self._volume_icons[5]  # Icon for 76-100% volume

        return {
            'percent': volume_percent,
            'icon': volume_icon
        }
