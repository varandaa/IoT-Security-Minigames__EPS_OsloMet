def login_attempt(state):
    """Handle login attempt in browser"""
    state.output_lines.append(f"[browser] Attempting login to {state.current_folder} ...")
    
    if state.bypassed:
        state.output_lines.append("[browser] Login bypassed: shell access granted!")
        state.browser_username = ""
        state.browser_password = ""
        state.browser_focus = None
        return True
    
    if state.browser_username == "admin" and state.browser_password == "admin":
        #state.output_lines.append("[browser] Login successful. Welcome, admin.")
        state.browser_username = ""
        state.browser_password = ""
        state.browser_focus = None
        return True
    else:
        #state.output_lines.append("[browser] Login failed: invalid credentials.")
        state.failed_login = True
        return False