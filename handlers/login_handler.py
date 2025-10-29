from config import USERNAME_LIGHT, PASSWORD_LIGHT, USERNAME_GIGGLE, PASSWORD_GIGGLE
from handlers import dialog_handler

def login_attempt(state):
    """Handle login attempt in browser (per page)"""
    page = state.current_page
    # Read current credentials (do this before clearing)
    username = page.get("username", "")
    password = page.get("password", "")

    # Clear focus after attempting
    state.browser_focus = None

    # Smart light login: accept any non-empty username/password as a successful login
    if page.get("id") == "smart_light_login":
        if username == USERNAME_LIGHT and password == PASSWORD_LIGHT:
            page["bypassed"] = True
            page["login_failed"] = False
            # navigate to admin panel
            state.go_to_page_by_id("smart_light_admin")
            dialog_handler.start_dialog(state, [
                f"We've reached the smart light hub login page.",
                "Let's try to bypass its login to access the admin panel.",
                "The user often uses the same password multiple times.",
                "Maybe we can use the password we found for the camera ?",
                "It's on the terminal history if you need to check."
            ], char_delay=20)
            state.current_stage_index = max(state.current_stage_index, 4)
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
            dialog_handler.start_dialog(state, [
                "Successful login to Giggle HomePod.",
                "Accessing Giggle admin panel now."
            ], char_delay=20)
            # promote progression a bit (arbitrary stage)
            state.current_stage_index = max(state.current_stage_index, 3)
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