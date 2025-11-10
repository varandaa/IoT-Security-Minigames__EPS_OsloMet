from config import USERNAME_LIGHT, PASSWORD_LIGHT, USERNAME_GIGGLE, PASSWORD_GIGGLE
from handlers import dialog_handler
from handlers.arduino_handler import send_command_to_arduino

def login_attempt(state):
    """Handle login attempt in browser (per page)"""
    page = state.current_page
    # Read current credentials (do this before clearing)
    username = page.get("username", "")
    password = page.get("password", "")

    # Clear focus after attempting
    state.browser_focus = None

    if page.get("id") == "smart_light_login":
        if username == USERNAME_LIGHT and password == PASSWORD_LIGHT:
            page["bypassed"] = True
            page["login_failed"] = False
            # navigate to admin panel
            state.go_to_page_by_id("smart_light_admin")
            send_command_to_arduino("D")
            dialog_handler.start_dialog(state, [
                f"We've reached the smart light hub admin panel.",
                "From the light usage history we can see that during week days they get up at 7.",
                "They also go to sleep at around 23 or midnight.",
                "Most importantly, we know they aren't usually home from 9 to 18. That's the best time to break in!"
            ], char_delay=20)
            state.current_stage_index = max(state.current_stage_index, 2)
            return True
        else:
            page["login_failed"] = True
            return False

    # Giggle HomePod login: check against Giggle credentials in config
    if page.get("id") == "giggle_login":
        if username == USERNAME_GIGGLE and password == PASSWORD_GIGGLE:
            page["bypassed"] = True
            page["login_failed"] = False
            state.go_to_page_by_id("giggle_admin")
            send_command_to_arduino("F")
            dialog_handler.start_dialog(state, [
                "We managed to access the HomePod admin panel!",
                "We can see there's an audio recording stored on the device.",
                "Press the button to listen the recording, it may contain important information."
            ], char_delay=20)
            # promote progression a bit (arbitrary stage)
            state.current_stage_index = max(state.current_stage_index, 4)
            return True
        else:
            page["login_failed"] = True
            return False

    # Default behavior for other pages: succeed only if already bypassed
    if page.get("bypassed"):
        page["login_failed"] = False
        return True
    else:
        page["login_failed"] = True
        return False