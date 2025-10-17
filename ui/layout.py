import pygame

def create_fonts(state):
    """Create fonts sized relative to window height for basic scaling."""
    mono_size = max(10, int(state.HEIGHT * 0.014))
    ui_size = max(12, int(state.HEIGHT * 0.016))
    title_size = max(16, int(state.HEIGHT * 0.022))
    state.mono_font = pygame.font.Font(pygame.font.match_font('dejavusansmono'), mono_size)
    state.ui_font = pygame.font.Font(pygame.font.match_font('dejavusans'), ui_size)
    state.title_font = pygame.font.Font(pygame.font.match_font('dejavusans'), title_size)

def update_layout(state):
    """Recalculate all rects and positions based on current WIDTH/HEIGHT."""
    # Pane layout
    state.terminal_rect = pygame.Rect(0, 0, state.WIDTH // 2, state.HEIGHT)
    state.browser_rect = pygame.Rect(state.WIDTH // 2, 0, state.WIDTH - state.WIDTH // 2, state.HEIGHT)
    
    # Login box size
    state.login_box_w = min(int(state.browser_rect.width * 0.6), 600)
    state.login_box_h = min(int(state.HEIGHT * 0.22), 320)
    state.login_box_x = state.browser_rect.x + (state.browser_rect.width - state.login_box_w) // 2
    state.login_box_y = state.browser_rect.y + (state.HEIGHT - state.login_box_h) // 2 - 20
    
    # Field dimensions
    field_w = state.login_box_w - 80
    field_h = max(36, int(state.login_box_h * 0.16))
    
    # Username field
    state.username_rect.x = state.login_box_x + 40
    state.username_rect.y = state.login_box_y + max(48, int(state.login_box_h * 0.22))
    state.username_rect.width = field_w
    state.username_rect.height = field_h
    
    # Password field
    gap = max(18, int(field_h * 0.6))
    state.password_rect.x = state.username_rect.x
    state.password_rect.y = state.username_rect.y + state.username_rect.height + gap
    state.password_rect.width = field_w
    state.password_rect.height = field_h
    
    # Login button
    state.login_button_rect.x = state.username_rect.x
    state.login_button_rect.y = state.password_rect.y + state.password_rect.height + gap
    state.login_button_rect.width = field_w
    state.login_button_rect.height = field_h
    
    # Recreate fonts
    create_fonts(state)