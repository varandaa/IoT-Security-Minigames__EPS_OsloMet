import pygame
from ui.layout import update_layout
from ui.terminal import draw_terminal
from ui.browser import draw_browser

def handle_resize(state, new_w, new_h):
    """Handle window resize events"""
    state.WIDTH = max(200, new_w)
    state.HEIGHT = max(200, new_h)
    state.screen = pygame.display.set_mode((state.WIDTH, state.HEIGHT), pygame.RESIZABLE)
    update_layout(state)
    draw_terminal(state)
    draw_browser(state)
    pygame.display.flip()