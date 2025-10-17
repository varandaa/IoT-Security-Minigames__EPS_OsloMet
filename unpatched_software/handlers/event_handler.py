import pygame
from handlers.command_handler import execute_command
from handlers.login_handler import login_attempt
from minigames import camera as camera_minigame

# Use camera_minigame.cap when needing to control/release the camera
cap = camera_minigame.cap

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

    connection_pages = [ 0, 2 ]  # Indexes of pages that can connect to others

    page = state.current_page
    if state.current_page_index in connection_pages:
        if state.username_rect.collidepoint((mx, my)):
            state.browser_focus = "username"
        elif state.password_rect.collidepoint((mx, my)):
            state.browser_focus = "password"
        elif state.login_button_rect.collidepoint((mx, my)):
            login_attempt(state)
    elif state.current_page["url"] == "http://192.168.1.1/admin":
        # Admin page: handle clicks on connected device links
        # state.device_links is populated when drawing the admin panel
        links = getattr(state, "device_links", None)
        if links:
            for item in links:
                if item["rect"].collidepoint((mx, my)):
                    dev_name = item["name"]
                    # If the device appears to be a camera, go to the camera login page
                    if "cam" in dev_name.lower() or "camera" in dev_name.lower():
                        state.go_to_page(0)  # camera login page
                    else:
                        # For other devices, create a new page entry and go there
                        new_url = f"http://{item['ip']}/"
                        state.add_page(new_url)
                        state.go_to_page(len(state.browser_pages) - 1)
                    return
    elif page["url"] == "http://145.40.68.12:8080/video":
        btn_width = 220
        btn_height = 48
        btn_x = state.browser_rect.x + (state.browser_rect.width - btn_width) // 2
        topbar_height = max(40, int(state.HEIGHT * 0.04)) + 16
        btn_y = state.browser_rect.y + state.browser_rect.height - btn_height - 32
        btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        if btn_rect.collidepoint(event.pos):
            # if needed, we could release the camera via cap.release()
            # cap.release()
            state.go_to_page(2)  # go to "http://192.168.1.1/login"
    else:
        if state.browser_rect.collidepoint((mx, my)):
            state.browser_focus = None
        if state.terminal_rect.collidepoint((mx, my)):
            state.browser_focus = None

