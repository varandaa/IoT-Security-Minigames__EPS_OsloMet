def login_attempt(state):
    """Handle login attempt in browser (per page)"""
    page = state.current_page
    page["username"] = ""
    page["password"] = ""
    state.browser_focus = None
    if page["bypassed"]:
        page["login_failed"] = False
        return True
    else:
        page["login_failed"] = True
        return False