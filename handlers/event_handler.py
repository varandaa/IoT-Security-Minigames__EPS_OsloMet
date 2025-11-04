import pygame
from handlers.arduino_handler import send_command_to_arduino
from handlers.command_handler import execute_command
from handlers.login_handler import login_attempt
from handlers import dialog_handler
from handlers import command_handler
from handlers import audio_handler
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
    # Close packet inspector with ESC
    inspector = getattr(state, 'packet_inspector', None)
    if inspector and inspector.get('visible'):
        if event.key == pygame.K_ESCAPE:
            inspector['visible'] = False
            state.output_lines.append("[+]Closed packet inspector")
            return
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

    # If packet inspector is visible, handle its clicks first
    inspector = getattr(state, 'packet_inspector', None)
    if inspector and inspector.get('visible') and state.terminal_rect.collidepoint((mx, my)):
        # Close button
        close_rect = inspector.get('close_rect')
        if close_rect and close_rect.collidepoint((mx, my)):
            inspector['visible'] = False
            state.output_lines.append("[+]Closed packet inspector")
            return

        # Packet rows - single click to select and show dialog for special packets
        for entry in inspector.get('packet_rects', []):
            r = entry.get('rect')
            if r and r.collidepoint((mx, my)):
                packet_idx = entry.get('index', -1)
                pkt = entry.get('packet')
                
                # Select the packet
                inspector['selected_index'] = packet_idx
                
                # If this is the 2nd packet (index 1), show dialog about credentials
                if packet_idx == 1:
                    payload = pkt.get('payload', '')
                    if not payload:
                        payload = "(no payload)"
                    lines = [
                        "We found some credentials in the packet!",
                        f"We can see them in the packet bytes - {payload}",
                        "They are using HTTP instead of HTTPS, which doesn't encrypt the data.",
                        "This means anyone inside the network can read it.",
                        "This looks like a login attempt to the Giggle SmartFridge.",
                        "There is another Giggle device on the network.",
                        "We can certainly use the credentials we discovered to access it!"
                    ]
                    dialog_handler.start_dialog(state, lines, char_delay=15)
                    # Mark that user has seen the credentials packet
                    state.seen_credentials_packet = True
                
                return


    # Check if Clippy icon was clicked (in terminal area)
    clippy_rect = getattr(state, "clippy_rect", None)
    if clippy_rect and clippy_rect.collidepoint((mx, my)):
        from ui.terminal import get_help_dialog_for_page
        help_text = get_help_dialog_for_page(state)
        dialog_handler.start_dialog(state, help_text, char_delay=20)
        return

    connection_pages = [ "route_simple_login", "camera_login", "smart_light_login", "giggle_login" ]  # id of pages that can connect to others

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

                        # Only allow access to the NEXT stage (not previous stages)
                        # required_stage must equal current_stage_index + 1
                        if required_stage > (state.current_stage_index + 1):
                            # blocked: show dialog explaining the order
                            dialog_handler.start_dialog(state, [
                                f"You can't access {dev_name} yet.",
                                "Let's focus on the current objective and follow the order."
                            ], char_delay=20)
                            return
                        elif required_stage < (state.current_stage_index + 1):
                            # blocked: show dialog explaining the order
                            dialog_handler.start_dialog(state, [
                                f"You already accessed {dev_name}.",
                                "Continue to the next objective."
                            ], char_delay=20)
                            return

                        # Allowed: perform navigation
                        if "cam" in dev_name.lower() or "camera" in dev_name.lower():
                            state.go_to_page_by_id("camera_login")  # camera login page
                            send_command_to_arduino("3")
                        elif "fridge" in dev_name.lower():
                            state.go_to_page_by_id("smart_fridge")  # smart fridge page
                            send_command_to_arduino("E") # since we don't hack it, send E to indicate "hacked"
                            # Update progression when accessing fridge
                            state.current_stage_index = max(state.current_stage_index, 3)
                            dialog_handler.start_dialog(state, [
                                    f"We're on the Smart Fridge page.",
                                    "There isn't anything very interesting for us here.",
                                    "However, we can see we're already logged in with the user's Giggle account.",
                                    "We can try to inspect the traffic going through the network using the 'wireshark' command.",
                                    "If there are some unencrypted credentials going through the network, we will be able to read them.",
                                    "Let's give the 'wireshark' command a try!"
                                ], char_delay=20)
                        elif "homepod" in dev_name.lower():
                            # Giggle HomePod device
                            state.go_to_page_by_id("giggle_login")
                            send_command_to_arduino("6")
                            page = state.current_page
                            if not page.get("bypassed", False):
                            #     # If already bypassed, go to admin panel directly
                            #     state.go_to_page_by_id("giggle_admin")
                            # else:
                                dialog_handler.start_dialog(state, [
                                    f"We've reached the Giggle HomePod login page.",
                                    "We have the Giggle credentials from the wireshark packet we inspected.",
                                    "Let's use them to login and access the HomePod's admin panel."
                                ], char_delay=20)
                        # command_handler.change_directory(state, "cd ..")
                        elif "light" in dev_name.lower() or "lamp" in dev_name.lower():
                            state.go_to_page_by_id("smart_light_login")  # smart light hub page
                            send_command_to_arduino("4")
                            page = state.current_page
                            if not page.get("bypassed", False):
                                dialog_handler.start_dialog(state, [
                                    f"We've reached the smart light hub login page.",
                                    "Let's try to bypass its login to access the admin panel.",
                                    "The user often uses the same password multiple times.",
                                    "Maybe we can use the password we found for the camera ?",
                                    "It's on the terminal history if you need to check."
                                ], char_delay=20)
                        elif "lock" in dev_name.lower() or "door" in dev_name.lower():
                            # Smart Lock device - launch minigame
                            from minigames import smart_lock
                            lock_game = smart_lock.get_smart_lock_game()
                            if lock_game:
                                lock_game.start()
                                dialog_handler.start_dialog(state, [
                                    "Here's the Smart Lock!",
                                    "We know the PIN is 3001 from the HomePod recording.",
                                    "Enter the PIN to unlock the door and complete the mission!"
                                ], char_delay=20)
                            send_command_to_arduino("7")
                            # Update progression when accessing lock
                            state.current_stage_index = max(state.current_stage_index, 5)
                        else:
                            # For other devices, create a new page entry and go there
                            new_url = f"http://{item['ip']}/"
                            state.add_page(new_url, new_url)
                            state.go_to_page_by_url(new_url)

                        return
        # General Router Admin button (shared for many pages)
        router_btn = getattr(state, "router_admin_button_rect", None)
        if router_btn and router_btn.collidepoint((mx, my)):
            # gating rules per page
            if page.get("id") == "smart_fridge":
                if not getattr(state, "seen_credentials_packet", False):
                    dialog_handler.start_dialog(state, [
                        "Hold on, you haven't inspected the network packets yet!",
                        "Go back to the terminal and use the 'wireshark' command to sniff the network traffic.",
                        "See if you can find some interesting informations."
                    ], char_delay=20)
                    return
                # message when allowed
                state.go_to_page_by_id("route_simple_admin")
                dialog_handler.start_dialog(state, [
                    "Back on the device list.",
                    "As we can see there is a 'Giggle-HomePod' device connected to the network.",
                    "We can certainly use the Giggle credentials we just discovered to login into the Home Pod.",
                    "Let's check it out!"
                ], char_delay=20)
                return

            if page.get("id") == "giggle_admin":
                if not getattr(state, "listened_to_homepod", False):
                    dialog_handler.start_dialog(state, [
                        "Hold on! You haven't listened to the HomePod recording yet.",
                        "Click the 'Play Recording' button to hear the recording first.",
                        "It may contain important information you need to gather."
                    ], char_delay=20)
                    return
                # Stop any playing audio before navigating away
                audio_handler.stop_audio()
                state.go_to_page_by_id("route_simple_admin")
                dialog_handler.start_dialog(state, [
                    "Now that we know the PIN, let's just access the Smart Lock.",
                    "This is the last step of our mission.",
                    "Let's go!"
                ], char_delay=20)
                return

            # If coming from camera video, release the camera first
            if page.get("id") == "camera_video":
                try:
                    cap.release()
                except Exception:
                    pass

            # Default behaviour: navigate to route admin
            state.go_to_page_by_id("route_simple_admin")
            dialog_handler.start_dialog(state, [
                "We're back on the admin panel.",
                "How about we try to hack the smart lamp now?",
                "If we can see the time it usually turns on and off, we can track their schedule.",
            ], char_delay=20)
            return
        # Giggle HomePod admin: handle Listen to HomePod button
        elif page.get("id") == "giggle_admin":
            listen_rect = getattr(state, "giggle_listen_button_rect", None)
            if listen_rect and listen_rect.collidepoint(event.pos):
                # Try to play audio from HomePod recording
                success = audio_handler.play_audio("homepod_recording")
                if success:
                    state.output_lines.append("[+] Playing HomePod recording...")
                    # Mark that user has listened to the audio
                    state.listened_to_homepod = True
                    dialog_handler.start_dialog(state, [
                        "Listening to the HomePod recording...",
                        "",
                        "",
                        "They mentioned the PIN of the smart lock!",
                        "It's 3001!"
                    ], char_delay=20)
                else:
                    dialog_handler.start_dialog(state, [
                        "No audio file found.",
                        "The HomePod recording is not available in the system."
                    ], char_delay=20)
                return
    elif state.terminal_rect.collidepoint((mx, my)):
            state.browser_focus = None

