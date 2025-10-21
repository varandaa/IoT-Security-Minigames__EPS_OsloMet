import pygame
import os
from config import BLACK, GREEN, BORDER

# Load Clippy image
_clippy_image = None
_clippy_rect = None

def _load_clippy():
    """Load and scale the Clippy image"""
    global _clippy_image
    if _clippy_image is None:
        clippy_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "hacker_clippy.png")
        try:
            img = pygame.image.load(clippy_path).convert_alpha()
            # Scale to a small icon size
            target_size = 100
            scale = target_size / img.get_height()
            _clippy_image = pygame.transform.smoothscale(img, (int(img.get_width() * scale), target_size))
        except Exception as e:
            print(f"Failed to load Clippy image: {e}")
            _clippy_image = None

def draw_terminal(state):
    """Draw the terminal pane (left side)"""
    # Background
    pygame.draw.rect(state.screen, BLACK, state.terminal_rect)
    
    # Separator line
    pygame.draw.line(state.screen, BORDER, 
                     (state.terminal_rect.right, 0), 
                     (state.terminal_rect.right, state.HEIGHT), 2)
    
    # Output lines
    y = 10
    line_h = state.mono_font.get_linesize()
    max_lines = max(1, (state.terminal_rect.height - 40) // line_h)
    
    for line in state.output_lines[-max_lines:]:
        rendered = state.mono_font.render(line, True, GREEN)
        state.screen.blit(rendered, (state.terminal_rect.x + 10, y))
        y += line_h
    
    # Input line with cursor
    prompt = state.current_folder + "> " + state.input_text
    if state.cursor_visible:
        prompt += "_"
    rendered_input = state.mono_font.render(prompt, True, GREEN)
    state.screen.blit(rendered_input, (state.terminal_rect.x + 10, y))
    
    # Draw Clippy icon in the top-right corner of the terminal
    global _clippy_image, _clippy_rect
    _load_clippy()
    if _clippy_image:
        clippy_x = state.terminal_rect.right - _clippy_image.get_width() - 10
        clippy_y = clippy_x + 70
        _clippy_rect = pygame.Rect(clippy_x, clippy_y, _clippy_image.get_width(), _clippy_image.get_height())
        
        # Check if mouse is hovering over Clippy
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = _clippy_rect.collidepoint(mouse_pos)
        
        # Draw a subtle background circle/glow when hovering
        if is_hovering:
            glow_surface = pygame.Surface((_clippy_image.get_width() + 10, _clippy_image.get_height() + 10), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (0, 255, 0, 50), 
                             (_clippy_image.get_width() // 2 + 5, _clippy_image.get_height() // 2 + 5), 
                             _clippy_image.get_width() // 2 + 5)
            state.screen.blit(glow_surface, (clippy_x - 5, clippy_y - 5))
            # Change cursor to hand pointer
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            # Reset cursor when not hovering
            if not getattr(state, '_cursor_was_on_clippy', False):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        state._cursor_was_on_clippy = is_hovering
        
        state.screen.blit(_clippy_image, (clippy_x, clippy_y))
        
        # Store the rect in state for click detection
        state.clippy_rect = _clippy_rect

def get_help_dialog_for_page(state):
    """Return context-sensitive help dialog based on current browser page and game state"""
    page_id = state.current_page["id"]
    wifi_connected = state.wifi_connected
    router_bypassed = False
    camera_bypassed = False
    
    # Check if router and camera have been bypassed
    for page in state.browser_pages:
        if page["id"] == "route_simple_login" and page["bypassed"]:
            router_bypassed = True
        if page["id"] == "camera_login" and page["bypassed"]:
            camera_bypassed = True
    
    # Context-sensitive help based on current page and progress
    if page_id == "empty":
        # Starting phase - need to connect to WiFi
        return [
            "Hey! Having a tough time?",
            "Don't worry, it's completely normal.",
            "In order to scan for existing WiFi networks you need to type the 'nmcli' command.",
            "Remember you can always type the 'help' command to see the list of existing commands.",
            "Got it?",
            "Now let's get back to hacking!",
        ]
  #  elif page_id == "route_simple_login" and wifi_connected and not router_bypassed:
        # Connected to WiFi but haven't started router hack
  #      return [
  #          "Great! You've connected to the WiFi.",
  #          "Now you need to hack into the router to access the network.",
  #          "Navigate to the RouteSimple folder: 'cd RouteSimple'",
  # #         "Type 'ls' to see the available exploits.",
   #         "Look for information about the router's software version.",
    #        "Run the matching exploit with './{exploit-name}'",
     #       "The router login should appear in the browser soon!",
      #  ]
    elif page_id == "route_simple_login":
        # On router login page
        return [
            "You're looking at the router's login page!",
            "If you're still inside the 'Wifi' folder type 'cd ..' to go back to the 'devices' folder."
            "By typing 'ls' you can see folders for different devices and tools.",
            "This is a RouteSimple router - check the version in the browser.",
            "Navigate to the RouteSimple folder: 'cd RouteSimple'",
            "Look for the exploit matching the router's version.",
            "Run it with './{exploit-name}' while in the RouteSimple folder.",
            "Once exploited, you'll bypass the login!",
        ]
    elif page_id == "route_simple_admin":
        # Router admin panel or router is bypassed
        return [
            "Excellent! The router is hacked.",
            "You now have access to all devices on the network.",
            "On the admin panel, you can see connected devices.",
            "Click on a device to access it!"
        ]
    elif page_id == "camera_login":
        # On camera login page
        return [
            "You're at the security camera login!",
            "This requires a brute force attack to crack the password.",
            "Navigate to my 'BruteForce' folder and take a look at the available wordlists.",
            "Try using the brute-force tool 'hydra' with the different wordlists until we get the right credentials",
            "You can do so by typing 'hydra {wordlist_name}'.",
            "Be patient - you might have to try different wordlists to guess the credentials.",
        ]
    elif page_id == "camera_video" or camera_bypassed:
        # Camera feed or camera is bypassed
        return [
            "Amazing work! You've accessed the camera.",
            "You can now see the video feed from inside the house.",
            "Continue exploring other devices on the network.",
            "Each device has different vulnerabilities to exploit.",
            "Use the admin panel to select your next target!",
        ]
    elif page_id == "wifi_networks":
        # On WiFi networks page
        return [
            "You're viewing available WiFi networks.",
            "John_Home_Wifi looks like the most interesting one, and it probably gelongs to this home.",
            "My Wi-Fi cracking tools are in the 'Wifi' folder. My favourite one is 'fern-wifi-cracker'",
            "Run the command './fern-wifi-cracker {network_name}' while in the 'WiFi' folder to crack the WiFi!",
            "After that, we'll be able to connect to the WiFi and try to hack the devices inside."
        ]
    else:
        # Generic help for other pages
        return [
            "You're making incredible progress!",
            "Continue exploring the network for more devices.",
            "Each IoT device has unique vulnerabilities.",
            "Use 'ls' and 'cd' to navigate the file system.",
            "Execute exploits to gain access to each device.",
            "Remember: real hackers always think creatively!",
        ]