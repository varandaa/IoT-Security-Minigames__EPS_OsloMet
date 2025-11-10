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
    elif cmd.split(" ")[0] == "hydra":
        run_hydra(state, cmd)
    elif cmd.split(" ")[0] == "fern-wifi-cracker":
        run_fern_wifi_cracker(state, cmd)
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
        # Build a few sample packets; one contains Giggle credentialsdevices
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
    state.output_lines.append("  ./{exploit_name}  - Run an exploit")
    state.output_lines.append("  hydra {wordlist}.txt  - Brute force the camera using the specified")
    state.output_lines.append("                          wordlist")
    state.output_lines.append("  fern-wifi-cracker {network_name}  - Crack a WiFi network")
    state.output_lines.append("  clear  - Clear the screen (can also use CTRL+L)")
    state.output_lines.append("  nmcli  - Scan for nearby Wifi networks and open web page to view them")
    state.output_lines.append("  wireshark - Open a packet inspector in the terminal to inspect network")
    state.output_lines.append("              traffic")

def list_files(state):
    """List files in current directory"""
    for file in config.PATH.get("root", []):
        state.output_lines.append(file)

def change_directory(state, cmd):
    """Placeholder - cd command disabled"""
    state.output_lines.append("The 'cd' command is disabled. All files are in the root directory.")

def run_hydra(state, cmd):
    """Run hydra brute force attack on the camera"""
    # Parse wordlist from command
    parts = cmd.split(" ")
    if len(parts) < 2:
        state.output_lines.append("[-]Please specify a wordlist. Usage: hydra <wordlist>")
        return
    
    wordlist = parts[1]
    available_exploits = config.PATH.get("root", [])
    
    # Camera brute force
    if state.current_page["id"] != "camera_login":
        dialog_handler.start_dialog(state, [
            "The camera has already been hacked!",
            "There's no need to run this exploit again.",
            "Let's move on to the next target."
        ], char_delay=20)
    else:
        if wordlist not in available_exploits:
            state.output_lines.append(f"[-]Wordlist '{wordlist}' not found.")
            return
        
        state.output_lines.append("[+]SmartCamPro camera has been found! (IP: 192.168.1.102)")

        # Simulate brute force attack
        state.current_page["is_being_brute_forced"] = True
        state.current_page["username"] = "*******"
        state.current_page["password"] = "*******"
        wait(state, 2)

        state.output_lines.append("[+]Starting brute force attack using hydra...")

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
        camera_minigame.on_bruteforce_success(state, "hydra")

def run_fern_wifi_cracker(state, cmd):
    """Run fern-wifi-cracker to crack a WiFi network"""
    # Parse network name from command
    parts = cmd.split(" ")
    if len(parts) < 2:
        state.output_lines.append("[-]Please specify the WiFi network name to crack. Usage: fern-wifi-cracker <network_name>")
        return
    
    network_name = parts[1]
    
    # Call the wifi minigame handler with the full command
    wifi_minigame.on_wifi_crack_attempt(state, cmd, wait)

def run_exploit(state, exploit_cmd):
    """Run an exploit"""
    exploit = exploit_cmd.split(" ")[0]

    available_exploits = config.PATH.get("root", [])
    
    if exploit not in available_exploits:
        state.output_lines.append(f"{exploit} doesn't exist")
        return

    state.output_lines.append("[+]Starting Exploit...")
    wait(state, 1)
    state.output_lines.append("[+]Scanning for the device on the network...")
    wait(state, 3)
    
    # Determine which exploit to run based on exploit name
    if exploit.startswith("exploit-"):
        # Router exploits
        if state.current_page["id"] != "route_simple_login":
            dialog_handler.start_dialog(state, [
                "We already hacked the router!",
                "There is no need need to run these exploits again.",
                "Let's try to hack the Camera next.",
                "Look for the 'hydra' tool!"
            ], char_delay=20)
        else:
            success = router_minigame.on_exploit_attempt(state, exploit)
            if success:
                # Defensive: ensure progression state reflects router hacked
                try:
                    state.current_stage_index = max(state.current_stage_index, 0)
                    send_command_to_arduino("A") 
                except Exception:
                    pass
    
    elif exploit in ["medusa", "ncrack", "patator", "crowbar", "aircrack-ng", "reaver", "bully", "wifite"]:
        # Other exploits not implemented yet
        state.output_lines.append(f"[-]{exploit} is not effective for the current target.")
        state.output_lines.append("Try using other available tools.")
    else:
        state.output_lines.append(f"[-]Unknown exploit: {exploit}")
