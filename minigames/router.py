"""Router minigame logic and resources.

Contains helpers for handling RouteSimple exploit checks and post-exploit behavior.
"""
import pygame
from handlers import dialog_handler

def on_exploit_attempt(state, exploit: str):
    """Handle exploit attempt results targeting RouteSimple router.

    Returns True when exploit succeeded, False otherwise.
    """
    from config import CORRECT_EXPLOIT
    from handlers.command_handler import wait

    state.output_lines.append("[!]RouteSimple Router has been found! (IP: 192.168.1.1)")
    wait(state, 1)
    state.output_lines.append("[+]Checking if this version is vulnerable...")
    wait(state, 2)

    if exploit == CORRECT_EXPLOIT:
        state.output_lines.append("[!]It's vulnerable!")
        wait(state, 1)
        state.output_lines.append("[+]Sending payload...")
        wait(state, 3)
        state.output_lines.append("[!]The RouteSimple router login has been bypassed!")
        state.current_page["bypassed"] = True
        wait(state, 1)
        state.current_page["bypass_time"] = pygame.time.get_ticks()
        # Advance progression to indicate router is hacked
        try:
            from config import STAGE_ORDER
            # router corresponds to STAGE_ORDER[0]
            state.current_stage_index = max(state.current_stage_index, 0)
            dialog_handler.start_dialog(state, [
                            f"Wohooooo!",
                            "We found an exploit for this unpatched version of the router and managed to bypass it's login!",
                            "From here, we can easily see all the devices in the network.",
                            "I'm so excited!",
                            "Let's start by trying to brute-force the camera.",
                            "In this attack, we will use a hacking tool that allows us to try millions of username/password combinations against the login form in seconds. "
                            "We will use a list of the most common credentials used world-wide to try to access this.",
                            "Press the 'RealViewCamera-1 URL to access it!"
                        ], char_delay=20)
        except Exception:
            pass
        return True
    else:
        state.output_lines.append("[-]This version of RouteSimple isn't vulnerable to this exploit. Maybe try a different one?")
        return False
