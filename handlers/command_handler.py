import config
import time
from handlers.arduino_handler import send_command_to_arduino
from ui.terminal import draw_terminal
from ui.browser import draw_browser
import pygame
import sys
import random

# Minigames
from minigames import camera as camera_minigame
from minigames import router as router_minigame
from minigames import wifi as wifi_minigame 
from handlers import dialog_handler


def wait(state, seconds):
    """Wait while processing events"""
    draw_terminal(state)
    draw_browser(state)
    pygame.display.flip()
    
    t0 = time.time()
    while time.time() - t0 < seconds:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.VIDEORESIZE:
                from handlers.resize_handler import handle_resize
                handle_resize(state, e.w, e.h)
        time.sleep(0.01)


def animate_bruteforce(state, total=1000, duration=3.0, prefix="Trying"):
    if total <= 0:
        return

    # Create a placeholder progress line and remember its index
    state.output_lines.append(f"{prefix} 0/{total} (0%)")
    progress_idx = len(state.output_lines) - 1

    interval = float(duration) / float(total)
    # Defensive minimum sleep to avoid too tight loops
    interval = max(0.001, interval)

    i = 0
    try:
        while i <= total:
            percent = int((i / total) * 100)
            state.output_lines[progress_idx] = f"{prefix} {i}/{total} ({percent}%)"

            # draw and process events so UI stays responsive
            draw_terminal(state)
            draw_browser(state)
            pygame.display.flip()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif e.type == pygame.VIDEORESIZE:
                    from handlers.resize_handler import handle_resize
                    handle_resize(state, e.w, e.h)

            time.sleep(interval)
            i += 1
    finally:
        # Ensure the progress flag is cleared if present
        try:
            state.current_page["is_being_brute_forced"] = False
        except Exception:
            pass

def execute_command(state, cmd):
    """Execute terminal command"""
    cmd = cmd.strip()
    skip = False
    if cmd == "help":
        show_help(state)
    elif cmd == 'ls':
        list_files(state)
    elif cmd.split(" ")[0] == "cd":
        change_directory(state, cmd)
    elif cmd[:2] == "./":
        run_exploit(state, cmd[2:])
    elif cmd == "clear":
        state.output_lines = ["Welcome to Clippy's terminal.", "Type 'help' for commands."]
    elif cmd == "":
        pass
    elif cmd == "nmcli":
        if state.current_page["id"] != "empty":
                dialog_handler.start_dialog(state, [
                    "We are already inside the network.",
                    "There is no need to run 'nmcli' again."
                ], char_delay=20)
                skip = True    
        if not skip:
            state.output_lines.append("[+]Looking for nearby Wifi networks...")
            wait(state, 1)
            state.output_lines.append("[+]Web page with Wifi networks opened!")
            wifi_minigame.on_wifi_analyser(state, cmd)
    elif cmd == "wireshark":
        # Open a simple terminal-side packet inspector with sample packets
        # Build a few sample packets; one contains Giggle credentials
        # Attach inspector state to game state
        if state.current_page["id"] != "smart_fridge":
                dialog_handler.start_dialog(state, [
                    "I see you want to inspect the network traffic.",
                    "Smart.",
                    "But we should stick to the plan, there is no need to run 'wireshark' right now."
                ], char_delay=20)
                skip = True
        if not skip:
            state.packet_inspector = {
                "visible": True,
                "packets": config.packets,
                # rects will be filled during drawing for click detection
                "packet_rects": []
            }
            state.output_lines.append("[+]Opened packet inspector (type 'wireshark' again or press ESC to close)")
    else:
        state.output_lines.append(f"'{cmd}' is not recognized as a command.")

def show_help(state):
    """Show available commands"""
    state.output_lines.append("Available commands:")
    state.output_lines.append("  help  - Show this message")
    state.output_lines.append("  ls  - List the files in this folder")
    state.output_lines.append("  cd {directory_name}  - Change folder to the desired one.")
    state.output_lines.append("                         Use 'cd ..' to go back to previous directory.")
    state.output_lines.append("                         You can see the folder you're currently in behind the '>'")
    state.output_lines.append("  ./{exploit_name}  - Run an exploit")
    state.output_lines.append("  clear  - Clear the screen (can also use CTRL+L)")
    state.output_lines.append("  nmcli  - Scan for nearby Wifi networks and open web page to view them")
    state.output_lines.append("  wireshark - Open a packet inspector in the terminal to inspect network traffic")

