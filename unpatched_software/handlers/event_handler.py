import pygame
from handlers.command_handler import execute_command
from handlers.login_handler import login_attempt

def handle_events(state, event):
    """Handle keyboard and mouse events"""
    if event.type == pygame.KEYDOWN:
        handle_keyboard(state, event)
    elif event.type == pygame.MOUSEBUTTONDOWN:
        handle_mouse(state, event)

def handle_keyboard(state, event):
    """Handle keyboard input"""
    page = state.current_page
    if event.key == pygame.K_RETURN:
        if state.browser_focus is not None:
            login_attempt(state)
        else:
            state.output_lines.append(state.current_folder + "> " + state.input_text)
            execute_command(state, state.input_text)
            state.input_text = ""
    elif event.key == pygame.K_BACKSPACE:
        if state.browser_focus == "username":
            page["username"] = page["username"][:-1]
        elif state.browser_focus == "password":
            page["password"] = page["password"][:-1]
        else:
            state.input_text = state.input_text[:-1]
    elif event.key == pygame.K_l and (event.mod & pygame.KMOD_CTRL):
        execute_command(state, "clear")
    else:
        if event.unicode and event.unicode.isprintable():
            if state.browser_focus == "username":
                page["username"] += event.unicode
            elif state.browser_focus == "password":
                page["password"] += event.unicode
            else:
                state.input_text += event.unicode

def handle_mouse(state, event):
    """Handle mouse clicks"""
    mx, my = event.pos
    
    if state.username_rect.collidepoint((mx, my)):
        state.browser_focus = "username"
    elif state.password_rect.collidepoint((mx, my)):
        state.browser_focus = "password"
    elif state.login_button_rect.collidepoint((mx, my)):
        login_attempt(state)
    else:
        if state.browser_rect.collidepoint((mx, my)):
            state.browser_focus = None
        if state.terminal_rect.collidepoint((mx, my)):
            state.browser_focus = None

