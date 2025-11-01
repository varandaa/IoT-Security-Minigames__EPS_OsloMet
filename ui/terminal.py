import pygame
import os
from config import BLACK, GREEN, BORDER, USERNAME_LIGHT, PASSWORD_LIGHT

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
    # If packet inspector is active, draw it over the terminal area
    if getattr(state, 'packet_inspector', None) and state.packet_inspector.get('visible'):
        draw_packet_inspector(state)

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


def draw_packet_inspector(state):
    """Draw a simple packet inspector UI inside the terminal pane."""
    inspector = state.packet_inspector
    if not inspector:
        return

    tr = state.terminal_rect
    # Inspector box (slightly inset)
    pad = 12
    box = pygame.Rect(tr.x + pad, tr.y + pad, tr.width - pad * 2, tr.height - pad * 2)
    pygame.draw.rect(state.screen, (18, 18, 18), box, border_radius=6)
    pygame.draw.rect(state.screen, (90, 90, 90), box, 2, border_radius=6)

    # Header
    header_h = 36
    header_rect = pygame.Rect(box.x, box.y, box.width, header_h)
    title = state.ui_font.render("Packet Inspector — wireshark", True, (220, 220, 220))
    state.screen.blit(title, (header_rect.x + 10, header_rect.y + 6))

    # Close button
    close_w = 72
    close_h = 24
    close_rect = pygame.Rect(box.right - close_w - 10, header_rect.y + 6, close_w, close_h)
    pygame.draw.rect(state.screen, (150, 50, 50), close_rect, border_radius=6)
    close_txt = state.ui_font.render("Close [ESC]", True, (255, 255, 255))
    state.screen.blit(close_txt, (close_rect.x + 8, close_rect.y + 3))
    inspector['close_rect'] = close_rect

    # Packet list area
    list_x = box.x + 10
    list_y = header_rect.y + header_h + 8
    line_h = state.ui_font.get_height() + 6

    inspector['packet_rects'] = []
    for i, pkt in enumerate(inspector.get('packets', [])):
        row_y = list_y + i * line_h
        # Background hover if mouse over
        row_rect = pygame.Rect(list_x, row_y, box.width - 20, line_h - 4)
        mouse_pos = pygame.mouse.get_pos()
        if row_rect.collidepoint(mouse_pos):
            pygame.draw.rect(state.screen, (30, 30, 30), row_rect)
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

        # Render packet summary
        summary = f"{pkt['time']}  {pkt['src']} -> {pkt['dst']}  {pkt['proto']}  {pkt['len']}B  {pkt['summary']}"
        txt = state.ui_font.render(summary, True, (200, 200, 200))
        state.screen.blit(txt, (row_rect.x + 6, row_rect.y + 2))

        inspector['packet_rects'].append({'rect': row_rect, 'packet': pkt})

    # Hint at bottom
    hint = state.ui_font.render("Click a packet to inspect payload", True, (160, 160, 160))
    state.screen.blit(hint, (box.x + 12, box.bottom - 28))

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
            "Navigate to the 'RouteSimple' folder: 'cd RouteSimple'",
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
            "You can do so by typing './hydra {wordlist_name}'.",
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
            "John_Home_Wifi looks like the most interesting one, and it probably belongs to this home.",
            "My Wi-Fi cracking tools are in the 'Wifi' folder. My favourite one is 'fern-wifi-cracker'",
            "Run the command './fern-wifi-cracker {network_name}' while in the 'WiFi' folder to crack the WiFi!",
            "After that, we'll be able to connect to the WiFi and try to hack the devices inside."
        ]
    elif page_id == "smart_light_login":
        # On smart light hub login page
        return [
            "This is the smart light hub login page.",
            "We can try to use the same password we found for the camera to bypass this login.",
            "I remember the credentials are :",
            f"Username: {USERNAME_LIGHT} | Password: {PASSWORD_LIGHT}",
        ]
    elif page_id == "smart_light_admin":
        # Smart light admin panel
        return [
            "Fantastic! We've accessed the smart light hub.",
            "From here, we can see the schedule of when the lights turn on and off.",
            "This information can help us understand the residents' routines.",
            "Let's continue exploring other devices on the network by going back to the router admin panel.",
        ]
    elif page_id == "smart_fridge":
        # Smart light admin panel
        return [
            "This page doesn't have anything interesting.",
            "Let's try to see the traffic going through the network using the 'wireshark' command.",
            "Maybe we can find some non-encrypted credentials that we can reuse in another device.",
            "Let's give it a shot.",
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