PATH = {
    "devices": [
        "SuperSmartToaster", "InternetOfFood",
        "SmartFridge", "CityLightController", "ThermoSenseX",
        "AutoGarden", "DoorGuardian", "SmartCamPro",
        "TrafficBeacon", "MediPump", "ParkSensor","RouteSimple", "EnergyMeter",
        "BruteForce", "Wifi"
    ],

    "RouteSimple": [
        "exploit-1.0.2", "exploit-2.3.4", "exploit-0.9.8",
        "exploit-1.0.1u", "exploit-3.0.0a"
    ],

    "SuperSmartToaster": [
        "exploit-0.8.1", "exploit-2.2.31", "exploit-1.4.0-beta",
        "exploit-1.4.0-beta1"
    ],

    "InternetOfFood": [
        "exploit-3.1.0", "exploit-2.0.0-rc1", "exploit-1.1.0",
        "exploit-1.1.1b", "exploit-0.7.0"
    ],

    "SmartFridge": [
        "exploit-2.0.0", "exploit-1.2.3", "exploit-0.7.9",
        "exploit-3.0.0-rc1"
    ],

    "CityLightController": [
        "exploit-4.4.0", "exploit-1.0.0", "exploit-0.3.2"
    ],

    "ThermoSenseX": [
        "exploit-0.9.0", "exploit-1.1.7", "exploit-2.2.0"
    ],

    "AutoGarden": [
        "exploit-1.5.3", "exploit-0.4.0-beta", "exploit-2.0.1",
        "exploit-2.0.1a"
    ],

    "DoorGuardian": [
        "exploit-3.0.0", "exploit-0.2.5", "exploit-1.7.4"
    ],

    "SmartCamPro": [
        "exploit-1.6.0", "exploit-2.10.0", "exploit-0.5.8",
        "exploit-0.5.8a", "exploit-0.6.1", "exploit-2.10.0b",
        "exploit-2.11.0"
    ],

    "TrafficBeacon": [
        "exploit-0.2.9", "exploit-1.3.3", "exploit-2.1.0"
    ],

    "MediPump": [
        "exploit-0.0.9", "exploit-1.0.0-rc2", "exploit-0.8.7",
        "exploit-0.8.7a", "exploit-0.9.0"
    ],

    "ParkSensor": [
        "exploit-0.1.0", "exploit-0.1.1alpha", "exploit-0.2.0",
        "exploit-0.2.1-rc1"
    ],

    "EnergyMeter": [
        "exploit-4.0.0", "exploit-3.2.1", "exploit-3.2.1a",
        "exploit-2.9.9-beta"
    ],

    "BruteForce" : [
        "hydra", "medusa", "ncrack", "patator", "crowbar", "combo-list.txt", "common-credentials.txt", "common-user-passwords.txt"
    ],
    
    "Wifi": [
        "aircrack-ng", "reaver", "bully", "fern-wifi-cracker", "wifite"
    ]
}

CORRECT_EXPLOIT="exploit-1.0.1u"

connected_devices = [
    ("iPhone-John", "192.168.1.75", "A4:83:E7:2F:11:8C"),
    ("RealViewCamera-1", "192.168.1.102", "00:1B:44:11:3A:B7"),
    ("CozyHomePod", "192.168.1.114", "B8:27:EB:A3:2D:1F"),
    ("SafeSecureDoorLock", "192.168.1.223", "F0:18:98:6C:4E:2A"),
]

network_info = [
    ("Network Name (SSID):", "                        Jonh-WiFi-5G"),
    ("Security:", "WPA3-PSK"),
    ("Channel:", "Auto (5GHz)"),
    ("IP Address:", "    192.168.1.1"),
    ("Subnet Mask:", "        255.255.255.0"),
    ("DHCP Server:", "         Enabled"),
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

# Define progression order (folders under /devices). Index 0 is the first stage.
STAGE_ORDER = [
    "RouteSimple",  # router
    "BruteForce",   # camera (brute force folder in this project)
    "iPhone",       # example next stage (iPhone-John)
    "Other"         # fallback for remaining devices
]

# Map device name substrings to a stage index for admin-panel clicks
DEVICE_STAGE_MAP = {
    "cam": 1,
    "camera": 1,
    "iphone": 2,
    "phone": 2,
    "route": 0,
    "routesimple": 0,
}