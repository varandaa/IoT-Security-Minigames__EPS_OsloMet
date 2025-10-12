def login_attempt(state):
    """Handle login attempt in browser"""
    
    state.browser_username = ""
    state.browser_password = ""
    state.browser_focus = None
    
    if state.bypassed:
        state.login_failed = False
        return True
    else:
       # print("login failed")
        state.login_failed = True
        return False