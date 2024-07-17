import ctypes
# Constants for key events
KEYEVENTF_EXTENDEDKEY = 0x1
KEYEVENTF_KEYUP = 0x2

# Virtual Key Codes
VK_WIN   = 0x5B
VK_LMENU = 0xA4 #Left Alt
VK_N     = 0x4E
VK_A     = 0x41
VK_S     = 0x53
VK_W     = 0x57
VK_SPACE = 0x20

def notification_center():
    user32 = ctypes.windll.user32
    # Hold down Win key
    user32.keybd_event(VK_WIN, 0, KEYEVENTF_EXTENDEDKEY, 0)
    # Press N key
    user32.keybd_event(VK_N, 0, KEYEVENTF_EXTENDEDKEY, 0)
    user32.keybd_event(VK_N, 0, KEYEVENTF_KEYUP, 0)
    # Release Win key
    user32.keybd_event(VK_WIN, 0, KEYEVENTF_KEYUP, 0)

def quick_settings():
    user32 = ctypes.windll.user32
    # Hold down Win key
    user32.keybd_event(VK_WIN, 0, KEYEVENTF_EXTENDEDKEY, 0)
    # Press A key
    user32.keybd_event(VK_A, 0, KEYEVENTF_EXTENDEDKEY, 0)
    user32.keybd_event(VK_A, 0, KEYEVENTF_KEYUP, 0)
    # Release Win key
    user32.keybd_event(VK_WIN, 0, KEYEVENTF_KEYUP, 0)

def search():
    user32 = ctypes.windll.user32
    # Hold down Win key
    user32.keybd_event(VK_WIN, 0, KEYEVENTF_EXTENDEDKEY, 0)
    # Press S key
    user32.keybd_event(VK_S, 0, KEYEVENTF_EXTENDEDKEY, 0)
    user32.keybd_event(VK_S, 0, KEYEVENTF_KEYUP, 0)
    # Release Win key
    user32.keybd_event(VK_WIN, 0, KEYEVENTF_KEYUP, 0)
    
def widget():
    user32 = ctypes.windll.user32
    # Hold down Win key
    user32.keybd_event(VK_WIN, 0, KEYEVENTF_EXTENDEDKEY, 0)
    # Press W key
    user32.keybd_event(VK_W, 0, KEYEVENTF_EXTENDEDKEY, 0)
    user32.keybd_event(VK_W, 0, KEYEVENTF_KEYUP, 0)
    # Release Win key
    user32.keybd_event(VK_WIN, 0, KEYEVENTF_KEYUP, 0)

def launcher():
    user32 = ctypes.windll.user32
    # Press down ALT key
    user32.keybd_event(VK_LMENU, 0, KEYEVENTF_EXTENDEDKEY, 0)
    # Press down Space key
    user32.keybd_event(VK_SPACE, 0, KEYEVENTF_EXTENDEDKEY, 0)
    # Release keys
    user32.keybd_event(VK_LMENU, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_SPACE, 0, KEYEVENTF_KEYUP, 0)


function_map = {
    'quick_settings': quick_settings,
    'notification_center': notification_center,
    'search': search,
    'widget': widget,
    'launcher': launcher
}
