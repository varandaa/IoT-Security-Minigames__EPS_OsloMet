import pygame
from config import WIDTH, HEIGHT

class GameState:
    def __init__(self):
        # Window setup
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
        
        # Browser state
        self.bypassed = False
        self.login_failed = False
        self.show_admin_panel = False
        self.bypass_time = 0
        self.browser_username = ""
        self.browser_password = ""
        self.browser_focus = None
        self.browser_cursor_visible = True
        self.browser_cursor_timer = 0
        self.browser_cursor_blink_speed = 500
        
        # Clock
        self.clock = pygame.time.Clock()
        
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
        
        # Load logo
        try:
            self.logo = pygame.image.load("./assets/routesimple.png").convert_alpha()
        except pygame.error:
            print("Error loading image")
            self.logo = None
        
        # Initialize layout
        from ui.layout import update_layout
        update_layout(self)
    
    def update_cursors(self, dt):
        """Update cursor blink timers"""
        self.cursor_timer += dt
        self.browser_cursor_timer += dt
        
        if self.cursor_timer >= self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        
        if self.browser_cursor_timer >= self.browser_cursor_blink_speed:
            self.browser_cursor_visible = not self.browser_cursor_visible
            self.browser_cursor_timer = 0
        
        # Check if we should show admin panel (2 seconds after bypass)
        if self.bypassed and not self.show_admin_panel:
            if pygame.time.get_ticks() - self.bypass_time > 2000:
                self.show_admin_panel = True