def list_files(state):
    """List files in current directory"""
    for file in config.PATH.get(state.current_folder.split("/")[state.level]):
        state.output_lines.append(file)

def change_directory(state, cmd):
    """Change current directory"""
    if len(cmd.split(" ")) == 1:
        state.output_lines.append("You must specify the folder you wish to go to.")
    else:
        folder = cmd.split(" ")[1]
        if folder == "..":
            if state.current_folder == "/devices":
                state.output_lines.append("You can't go back any further!")
            else:
                state.current_folder = "/devices"
                state.level -= 1
        elif folder in config.PATH.get("devices"):
            state.current_folder += "/" + folder
            state.level += 1
        else:
            state.output_lines.append(f"{folder} isn't a folder.")

def run_exploit(state, exploit_cmd):
    """Run an exploit"""
    exploit = exploit_cmd.split(" ")[0]
    if exploit in config.PATH.get("devices"):
        state.output_lines.append("That is a folder. It isn't an exploit!")
    elif exploit in config.PATH.get(state.current_folder.split("/")[state.level]):
        state.output_lines.append("[+]Starting Exploit...")
        wait(state, 1)
        state.output_lines.append("[+]Scanning for the device on the network...")
        wait(state, 3)
        
        if state.current_folder == "/devices/RouteSimple":
            # Delegate router exploit handling to the router minigame module
            if state.current_page["id"] != "route_simple_login":
                dialog_handler.start_dialog(state, [
            "We already hacked the router!",
            "There is no need need to run these exploits again.",
            "Let's search for my 'BruteForce' folder and hack the Camera.",
            "Remember 'cd ..' to go to the previous directory"
        ], char_delay=20)
                pass
            else:
                success = router_minigame.on_exploit_attempt(state, exploit)
                if success:
                    # Defensive: ensure progression state reflects router hacked
                    try:
                        state.current_stage_index = max(state.current_stage_index, 0)
                        send_command_to_arduino("A") 
                    except Exception:
                        pass
        
        elif state.current_folder == "/devices/BruteForce" and state.current_page["id"]=="camera_login":
            # Delegate camera bruteforce handling to the camera minigame module
            if (state.current_page["id"] != "camera_login"):
                print("Already hacked")
            else:
                if exploit == "hydra":
                    wordlist = exploit_cmd.split(" ")[1]
                    if wordlist not in config.PATH.get("BruteForce"):
                        state.output_lines.append(f"[-]Wordlist '{wordlist}' not found in this folder.")
                        return
                    
                    state.output_lines.append("[+]SmartCamPro camera has been found! (IP: 192.168.1.102)")

                    # Simulate brute force attack
                    state.current_page["is_being_brute_forced"] = True
                    state.current_page["username"] = "*******"
                    state.current_page["password"] = "*******"
                    wait(state, 2)

                    state.output_lines.append("[+]Starting brute force attack using " + exploit + "...")

                    # Animate trying combinations (1000 by default over ~3s)
                    animate_bruteforce(state, total=random.randint(1000,1500), duration=3.0, prefix="Trying credentials:")
                    
                    if wordlist != "common-credentials.txt":
                        dialog_handler.start_dialog(state, [
                            f"The wordlist '{wordlist}' doesn't seem to have the right credentials.",
                            "Try using 'common-credentials.txt' instead. It should have what we need."
                        ], char_delay=20)
                        state.output_lines.append(f"[-]The wordlist '{wordlist}' doesn't seem to have the right credentials.")
                        return

                    # Use camera minigame handler
                    camera_minigame.on_bruteforce_success(state, exploit)
                else:
                    dialog_handler.start_dialog(state, [
                        f"{exploit} is not effective against this device.",
                        "You should try using 'hydra' to brute force the camera login.",
                        "With some wordlists, it should be possible to get in.",
                        "Try ./hydra <wordlist>.",
                        "You can find it in the 'BruteForce' folder."
                    ], char_delay=20)
                    state.output_lines.append(f"[-]{exploit} is not effective against this device.")
        elif state.current_folder == "/devices/Wifi":
            if exploit.startswith("fern-wifi-cracker"):
                wifi_minigame.on_wifi_crack_attempt(state, exploit_cmd, wait)
        else:
            state.output_lines.append("[-]This device wasn't found on the network. What is the device you're trying to attack?")
    else:
        state.output_lines.append(f"{exploit} doesn't exist in this folder")