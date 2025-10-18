import pygame
from config import WIDTH, HEIGHT
import ctypes

class GameState:
    def __init__(self):
        # Window setup

        # don't use the scale of windows
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Windows 8.1+
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()  # Windows 7
            except Exception:
                pass

        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Hacker Terminal")
        
        # Terminal state
        self.input_text = ""
        self.output_lines = ["Welcome to the Linux terminal.", "Type 'help' for commands."]
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 500
        
        # File system
        self.current_folder = "/devices"
        self.level = 1

        # Browser global state (cursor, focus)
        # These properties are shared across all pages
        self.browser_cursor_visible = True
        self.browser_cursor_timer = 0
        self.browser_cursor_blink_speed = 500
        self.browser_focus = None  # Which field is focused (username, password, etc.)

        # Browser pages state
        # Each page has its own login, bypass, etc.
        self.browser_pages = [
            {
                "id": "empty",
                "url": "http://192.168.1.1/login",
                "bypassed": False,
                "login_failed": False,
                "show_admin_panel": False,
                "bypass_time": 0,
                "username": "",
                "password": "",
                "logo_path": "./assets/routesimple.png"
            },
            # RouteSimple Login
            {
                "id": "route_simple_login",
                "url": "http://192.168.1.1/login",
                "bypassed": False,
                "login_failed": False,
                "show_admin_panel": False,
                "bypass_time": 0,
                "username": "",
                "password": "",
                "logo_path": "./assets/routesimple.png"
            },
            # RouteSimple Admin Panel
            {
                "id": "route_simple_admin",
                "url": "http://192.168.1.1/admin",
                "bypassed": True,  # Admin page is only shown after bypass
                "login_failed": False,
                "show_admin_panel": True,
                "bypass_time": 0,
                "username": "admin",
                "password": ""
            },
            {
                "id": "camera_login",
                "url": "http://192.168.1.102/login",
                "bypassed": False,
                "login_failed": False,
                "show_admin_panel": False,
                "bypass_time": 0,
                "username": "",
                "password": "",
                "logo_path": "./assets/camera.png"
            },
            {
                "id": "camera_video",
                "url": "http://192.168.1.102/video",
                "bypassed": False,
                "login_failed": False,
                "show_admin_panel": False,
                "bypass_time": 0,
                "username": "",
                "password": ""
            }
        ]
    # Start at the router login page so the flow begins with the router
        #self.current_page_index = 0  # Start page index (router login)
        self.go_to_page_by_id("route_simple_login")

        # Clock
        self.clock = pygame.time.Clock()

        # Progression: which stage the player has reached (index into config.STAGE_ORDER)
        # Start at -1 (nothing hacked). When they bypass router, set to 0.
        self.current_stage_index = -1
        
        # Fonts
        self.mono_font = None
        self.ui_font = None
        self.title_font = None
        
        # Layout
        self.terminal_rect = None
        self.browser_rect = None
        self.login_box_w = 420
        self.login_box_h = 220
        self.login_box_x = 0
        self.login_box_y = 0
        self.username_rect = pygame.Rect(0, 0, 340, 36)
        self.password_rect = pygame.Rect(0, 0, 340, 36)
        self.login_button_rect = pygame.Rect(0, 0, 340, 36)
        
        # # Load logo
        # try:
        #     self.logo = pygame.image.load("./assets/routesimple.png").convert_alpha()
        # except pygame.error:
        #     print("Error loading image")
        #     self.logo = None
        
        # Initialize layout
        from ui.layout import update_layout
        update_layout(self)

    # Property to access the current page's data
    @property
    def current_page(self):
        return self.browser_pages[self.current_page_index]

    # Methods to switch pages
    def go_to_page(self, index):
        """Switch to any browser page by index."""
        if 0 <= index < len(self.browser_pages):
            self.current_page_index = index

    def go_to_page_by_id(self, page_id):
        """Switch to a browser page by its ID."""
        for i, page in enumerate(self.browser_pages):
            if page["id"] == page_id:
                self.current_page_index = i
                return
            
    def go_to_page_by_url(self, url):
        """Switch to a browser page by its URL."""
        for i, page in enumerate(self.browser_pages):
            if page["url"] == url:
                self.current_page_index = i
                return

    def add_page(self, id, url):
        """Add a new browser page with default properties."""
        self.browser_pages.append({
            "id": id,
            "url": url,
            "bypassed": False,
            "login_failed": False,
            "show_admin_panel": False,
            "bypass_time": 0,
            "username": "",
            "password": ""
        })
    
    def update_cursors(self, dt):
        """Update cursor blink timers (global and current page)"""
        self.cursor_timer += dt
        self.browser_cursor_timer += dt

        if self.cursor_timer >= self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        if self.browser_cursor_timer >= self.browser_cursor_blink_speed:
            self.browser_cursor_visible = not self.browser_cursor_visible
            self.browser_cursor_timer = 0

    def check_transition(self):
        self.check_admin_panel_transition()

    def check_admin_panel_transition(self):
        # Check if we should show admin panel (2 seconds after bypass) for current page
        if self.current_page["bypassed"] and not self.current_page["show_admin_panel"]:
            if pygame.time.get_ticks() - self.current_page["bypass_time"] > 2000:
                self.current_page["show_admin_panel"] = True
                self.go_to_page_by_id("route_simple_admin")  # Automatically switch to admin page