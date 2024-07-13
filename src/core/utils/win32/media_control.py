from enum import Enum
from PyQt6.QtGui import QImage
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager
from winsdk.windows.storage.streams import DataReader, Buffer, InputStreamOptions

THUMBNAIL_BUFFER_SIZE = 5 * 1024 * 1024

class WindowsMediaRepeat(Enum):
    Off = 0
    Track = 1
    List = 2

async def get_current_session():
    try:
        sessions = await GlobalSystemMediaTransportControlsSessionManager.request_async()
        return sessions.get_current_session()
    except Exception as e:
        print(f"Error getting current session: {e}")
        return None

def props_to_dict(props):
    return {
        attr: props.__getattribute__(attr) for attr in dir(props) if attr[0] != '_'
    }

async def get_media_info():
    try:
        current_session = await get_current_session()

        if current_session:
            media_props = await current_session.try_get_media_properties_async()
            media_props = props_to_dict(media_props)
            del media_props['genres']
            return media_props
    except Exception as e:
        print(f"Error getting media info: {e}")

    return {
        'title': 'No media',
        'artist': 'Unknown',
        'album_title': '',
        'album_artist': '',
        'album_track_count': 0,
        'playback_type': 0,
        'subtitle': '',
        'thumbnail': None,
        'track_number': 0
    }

async def get_playback_info():
    try:
        current_session = await get_current_session()

        if current_session:
            playback_props = current_session.get_playback_info()
            playback_props = props_to_dict(playback_props)
            playback_props['controls'] = props_to_dict(playback_props['controls'])
            return playback_props
    except Exception as e:
        print(f"Error getting playback info: {e}")

    return {
        'auto_repeat_mode': None,
        'controls': {
            'is_channel_down_enabled': False,
            'is_channel_up_enabled': False,
            'is_fast_forward_enabled': False,
            'is_next_enabled': False,
            'is_pause_enabled': False,
            'is_play_enabled': False,
            'is_play_pause_toggle_enabled': False,
            'is_playback_position_enabled': False,
            'is_playback_rate_enabled': False,
            'is_previous_enabled': False,
            'is_record_enabled': False,
            'is_repeat_enabled': False,
            'is_rewind_enabled': False,
            'is_shuffle_enabled': False,
            'is_stop_enabled': False
        },
        'is_shuffle_active': None,
        'playback_rate': None,
        'playback_status': 0,
        'playback_type': 0
    }

async def stream_to_image(thumbnail_ref) -> QImage:
    buffer = Buffer(THUMBNAIL_BUFFER_SIZE)
    readable_stream = await thumbnail_ref.open_read_async()
    await readable_stream.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)
    buffer_reader = DataReader.from_buffer(buffer)
    thumbnail_buffer = buffer_reader.read_bytes(buffer.length)
    thumbnail_image = QImage()
    thumbnail_image.loadFromData(bytearray(thumbnail_buffer))
    return thumbnail_image
