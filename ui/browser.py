import pygame
from datetime import datetime, timedelta
from config import (BROWSER_BG, TOPBAR_BG, TEXT_COLOR, FIELD_BG, 
                   FIELD_BORDER, BUTTON_BG, BUTTON_TEXT, BYPASS_ALERT_BG,
                    FAILED_ALERT_BG, connected_devices, network_info)
from minigames import camera as camera_minigame
cap = camera_minigame.cap
from handlers import dialog_handler
from minigames.wifi import wifi_networks


def draw_browser(state):
    """Draw the browser pane (right side)"""
    # Background
    pygame.draw.rect(state.screen, BROWSER_BG, state.browser_rect)

    page = state.current_page

    # Display page based on page id
    if page["id"] == "camera_login":
        draw_topbar(state, page["url"])
        draw_camera_header(state)
        draw_camera_logo(state)
        draw_login_box(state)
        draw_camera_fields(state)
        draw_camera_version(state)
        # Bypass alert
        if page["bypassed"] or page["login_failed"]:
            draw_alert(state, page["bypassed"])
        # Cursor in focused field
        draw_field_cursor(state)
    elif page["id"] == "camera_video":
        draw_video_feed(state)
        draw_topbar(state, page["url"])
        draw_next_page_button(state)
    elif page["id"] == "route_simple_admin":
        draw_topbar(state, page["url"])
        draw_admin_panel(state)
    elif page["id"] == "route_simple_login":
        draw_topbar(state, page["url"])
        draw_header(state)
        draw_logo(state)
        draw_login_box(state)
        draw_fields(state)
        draw_version(state)
        # Bypass alert
        if page["bypassed"] or page["login_failed"]:
            draw_alert(state, page["bypassed"])
        # Cursor in focused field
        draw_field_cursor(state)
    elif page["id"] == "empty":
        draw_topbar(state, page["url"])
    elif page["id"] == "wifi_networks":
        draw_topbar(state, page["url"])
        draw_wifi_networks(state)
    elif page["id"] == "smart_fridge":
        draw_topbar(state, page["url"])
        draw_smart_fridge(state)
    else:
        # Unknown page: show blank or error
        draw_topbar(state, page["url"])

def draw_next_page_button(state):
    """Draw a button over the video to go to the next page (router login)."""
    browser_rect = state.browser_rect
    # Button size and position (centered horizontally, near bottom)
    btn_width = 220
    btn_height = 48
    btn_x = browser_rect.x + (browser_rect.width - btn_width) // 2
    # Place above bottom, but below video
    topbar_height = max(40, int(state.HEIGHT * 0.04)) + 16
    btn_y = browser_rect.y + topbar_height + browser_rect.height - topbar_height - btn_height - 32
    btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
    # Draw button
    pygame.draw.rect(state.screen, BUTTON_BG, btn_rect, border_radius=8)
    pygame.draw.rect(state.screen, (160, 160, 160), btn_rect, 2, border_radius=8)
    btn_text = state.ui_font.render("Go to Router Admin Page", True, BUTTON_TEXT)
    tx = btn_rect.x + (btn_rect.width - btn_text.get_width()) // 2
    ty = btn_rect.y + (btn_rect.height - btn_text.get_height()) // 2
    state.screen.blit(btn_text, (tx, ty))

def draw_video_feed(state):
    ret, frame = cap.read()
    if not ret:
        return

    # Convert frame to RGB and resize to area below top bar
    frame = camera_minigame.cv2.cvtColor(frame, camera_minigame.cv2.COLOR_BGR2RGB)
    browser_rect = state.browser_rect
    # Calculate top bar height (same as in draw_topbar)
    topbar_height = max(40, int(state.HEIGHT * 0.04)) + 16  # 8px padding top and bottom
    video_x = browser_rect.x
    video_y = browser_rect.y + topbar_height
    video_width = browser_rect.width
    video_height = browser_rect.height - topbar_height
    frame = camera_minigame.cv2.resize(frame, (video_width, video_height))
    frame_surface = pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], 'RGB')
    state.screen.blit(frame_surface, (video_x, video_y))

