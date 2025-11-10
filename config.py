PATH = {
    "root": [
        "exploit-1.0.2", "exploit-2.3.4", "exploit-0.9.8",
        "exploit-1.0.1u", "exploit-3.0.0a",
        "combo-list.txt", "common-credentials.txt", "common-user-passwords.txt",
    ]
}

CORRECT_EXPLOIT="exploit-1.0.1u"

connected_devices = [
    ("RealViewCamera-1", "192.168.1.102", "00:1B:44:11:3A:B7"),
    ("Giggle-SmartFridge", "192.168.1.150", "E8:4F:25:9A:1C:3D"),
    ("Giggle-HomePod", "192.168.1.114", "B8:27:EB:A3:2D:1F"),
    ("SafeSecureDoorLock", "192.168.1.223", "F0:18:98:6C:4E:2A"),
    ("SmartLightHub", "192.168.1.180", "D4:3D:7E:4F:5A:6B")
]

network_info = [
    ("Network Name (SSID):", "                        Jonh-WiFi-5G"),
    ("Security:", "WPA2-PSK"),
    ("Channel:", "Auto (5GHz)"),
    ("IP Address:", "    192.168.1.1"),
    ("Subnet Mask:", "        255.255.255.0"),
    ("DHCP Server:", "         Enabled"),
]

packets = [
    {"time": "12:01:02", "src": "192.168.1.75", "dst": "192.168.1.150", "proto": "HTTP", "len": 128,
        "summary": "GET /status", "payload": "username=john112&role=admin&status=online"},
    {"time": "12:01:05", "src": "192.168.1.75", "dst": "192.168.1.150", "proto": "HTTP", "len": 256,
        "summary": "POST /login", "payload": "username=john112&password=John2206_"},
    {"time": "12:01:09", "src": "192.168.1.150", "dst": "192.168.1.75", "proto": "HTTP", "len": 200,
        "summary": "200 OK", "payload": "session=abcd1234"},
    {"time": "12:01:15", "src": "192.168.1.102", "dst": "192.168.1.1", "proto": "RTSP", "len": 512,
        "summary": "SETUP", "payload": ""},
]


WIDTH = 1920
HEIGHT = 1080
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BROWSER_BG = (245, 245, 245)      # light page background
TOPBAR_BG = (230, 230, 230)       # address/top bar
FIELD_BG = (255, 255, 255)        # input field background (white)
FIELD_BORDER = (160, 160, 160)    # input field border
TEXT_COLOR = (30, 30, 30)         # main dark text
BUTTON_BG = (200, 200, 200)       # login button background
BUTTON_TEXT = (0, 0, 0)           # login button text
BYPASS_ALERT_BG = (60, 180, 60)          # green alert for bypassed login
FAILED_ALERT_BG = (255, 95, 86)          # green alert for bypassed login
BORDER = (180, 180, 180)          # generic light border
DARK_TERMINAL = (20, 20, 20)      # used for other browser areas

# Define progression order (folders under /root). Index 0 is the first stage.
STAGE_ORDER = [
    "RouteSimple",  # router
    "BruteForce",   # camera (brute force folder in this project)
    "Other"         # fallback for remaining devices
]

# Map device name substrings to a stage index for admin-panel clicks
DEVICE_STAGE_MAP = {
    "cam": 1,
    "camera": 1,
    "light": 2,
    "lamp": 2,
    "route": 0,
    "routesimple": 0,
    "fridge": 3,
    "homepod": 4,
    "lock": 5,
    "door": 5,
}

USERNAME_LIGHT = "john"
PASSWORD_LIGHT = "Winter2001!"

USERNAME_GIGGLE = "john112"
PASSWORD_GIGGLE = "John2206_"