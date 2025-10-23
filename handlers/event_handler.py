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
            # record command in history (ignore empty)
            cmd = state.input_text.strip()
            if cmd:
                state.command_history.append(cmd)
            # reset any history browsing
            state.history_index = None
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
    elif event.key == pygame.K_UP:
        # Navigate up in history (older commands)
        if state.command_history:
            if state.history_index is None:
                state.history_index = len(state.command_history) - 1
            else:
                state.history_index = max(0, state.history_index - 1)
            state.input_text = state.command_history[state.history_index]
    elif event.key == pygame.K_DOWN:
        # Navigate down in history (newer commands)
        if state.command_history and state.history_index is not None:
            state.history_index = min(len(state.command_history) - 1, state.history_index + 1)
            # If we've moved past the last, clear
            if state.history_index >= len(state.command_history):
                state.history_index = None
                state.input_text = ""
            else:
                state.input_text = state.command_history[state.history_index]
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

    # Check if Clippy icon was clicked (in terminal area)
    clippy_rect = getattr(state, "clippy_rect", None)
    if clippy_rect and clippy_rect.collidepoint((mx, my)):
        from ui.terminal import get_help_dialog_for_page
        help_text = get_help_dialog_for_page(state)
        dialog_handler.start_dialog(state, help_text, char_delay=20)
        return

    connection_pages = [ "route_simple_login", "camera_login" ]  # id of pages that can connect to others

    page = state.current_page
    if state.browser_rect.collidepoint((mx, my)):
        if page["id"] in connection_pages:
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
                            dialog_handler.start_dialog(state, [
                                f"You can't access {dev_name} yet.",
                                "Let's stick to the plan, access the devices in the right order."
                            ], char_delay=20)
                            return

                        # Allowed: perform navigation
                        if "cam" in dev_name.lower() or "camera" in dev_name.lower():
                            state.go_to_page_by_id("camera_login")  # camera login page
                        elif "fridge" in dev_name.lower() or "giggle" in dev_name.lower():
                            state.go_to_page_by_id("smart_fridge")  # smart fridge page
                        # command_handler.change_directory(state, "cd ..")
                        else:
                            # For other devices, create a new page entry and go there
                            new_url = f"http://{item['ip']}/"
                            state.add_page(new_url, new_url)
                            state.go_to_page_by_url(new_url)

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
                cap.release()
                state.go_to_page_by_id("route_simple_admin")  # go to "http://192.168.1.1/admin"
                dialog_handler.start_dialog(state, [
                                f"We're back on the admin panel.",
                                "How about we try to hack the smart lamp now?",
                                "If we can see the time it usually turns on and off, we can track their schedule.",
                                "Know the time they wake up...",
                                "The time they leave for work..."
                            ], char_delay=20)
    elif state.terminal_rect.collidepoint((mx, my)):
            state.browser_focus = None

