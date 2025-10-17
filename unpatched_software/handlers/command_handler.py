import config
import time
from ui.terminal import draw_terminal
from ui.browser import draw_browser
import pygame
import sys

# Minigames
from minigames import camera as camera_minigame
from minigames import router as router_minigame

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

def execute_command(state, cmd):
    """Execute terminal command"""
    cmd = cmd.strip()
    
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

def run_exploit(state, exploit):
    """Run an exploit"""
    if exploit in config.PATH.get("devices"):
        state.output_lines.append("That is a folder. It isn't an exploit!")
    elif exploit in config.PATH.get(state.current_folder.split("/")[state.level]):
        state.output_lines.append("[+]Starting Exploit...")
        wait(state, 1)
        state.output_lines.append("[+]Scanning for the device on the network...")
        wait(state, 3)
        
        if state.current_folder == "/devices/RouteSimple":
            # Delegate router exploit handling to the router minigame module
            router_minigame.on_exploit_attempt(state, exploit)
        elif state.current_folder == "/devices/BruteForce" and state.curren:
            # Delegate camera bruteforce handling to the camera minigame module
            if (state.current_page_index != 2):
                print("Already hacked")
            else:
                state.output_lines.append("[+]SmartCamPro camera has been found! (IP: 145.40.68.12)")
                # Simulate brute force attack
                wait(state, 2)
                state.output_lines.append("[+]Starting brute force attack using " + exploit + "...")
                wait(state, 5)
                # Use camera minigame handler
                camera_minigame.on_bruteforce_success(state, exploit)
        else:
            state.output_lines.append("[-]This device wasn't found on the network. What is the device you're trying to attack?")
    else:
        state.output_lines.append(f"{exploit} doesn't exist in this folder")