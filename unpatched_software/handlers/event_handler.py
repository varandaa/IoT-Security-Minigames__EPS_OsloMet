import pygame
from handlers.command_handler import execute_command
from handlers.login_handler import login_attempt
from handlers import dialog_handler
from handlers import command_handler
from minigames import camera as camera_minigame

# Use camera_minigame.cap when needing to control/release the camera
cap = camera_minigame.cap

def handle_events(state, event):
    """Handle keyboard and mouse events"""
    # If a dialog is active, block interactions except dialog keys
    dlg = getattr(state, "dialog", None)
    if dlg and dlg.get("visible"):
        if event.type == pygame.KEYDOWN:
            # Let dialog handler process Enter; other keys ignored
            from handlers import dialog_handler
            dialog_handler.handle_key(state, event)
        # ignore mouse events while dialog active
        return

    if event.type == pygame.KEYDOWN:
        handle_keyboard(state, event)
    elif event.type == pygame.MOUSEBUTTONDOWN:
        handle_mouse(state, event)

def handle_keyboard(state, event):
    """Handle keyboard input"""
    # If a dialog is active, let the dialog handler consume Enter
    dlg = getattr(state, "dialog", None)
    if dlg:
        consumed = dialog_handler.handle_key(state, event)
        if consumed:
            return

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
            from config import DEVICE_STAGE_MAP
            for item in links:
                if item["rect"].collidepoint((mx, my)):
                    dev_name = item["name"]
                    dev_key = dev_name.lower()
                    # Determine required stage for this device (default to next stage)
                    required_stage = 999
                    for k, v in DEVICE_STAGE_MAP.items():
                        if k in dev_key:
                            required_stage = v
                            break

                    # Allow access if device's required_stage is <= current_stage_index + 1
                    # (player can access the next stage after completing the previous one)
                    if required_stage > (state.current_stage_index + 1):
                        # blocked: show dialog explaining the order
                        from handlers import dialog_handler
                        dialog_handler.start_dialog(state, [
                            f"You can't access {dev_name} yet.",
                            "You need to progress in the network in order. Try the required devices first."
                        ], char_delay=20)
                        return

                    # Allowed: perform navigation
                    if "cam" in dev_name.lower() or "camera" in dev_name.lower():
                        state.go_to_page(2)  # camera login page
                        command_handler.change_directory(state, "cd ..")
                    else:
                        # For other devices, create a new page entry and go there
                        new_url = f"http://{item['ip']}/"
                        state.add_page(new_url)
                        state.go_to_page(len(state.browser_pages) - 1)

                    return
    elif page["url"] == "http://192.168.1.102/video":
        btn_width = 220
        btn_height = 48
        btn_x = state.browser_rect.x + (state.browser_rect.width - btn_width) // 2
        topbar_height = max(40, int(state.HEIGHT * 0.04)) + 16
        btn_y = state.browser_rect.y + state.browser_rect.height - btn_height - 32
        btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        if btn_rect.collidepoint(event.pos):
            # if needed, we could release the camera via cap.release()
            # cap.release()
            state.go_to_page(0)  # go to "http://192.168.1.1/login"
    else:
        if state.browser_rect.collidepoint((mx, my)):
            state.browser_focus = None
        if state.terminal_rect.collidepoint((mx, my)):
            state.browser_focus = None