def draw_camera_header(state):
    """Draw camera login page title and divider"""
    title = state.title_font.render("Camera Web Login", True, TEXT_COLOR)
    state.screen.blit(title, (state.browser_rect.x + 40, state.browser_rect.y + 80))
    header_div_y = state.browser_rect.y + 120
    pygame.draw.line(state.screen, (180, 180, 180),
                     (state.browser_rect.x + 30, header_div_y),
                     (state.browser_rect.right - 30, header_div_y), 1)


def draw_camera_fields(state):
    """Draw username, password fields and login button for camera login"""
    label_padding = 3
    user_label_y = state.username_rect.y - (state.ui_font.get_height() + label_padding)
    pass_label_y = state.password_rect.y - (state.ui_font.get_height() + label_padding)
    user_label = state.ui_font.render("Camera User", True, TEXT_COLOR)
    pass_label = state.ui_font.render("Camera Password", True, TEXT_COLOR)
    state.screen.blit(user_label, (state.username_rect.x, user_label_y))
    state.screen.blit(pass_label, (state.password_rect.x, pass_label_y))
    # Username field
    pygame.draw.rect(state.screen, FIELD_BG, state.username_rect)
    pygame.draw.rect(state.screen, FIELD_BORDER, state.username_rect, 1)
    page = state.current_page
    username_display = page["username"] if page["username"] else "user"
    username_color = TEXT_COLOR if page["username"] else (140, 140, 140)
    uname_render = state.ui_font.render(username_display, True, username_color)
    state.screen.blit(uname_render, (state.username_rect.x + 8,
                                     state.username_rect.y + (state.username_rect.height - uname_render.get_height()) // 2))
    # Password field
    pygame.draw.rect(state.screen, FIELD_BG, state.password_rect)
    pygame.draw.rect(state.screen, FIELD_BORDER, state.password_rect, 1)
    if page["password"]:
        pwd_display = "*" * len(page["password"])
        pwd_render = state.ui_font.render(pwd_display, True, TEXT_COLOR)
    else:
        pwd_render = state.ui_font.render("password", True, (140, 140, 140))
    state.screen.blit(pwd_render, (state.password_rect.x + 8,
                                   state.password_rect.y + (state.password_rect.height - pwd_render.get_height()) // 2))
    # Login button
    pygame.draw.rect(state.screen, BUTTON_BG, state.login_button_rect, border_radius=6)
    pygame.draw.rect(state.screen, (160, 160, 160), state.login_button_rect, 1, border_radius=6)
    login_text = state.ui_font.render("Camera Login", True, BUTTON_TEXT)
    tx = state.login_button_rect.x + (state.login_button_rect.width - login_text.get_width()) // 2
    ty = state.login_button_rect.y + (state.login_button_rect.height - login_text.get_height()) // 2
    state.screen.blit(login_text, (tx, ty))

    # Camera-specific status messages:
    # - show a red "Invalid login" while brute-forcing is active
    # - show a green "Login in" when the page has been bypassed
    try:
        if page.get("is_being_brute_forced"):
            status_txt = state.ui_font.render("Invalid login", True, (239, 83, 80))
            sx = state.login_box_x + (state.login_box_w - status_txt.get_width()) // 2
            sy = state.login_box_y - 42
            state.screen.blit(status_txt, (sx, sy))
        elif page.get("bypassed"):
            status_txt = state.ui_font.render("Login in", True, (67, 160, 71))
            sx = state.login_box_x + (state.login_box_w - status_txt.get_width()) // 2
            sy = state.login_box_y - 42
            state.screen.blit(status_txt, (sx, sy))
    except Exception:
        # Be defensive in drawing code — don't crash the whole UI if something odd happens
        pass

def draw_camera_version(state):
    """Draw version label below camera login box"""
    version_label = state.ui_font.render("Camera Web Interface v2.3.4", True, TEXT_COLOR)
    version_y = state.login_box_y + state.login_box_h + 30
    version_x = state.login_box_x + (state.login_box_w - version_label.get_width()) // 2
    state.screen.blit(version_label, (version_x, version_y))
    """Draw camera login page title and divider"""
    title = state.title_font.render("Camera Web Login", True, TEXT_COLOR)
    state.screen.blit(title, (state.browser_rect.x + 40, state.browser_rect.y + 80))
    header_div_y = state.browser_rect.y + 120
    pygame.draw.line(state.screen, (180, 180, 180),
                     (state.browser_rect.x + 30, header_div_y),
                     (state.browser_rect.right - 30, header_div_y), 1)

def draw_camera_logo(state):
    """Draw camera logo above login box"""
    # You can replace this with a specific camera logo if you have one
    logo = pygame.image.load(state.current_page["logo_path"]).convert_alpha()
    if logo:
        logo_max_width = state.login_box_w * 0.4
        scale_factor = logo_max_width / logo.get_width()
        logo_scaled = pygame.transform.smoothscale(
            logo,
            (int(logo.get_width() * scale_factor),
             int(logo.get_height() * scale_factor))
        )
        logo_rect = logo_scaled.get_rect()
        logo_rect.centerx = state.login_box_x + state.login_box_w // 2
        logo_rect.bottom = state.login_box_y - 20
        state.screen.blit(logo_scaled, logo_rect)

def draw_camera_version(state):
    """Draw version label below camera login box"""
    version_label = state.ui_font.render("Camera Web Interface v2.3.4", True, TEXT_COLOR)
    version_y = state.login_box_y + state.login_box_h + 30
    version_x = state.login_box_x + (state.login_box_w - version_label.get_width()) // 2
    state.screen.blit(version_label, (version_x, version_y))

def draw_topbar(state, url):
    """Draw browser address bar"""
    topbar_rect = pygame.Rect(state.browser_rect.x + 6, state.browser_rect.y + 8, 
                              state.browser_rect.width - 12, max(40, int(state.HEIGHT * 0.04)))
    pygame.draw.rect(state.screen, TOPBAR_BG, topbar_rect, border_radius=6)
    
    # Window buttons
    pygame.draw.circle(state.screen, (255, 95, 86), (topbar_rect.x + 18, topbar_rect.y + topbar_rect.height // 2), 8)
    pygame.draw.circle(state.screen, (255, 189, 46), (topbar_rect.x + 42, topbar_rect.y + topbar_rect.height // 2), 8)
    pygame.draw.circle(state.screen, (39, 201, 63), (topbar_rect.x + 66, topbar_rect.y + topbar_rect.height // 2), 8)
    
    # Address
    url_render = state.ui_font.render(url, True, TEXT_COLOR)
    state.screen.blit(url_render, (topbar_rect.x + 92, topbar_rect.y + (topbar_rect.height - url_render.get_height()) // 2))

def draw_header(state):
    """Draw page title and divider"""
    title = state.title_font.render("RouteSimple Router Administration", True, TEXT_COLOR)
    state.screen.blit(title, (state.browser_rect.x + 40, state.browser_rect.y + 80))
    
    header_div_y = state.browser_rect.y + 120
    pygame.draw.line(state.screen, (220, 220, 220), 
                     (state.browser_rect.x + 30, header_div_y), 
                     (state.browser_rect.right - 30, header_div_y), 1)

def draw_logo(state):
    """Draw company logo above login box"""
    logo = pygame.image.load(state.current_page["logo_path"]).convert_alpha()
    if logo:
        logo_max_width = state.login_box_w * 0.5
        scale_factor = logo_max_width / logo.get_width()
        logo_scaled = pygame.transform.smoothscale(
            logo,
            (int(logo.get_width() * scale_factor), 
             int(logo.get_height() * scale_factor))
        )
        logo_rect = logo_scaled.get_rect()
        logo_rect.centerx = state.login_box_x + state.login_box_w // 2
        logo_rect.bottom = state.login_box_y - 20
        state.screen.blit(logo_scaled, logo_rect)

def draw_login_box(state):
    """Draw login box background"""
    login_box = pygame.Rect(state.login_box_x, state.login_box_y, 
                           state.login_box_w, state.login_box_h)
    pygame.draw.rect(state.screen, FIELD_BG, login_box, border_radius=8)
    pygame.draw.rect(state.screen, (200, 200, 200), login_box, 1, border_radius=8)

def draw_fields(state):
    """Draw username, password fields and login button"""
    # Labels
    label_padding = 3
    user_label_y = state.username_rect.y - (state.ui_font.get_height() + label_padding)
    pass_label_y = state.password_rect.y - (state.ui_font.get_height() + label_padding)
    
    user_label = state.ui_font.render("Username", True, TEXT_COLOR)
    pass_label = state.ui_font.render("Password", True, TEXT_COLOR)
    state.screen.blit(user_label, (state.username_rect.x, user_label_y))
    state.screen.blit(pass_label, (state.password_rect.x, pass_label_y))
    
    # Username field
    pygame.draw.rect(state.screen, FIELD_BG, state.username_rect)
    pygame.draw.rect(state.screen, FIELD_BORDER, state.username_rect, 1)
    page = state.current_page
    username_display = page["username"] if page["username"] else "enter username"
    username_color = TEXT_COLOR if page["username"] else (140, 140, 140)
    uname_render = state.ui_font.render(username_display, True, username_color)
    state.screen.blit(uname_render, (state.username_rect.x + 8, 
                                     state.username_rect.y + (state.username_rect.height - uname_render.get_height()) // 2))
    # Password field
    pygame.draw.rect(state.screen, FIELD_BG, state.password_rect)
    pygame.draw.rect(state.screen, FIELD_BORDER, state.password_rect, 1)
    if page["password"]:
        pwd_display = "*" * len(page["password"])
        pwd_render = state.ui_font.render(pwd_display, True, TEXT_COLOR)
    else:
        pwd_render = state.ui_font.render("enter password", True, (140, 140, 140))
    state.screen.blit(pwd_render, (state.password_rect.x + 8, 
                                   state.password_rect.y + (state.password_rect.height - pwd_render.get_height()) // 2))
    
    # Login button
    pygame.draw.rect(state.screen, BUTTON_BG, state.login_button_rect, border_radius=6)
    pygame.draw.rect(state.screen, (160, 160, 160), state.login_button_rect, 1, border_radius=6)
    login_text = state.ui_font.render("Login", True, BUTTON_TEXT)
    tx = state.login_button_rect.x + (state.login_button_rect.width - login_text.get_width()) // 2
    ty = state.login_button_rect.y + (state.login_button_rect.height - login_text.get_height()) // 2
    state.screen.blit(login_text, (tx, ty))

def draw_version(state):
    """Draw version label below login box"""
    version_label = state.ui_font.render("RouteSimple version 1.0.1u", True, TEXT_COLOR)
    version_y = state.login_box_y + state.login_box_h + 30
    version_x = state.login_box_x + (state.login_box_w - version_label.get_width()) // 2
    state.screen.blit(version_label, (version_x, version_y))

def draw_alert(state, bypassed):
    """Draw bypass success alert"""
    bg_color = FAILED_ALERT_BG
    alert_min_w = 170
    alert_string = "INVALID LOGIN"
    if bypassed:
        bg_color = BYPASS_ALERT_BG
        alert_min_w = 150
        alert_string = "VALID LOGIN"
 
    alert_w = min(alert_min_w, state.login_box_w - 20)
    alert_rect = pygame.Rect(state.login_box_x + state.login_box_w - alert_w - 10, 
                            state.login_box_y - 34, alert_w, 28)
    pygame.draw.rect(state.screen, bg_color, alert_rect, border_radius=6)
    alert_txt = state.ui_font.render(alert_string, True, (255, 255, 255))
    state.screen.blit(alert_txt, (alert_rect.x, 
                                  alert_rect.y + (alert_rect.height - alert_txt.get_height()) // 2))

def draw_field_cursor(state):
    """Draw blinking cursor in focused field"""
    page = state.current_page
    if state.browser_focus is not None and state.browser_cursor_visible:
        if state.browser_focus == "username":
            caret_x = state.username_rect.x + 8 + state.ui_font.size(page["username"])[0]
            caret_y1 = state.username_rect.y + 6
            caret_y2 = state.username_rect.y + state.username_rect.height - 6
            pygame.draw.line(state.screen, TEXT_COLOR, (caret_x, caret_y1), (caret_x, caret_y2), 2)
        elif state.browser_focus == "password":
            caret_x = state.password_rect.x + 8 + state.ui_font.size("*" * len(page["password"]))[0]
            caret_y1 = state.password_rect.y + 6
            caret_y2 = state.password_rect.y + state.password_rect.height - 6
            pygame.draw.line(state.screen, TEXT_COLOR, (caret_x, caret_y1), (caret_x, caret_y2), 2)


def draw_admin_panel(state):
    """Draw admin panel after successful bypass"""
    padding = 40
    start_y = state.browser_rect.y + 140
    
    # Welcome header
    welcome_text = state.title_font.render("Welcome back, John", True, (67, 160, 71))
    state.screen.blit(welcome_text, (state.browser_rect.x + padding, start_y))
    
    # Divider
    header_div_y = start_y + 40
    pygame.draw.line(state.screen, (220, 220, 220), 
                     (state.browser_rect.x + padding, header_div_y), 
                     (state.browser_rect.right - padding, header_div_y), 2)
    
    y = header_div_y + 30
    
    # Network Information Section
    section_font_bold = pygame.font.Font(pygame.font.match_font('dejavusans', bold=True), state.ui_font.get_height())
    section_title = section_font_bold.render("Network Information", True, TEXT_COLOR)
    state.screen.blit(section_title, (state.browser_rect.x + padding, y))
    y += 35
    
    
    for label, value in network_info:
        label_render = state.ui_font.render(label, True, (100, 100, 100))
        value_render = state.ui_font.render(value, True, TEXT_COLOR)
        state.screen.blit(label_render, (state.browser_rect.x + padding + 10, y))
        state.screen.blit(value_render, (state.browser_rect.x + padding + 110, y))
        y += 25
    
    y += 15
    
    # Connected Devices Section
    section_title = section_font_bold.render("Connected Devices (4)", True, TEXT_COLOR)
    state.screen.blit(section_title, (state.browser_rect.x + padding, y))
    y += 35
    
    # Device list header
    header_bg = pygame.Rect(state.browser_rect.x + padding, y, state.browser_rect.width - padding * 2, 30)
    pygame.draw.rect(state.screen, (240, 240, 240), header_bg)
    
    device_header = state.ui_font.render("Device Name", True, (80, 80, 80))
    ip_header = state.ui_font.render("IP Address", True, (80, 80, 80))
    mac_header = state.ui_font.render("MAC Address", True, (80, 80, 80))
    
    state.screen.blit(device_header, (state.browser_rect.x + padding + 10, y + 7))
    state.screen.blit(ip_header, (state.browser_rect.x + padding + 250, y + 7))
    state.screen.blit(mac_header, (state.browser_rect.x + padding + 430, y + 7))
    y += 35
    

    
    # Prepare clickable device links storage (cleared each draw)
    state.device_links = []

    # Link color like an URL
    LINK_COLOR = (0, 102, 204)

    # Compute row height with some breathing room so rows aren't cramped
    font_h = state.ui_font.get_height()
    row_height = max(36, font_h + 14)

    for i, (device, ip, mac) in enumerate(connected_devices):
        # Alternating row colors
        if i % 2 == 0:
            row_bg = pygame.Rect(state.browser_rect.x + padding, y, state.browser_rect.width - padding * 2, row_height)
            pygame.draw.rect(state.screen, (248, 248, 248), row_bg)

        # Render device name as a blue link-like text
        device_render = state.ui_font.render(device, True, LINK_COLOR)
        ip_render = state.ui_font.render(ip, True, TEXT_COLOR)
        mac_render = state.ui_font.render(mac, True, (120, 120, 120))

        # Center text vertically in the row
        txt_w = device_render.get_width()
        txt_h = device_render.get_height()
        dev_x = state.browser_rect.x + padding + 10
        dev_y = y + (row_height - txt_h) // 2
        state.screen.blit(device_render, (dev_x, dev_y))

        # Underline to indicate a link (inside the row so it's not overdrawn)
        underline_y = dev_y + txt_h + 2
        pygame.draw.line(state.screen, LINK_COLOR, (dev_x, underline_y), (dev_x + txt_w, underline_y), 2)

        # Record clickable rect for the device name (include a few pixels below text so underline is clickable)
        dev_rect = pygame.Rect(dev_x, dev_y, txt_w, txt_h + 6)
        state.device_links.append({"name": device, "ip": ip, "mac": mac, "rect": dev_rect})

        # IP and MAC, also vertically centered
        state.screen.blit(ip_render, (state.browser_rect.x + padding + 250, y + (row_height - ip_render.get_height()) // 2))
        state.screen.blit(mac_render, (state.browser_rect.x + padding + 430, y + (row_height - mac_render.get_height()) // 2))
        y += row_height + 6
    
    y += 20
    
    # System info at bottom
    system_info = state.ui_font.render("Firmware: v1.0.1u | Uptime: 42 days, 3 hours", True, (150, 150, 150))
    state.screen.blit(system_info, (state.browser_rect.x + padding, y))

def draw_wifi_networks(state):
    """Draw Wifi networks page."""
    padding = 40
    y = state.browser_rect.y + 140
    
    # Page title
    title_text = state.title_font.render("Nearby Wifi Networks", True, TEXT_COLOR)
    state.screen.blit(title_text, (state.browser_rect.x + padding, y))
    y += 50
    
    for ssid, security, signal in wifi_networks:
        # Parse numeric signal (expects strings like '-40 dBm')

        # Determine number of bars (0..4) from signal strength
        # Strong: >= -50 -> 4, -65..-51 -> 3, -75..-66 ->2, -85..-76->1, else 0
        if signal >= -50:
            bars = 4
        elif signal >= -65:
            bars = 3
        elif signal >= -75:
            bars = 2
        elif signal >= -85:
            bars = 1
        else:
            bars = 0

        ssid_render = state.ui_font.render(ssid, True, TEXT_COLOR)
        security_render = state.ui_font.render(security, True, (100, 100, 100))

        # Draw signal icon (4 vertical bars) to the left of the SSID
        icon_x = state.browser_rect.x + padding - 36
        icon_base_y = y + ssid_render.get_height()
        bar_width = 6
        gap = 4
        for i in range(4):
            # height increases with bar index
            h = (i + 1) * 6
            bx = icon_x + i * (bar_width + gap)
            by = icon_base_y - h
            color = (180, 180, 180)  # default grey for empty
            if i < bars:
                # color by strength
                if bars >= 3:
                    color = (67, 160, 71)  # green
                elif bars == 2:
                    color = (255, 193, 7)  # amber
                else:
                    color = (239, 83, 80)  # red
            pygame.draw.rect(state.screen, color, (bx + 10, by, bar_width, h))

        state.screen.blit(ssid_render, (state.browser_rect.x + padding + 30, y))
        state.screen.blit(security_render, (state.browser_rect.x + padding + 300, y))
        
        y += ssid_render.get_height() + 20

def draw_smart_fridge(state):
    """Draw the smart fridge page with Giggle branding and food inventory."""
    padding = 40
    y = state.browser_rect.y + 80
    
    # Header with Giggle logo
    try:
        giggle_logo = pygame.image.load("./assets/giggle-logo.png").convert_alpha()
        logo_height = 60
        scale = logo_height / giggle_logo.get_height()
        giggle_logo = pygame.transform.smoothscale(
            giggle_logo,
            (int(giggle_logo.get_width() * scale), logo_height)
        )
        logo_x = state.browser_rect.x + padding
        state.screen.blit(giggle_logo, (logo_x, y))
    except Exception:
        pass  # Skip logo if not found
    
    # Title next to logo
    title = state.title_font.render("Smart Fridge", True, TEXT_COLOR)
    state.screen.blit(title, (state.browser_rect.x + padding + 200, y + 10))
    
    y += 80
    
    # "Logged in with Giggle" status
    login_status = state.ui_font.render("Logged in with Giggle", True, (67, 160, 71))
    state.screen.blit(login_status, (state.browser_rect.x + padding, y))
    
    y += 40
    
    # Divider line
    pygame.draw.line(state.screen, (220, 220, 220),
                     (state.browser_rect.x + padding, y),
                     (state.browser_rect.right - padding, y), 1)
    
    y += 30
    
    # Fridge icon
    try:
        fridge_icon = pygame.image.load("./assets/smart-fridge-icon.png").convert_alpha()
        icon_width = 120
        scale = icon_width / fridge_icon.get_width()
        fridge_icon = pygame.transform.smoothscale(
            fridge_icon,
            (int(fridge_icon.get_width() * scale), int(fridge_icon.get_height() * scale))
        )
        icon_x = state.browser_rect.x + padding
        state.screen.blit(fridge_icon, (icon_x, y))
    except Exception:
        pass  # Skip icon if not found
    
    # Food inventory section (to the right of the fridge icon)
    inventory_x = state.browser_rect.x + padding + 180
    inventory_y = y
    
    section_title = state.title_font.render("Food Inventory", True, TEXT_COLOR)
    state.screen.blit(section_title, (inventory_x, inventory_y))
    
    inventory_y += 50
    
    # Define food items with quantities and expiration info (dynamic dates)
    today = datetime.now()
    
    def format_expiry(days_offset):
        """Format expiration date with offset from today"""
        if days_offset is None:
            return "No expiry"
        expiry_date = today + timedelta(days=days_offset)
        return f"Expires: {expiry_date.strftime('%b %d')}"
    
    food_items = [
        ("Milk", "2 bottles", format_expiry(2)),           # Expires in 2 days
        ("Cheese", "1 block", format_expiry(10)),          # Expires in 10 days
        ("Apples", "6 pieces", "Fresh"),
        ("Carrots", "1 bag", "Fresh"),
        ("Chicken", "500g", format_expiry(1)),             # Expires in 1 day
        ("Leftover Pizza", "3 slices", format_expiry(0)),  # Expires today
        ("Orange Juice", "1 carton", format_expiry(3)),    # Expires in 3 days
        ("Chocolate", "2 bars", format_expiry(None)),      # No expiry
        ("Eggs", "12 count", format_expiry(5)),            # Expires in 5 days
        ("Butter", "250g", format_expiry(13)),             # Expires in 13 days
    ]
    
    # Create a neat table-like display with colored bullets
    for item_name, quantity, expiry in food_items:
        # Draw a colored bullet point/circle
        bullet_color = (67, 160, 71)  # Green for fresh items
        
        # Determine color based on expiry date proximity
        if "Expires" in expiry:
            try:
                # Extract the date from the expiry string
                expiry_str = expiry.replace("Expires: ", "")
                expiry_date = datetime.strptime(f"{expiry_str} {today.year}", "%b %d %Y")
                days_until_expiry = (expiry_date - today).days
                
                if days_until_expiry <= 1:
                    bullet_color = (239, 83, 80)  # Red for expiring today or tomorrow
                elif days_until_expiry <= 5:
                    bullet_color = (255, 193, 7)  # Amber for expiring within 5 days
                # else: stays green
            except Exception:
                pass  # Keep default green if parsing fails
        
        pygame.draw.circle(state.screen, bullet_color, 
                         (inventory_x - 15, inventory_y + 10), 5)
        
        # Item name (bold-ish by using title font at smaller size or regular font)
        item_render = state.ui_font.render(item_name, True, TEXT_COLOR)
        state.screen.blit(item_render, (inventory_x, inventory_y))
        
        # Quantity
        qty_render = state.ui_font.render(quantity, True, (100, 100, 100))
        state.screen.blit(qty_render, (inventory_x + 200, inventory_y))
        
        # Expiration info with dynamic color
        expiry_color = TEXT_COLOR
        if "Expires" in expiry:
            try:
                # Extract the date from the expiry string
                expiry_str = expiry.replace("Expires: ", "")
                expiry_date = datetime.strptime(f"{expiry_str} {today.year}", "%b %d %Y")
                days_until_expiry = (expiry_date - today).days
                
                if days_until_expiry <= 1:
                    expiry_color = (239, 83, 80)  # Red for expiring today or tomorrow
                elif days_until_expiry <= 5:
                    expiry_color = (255, 152, 0)  # Orange for expiring within 5 days
            except Exception:
                pass  # Keep default color if parsing fails
        
        expiry_render = state.ui_font.render(expiry, True, expiry_color)
        state.screen.blit(expiry_render, (inventory_x + 340, inventory_y))
        
        inventory_y += 30
    
    # Temperature display at the bottom
    inventory_y += 20
    temp_text = state.ui_font.render("Temperature: 4°C | Humidity: 65%", True, (150, 150, 150))
    state.screen.blit(temp_text, (state.browser_rect.x + padding, inventory_y))