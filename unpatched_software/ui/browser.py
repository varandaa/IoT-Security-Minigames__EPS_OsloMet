import pygame
from config import (BROWSER_BG, TOPBAR_BG, TEXT_COLOR, FIELD_BG, 
                   FIELD_BORDER, BUTTON_BG, BUTTON_TEXT, BYPASS_ALERT_BG,
                    FAILED_ALERT_BG, connected_devices, network_info)

def draw_browser(state):
    """Draw the browser pane (right side)"""
    # Background
    pygame.draw.rect(state.screen, BROWSER_BG, state.browser_rect)
    
    
    page = state.current_page
    # Display page based on URL
    if page["url"].endswith("/admin"):
        draw_topbar(state, page["url"])
        draw_admin_panel(state)
    elif page["url"].endswith("/login"):
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
    else:
        # Unknown page: show blank or error
        draw_topbar(state, page["url"])

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
    if state.logo:
        logo_max_width = state.login_box_w * 0.5
        scale_factor = logo_max_width / state.logo.get_width()
        logo_scaled = pygame.transform.smoothscale(
            state.logo,
            (int(state.logo.get_width() * scale_factor), 
             int(state.logo.get_height() * scale_factor))
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
    

    
    for i, (device, ip, mac) in enumerate(connected_devices):
        # Alternating row colors
        if i % 2 == 0:
            row_bg = pygame.Rect(state.browser_rect.x + padding, y, state.browser_rect.width - padding * 2, 25)
            pygame.draw.rect(state.screen, (248, 248, 248), row_bg)
        
        device_render = state.ui_font.render(device, True, TEXT_COLOR)
        ip_render = state.ui_font.render(ip, True, TEXT_COLOR)
        mac_render = state.ui_font.render(mac, True, (120, 120, 120))
        
        state.screen.blit(device_render, (state.browser_rect.x + padding + 10, y + 4))
        state.screen.blit(ip_render, (state.browser_rect.x + padding + 250, y + 4))
        state.screen.blit(mac_render, (state.browser_rect.x + padding + 430, y + 4))
        y += 25
    
    y += 20
    
    # System info at bottom
    system_info = state.ui_font.render("Firmware: v1.0.1u | Uptime: 42 days, 3 hours", True, (150, 150, 150))
    state.screen.blit(system_info, (state.browser_rect.x + padding, y))