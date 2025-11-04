import pygame
import os
from handlers import arduino_handler
from config import TEXT_COLOR, BUTTON_BG, BUTTON_TEXT

class SmartLockMinigame:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.active = False
        self.entered_pin = ""
        self.correct_pin = "3001"
        self.message = ""
        self.message_color = TEXT_COLOR
        self.won = False
        self.victory_dialog_shown = False  # Track if victory dialog has been shown
        
        # Button layout
        self.buttons = []
        self.check_button = None
        self.clear_button = None
        
        # Load wood background
        self.wood_background = None
        try:
            wood_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "wood-bg.jpg")
            self.wood_background = pygame.image.load(wood_path).convert()
            # Scale to screen size
            self.wood_background = pygame.transform.scale(self.wood_background, (width, height))
        except Exception as e:
            print(f"Could not load wood background: {e}")
        
        # Load sound effects
        self.beep_sound = None
        self.unlock_sound = None
        try:
            beep_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "PIN_beep.mp3")
            self.beep_sound = pygame.mixer.Sound(beep_path)
        except Exception as e:
            print(f"Could not load beep sound: {e}")
        
        try:
            unlock_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "door_unlocked.mp3")
            self.unlock_sound = pygame.mixer.Sound(unlock_path)
        except Exception as e:
            print(f"Could not load unlock sound: {e}")
        
        # Load sticky note image
        self.sticky_note = None
        try:
            sticky_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sticky-note.png")
            self.sticky_note = pygame.image.load(sticky_path).convert_alpha()
        except Exception as e:
            print(f"Could not load sticky note: {e}")
        
        # Fonts
        self.title_font = pygame.font.Font(None, 64)
        self.pin_font = pygame.font.Font(None, 80)
        self.button_font = pygame.font.Font(None, 56)
        self.message_font = pygame.font.Font(None, 36)
        
        self._setup_buttons()
    
    def _setup_buttons(self):
        """Setup the number pad buttons"""
        # Button dimensions
        button_size = 100
        spacing = 20
        
        # Calculate center position
        pad_width = button_size * 3 + spacing * 2
        pad_height = button_size * 4 + spacing * 3
        start_x = (self.width - pad_width) // 2
        start_y = (self.height - pad_height) // 2 + 80
        
        # Number buttons (1-9, 0)
        # Using simple text characters instead of emojis for better compatibility
        numbers = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['OK', '0', '<']  # Check, 0, Backspace
        ]
        
        self.buttons = []
        for row_idx, row in enumerate(numbers):
            for col_idx, num in enumerate(row):
                x = start_x + col_idx * (button_size + spacing)
                y = start_y + row_idx * (button_size + spacing)
                rect = pygame.Rect(x, y, button_size, button_size)
                
                button_data = {
                    'rect': rect,
                    'label': num,
                    'value': num
                }
                
                if num == 'OK':
                    self.check_button = button_data
                elif num == '<':
                    self.clear_button = button_data
                else:
                    self.buttons.append(button_data)
    
    def start(self):
        """Start the minigame"""
        self.active = True
        self.entered_pin = ""
        self.message = "Enter the PIN code"
        self.message_color = (255, 255, 255)  # White color
        self.won = False
        self.victory_dialog_shown = False
    
    def stop(self):
        """Stop the minigame"""
        self.active = False
    
    def handle_click(self, pos):
        """Handle mouse clicks on the number pad"""
        if not self.active or self.won:
            return False
        
        # Check number buttons
        for button in self.buttons:
            if button['rect'].collidepoint(pos):
                if len(self.entered_pin) < 4:
                    self.entered_pin += button['value']
                    self.message = "Enter the PIN code"
                    self.message_color = (255, 255, 255)  # White
                    # Play beep sound
                    if self.beep_sound:
                        self.beep_sound.play()
                return True
        
        # Check clear button
        if self.clear_button and self.clear_button['rect'].collidepoint(pos):
            if len(self.entered_pin) > 0:
                self.entered_pin = self.entered_pin[:-1]
                self.message = "Enter the PIN code"
                self.message_color = (255, 255, 255)  # White
                # Play beep sound
                if self.beep_sound:
                    self.beep_sound.play()
            return True
        
        # Check submit button
        if self.check_button and self.check_button['rect'].collidepoint(pos):
            if len(self.entered_pin) == 4:
                if self.entered_pin == self.correct_pin:
                    self.message = "ACCESS GRANTED!"
                    self.message_color = (67, 160, 71)
                    self.won = True
                    # Play unlock sound
                    if self.unlock_sound:
                        self.unlock_sound.play()
                    return True
                else:
                    self.message = "INCORRECT PIN"
                    self.message_color = (239, 83, 80)
                    self.entered_pin = ""
                    # Play beep sound for feedback
                    if self.beep_sound:
                        self.beep_sound.play()
            else:
                self.message = "Please enter 4 digits"
                self.message_color = (255, 160, 0)
            return True
        
        return False
    
    def draw(self):
        """Draw the smart lock interface"""
        if not self.active:
            return
        
        # Draw wood background
        if self.wood_background:
            self.screen.blit(self.wood_background, (0, 0))
        else:
            # Fallback to dark background
            self.screen.fill((40, 30, 25))
        
        # Calculate keypad panel dimensions
        # Panel should contain: logo, PIN display, message, and all buttons
        panel_padding = 40
        button_size = 100
        spacing = 20
        
        # Calculate total button area
        button_area_width = button_size * 3 + spacing * 2
        button_area_height = button_size * 4 + spacing * 3
        
        # Panel dimensions (larger than button area to include logo and display)
        panel_width = button_area_width + panel_padding * 2
        panel_height = button_area_height + 450  # Extra space for logo, display, message
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        
        # Draw the keypad panel (device casing)
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # Outer metallic frame
        pygame.draw.rect(self.screen, (80, 80, 85), panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, (60, 60, 65), panel_rect.inflate(-10, -10), border_radius=18)
        
        # Inner dark panel
        inner_panel = panel_rect.inflate(-20, -20)
        pygame.draw.rect(self.screen, (35, 35, 40), inner_panel, border_radius=15)
        
        # Logo area at the top of the panel
        logo_y = panel_y + 60
        logo_bg = pygame.Rect(self.width // 2 - 120, logo_y - 30, 240, 60)
        pygame.draw.rect(self.screen, (50, 50, 55), logo_bg, border_radius=10)
        pygame.draw.rect(self.screen, (120, 120, 125), logo_bg, 2, border_radius=10)
        
        yale_text = self.title_font.render("SS", True, (220, 220, 220))
        yale_rect = yale_text.get_rect(center=(self.width // 2, logo_y))
        self.screen.blit(yale_text, yale_rect)
        
        # Draw PIN display (screen)
        pin_y = logo_y + 80
        pin_display_rect = pygame.Rect(self.width // 2 - 140, pin_y, 280, 80)
        pygame.draw.rect(self.screen, (20, 25, 30), pin_display_rect, border_radius=10)
        pygame.draw.rect(self.screen, (60, 90, 130), pin_display_rect, 3, border_radius=10)
        
        # Display PIN as dots or numbers
        pin_display = "•" * len(self.entered_pin) + "_" * (4 - len(self.entered_pin))
        pin_text = self.pin_font.render(pin_display, True, (200, 220, 255))
        pin_rect = pin_text.get_rect(center=pin_display_rect.center)
        self.screen.blit(pin_text, pin_rect)
        
        # Draw message
        msg_y = pin_y + 110
        msg_text = self.message_font.render(self.message, True, self.message_color)
        msg_rect = msg_text.get_rect(center=(self.width // 2, msg_y))
        self.screen.blit(msg_text, msg_rect)
        
        # Draw number buttons
        mouse_pos = pygame.mouse.get_pos()
        
        for button in self.buttons:
            rect = button['rect']
            is_hovering = rect.collidepoint(mouse_pos)
            
            # Button background - darker, more realistic
            if is_hovering:
                pygame.draw.rect(self.screen, (60, 90, 130), rect, border_radius=12)
            else:
                pygame.draw.rect(self.screen, (30, 30, 35), rect, border_radius=12)
            
            # Button border - metallic look
            pygame.draw.rect(self.screen, (180, 180, 190), rect, 2, border_radius=12)
            
            # Button label - bright white for contrast
            label_text = self.button_font.render(button['label'], True, (220, 230, 255))
            label_rect = label_text.get_rect(center=rect.center)
            self.screen.blit(label_text, label_rect)
        
        # Draw clear button (backspace)
        if self.clear_button:
            rect = self.clear_button['rect']
            is_hovering = rect.collidepoint(mouse_pos)
            
            if is_hovering:
                pygame.draw.rect(self.screen, (150, 60, 60), rect, border_radius=12)
            else:
                pygame.draw.rect(self.screen, (90, 30, 30), rect, border_radius=12)
            
            pygame.draw.rect(self.screen, (180, 180, 190), rect, 2, border_radius=12)
            
            label_text = self.button_font.render(self.clear_button['label'], True, (255, 200, 200))
            label_rect = label_text.get_rect(center=rect.center)
            self.screen.blit(label_text, label_rect)
        
        # Draw check button
        if self.check_button:
            rect = self.check_button['rect']
            is_hovering = rect.collidepoint(mouse_pos)
            
            if is_hovering:
                pygame.draw.rect(self.screen, (60, 140, 90), rect, border_radius=12)
            else:
                pygame.draw.rect(self.screen, (30, 90, 60), rect, border_radius=12)
            
            pygame.draw.rect(self.screen, (180, 180, 190), rect, 2, border_radius=12)
            
            # Use smaller font for "OK" text
            ok_font = pygame.font.Font(None, 48)
            label_text = ok_font.render(self.check_button['label'], True, (200, 255, 200))
            label_rect = label_text.get_rect(center=rect.center)
            self.screen.blit(label_text, label_rect)
        
        # If won, show victory message
        if self.won:
            arduino_handler.send_command_to_arduino("G")
            # Position messages within the keypad panel
            victory_y = panel_y + panel_height - 90
            victory_text = self.title_font.render("DOOR UNLOCKED", True, (67, 160, 71))
            victory_rect = victory_text.get_rect(center=(self.width // 2, victory_y))
            self.screen.blit(victory_text, victory_rect)
            
            # Show completion message with smaller font
            completion_font = pygame.font.Font(None, 28)
            completion_text = completion_font.render("Mission Complete! Press ESC to exit.", True, (200, 200, 200))
            completion_rect = completion_text.get_rect(center=(self.width // 2, victory_y + 50))
            self.screen.blit(completion_text, completion_rect)
            
            # Draw sticky note with credits on the right side
            if self.sticky_note:
                # Scale sticky note to a bigger size
                note_height = 320
                scale = note_height / self.sticky_note.get_height()
                note_width = int(self.sticky_note.get_width() * scale)
                scaled_note = pygame.transform.smoothscale(self.sticky_note, (note_width, note_height))
                
                # Position more to the left and up
                note_x = self.width - note_width - 120
                note_y = (self.height - note_height) // 2 - 60
                self.screen.blit(scaled_note, (note_x, note_y))
                
                # Draw credits text on the sticky note
                credits_font = pygame.font.Font(None, 24)
                credits = [
                    "",
                    "",
                    "PROJECT DONE BY:",
                    "Dinis Costa",
                    "Ivan Peña",
                    "Joep van der Meulen",
                    "Kevin Welz",
                    "Luca Palaysi"
                ]
                
                # Starting position for text (centered on sticky note)
                text_start_y = note_y + 40
                for i, line in enumerate(credits):
                    if line:  # Skip empty lines
                        text_surf = credits_font.render(line, True, (40, 40, 40))
                        text_x = note_x + (note_width - text_surf.get_width() - 15) // 2
                        text_y = text_start_y + i * 30
                        self.screen.blit(text_surf, (text_x, text_y))


# Global instance
smart_lock_game = None

def init_smart_lock(screen, width, height):
    """Initialize the smart lock minigame"""
    global smart_lock_game
    smart_lock_game = SmartLockMinigame(screen, width, height)
    return smart_lock_game

def get_smart_lock_game():
    """Get the smart lock game instance"""
    return smart_lock_game
