import pygame
from handlers import dialog_handler
from handlers.arduino_handler import send_command_to_arduino

wifi_networks = [
    ("John_Home_Wifi", "WPA2", -40), # the one to be hacked needs to be first
    ("Coffee_Shop_Free_Wifi", "Open", -70),
    ("Pierre_Wifi", "WPA3", -55),
    ("Public_Wifi", "Open", -80),
    ("Office_Network", "WPA2", -90),
]

def on_wifi_analyser(state, tool: str):
    """Open web page showing nearby Wifi networks."""
    state.go_to_page_by_id("wifi_networks")
    dialog_handler.start_dialog(state, [
        "Great! You've found the Wifi networks.",
        "Now you can try to crack the Wifi password using fern-wifi-cracker.",
        "To use it, fern-wifi-cracker {name of the wifi network}."
    ], char_delay=20)

def on_wifi_crack_attempt(state, exploit_cmd: str, wait_func):
    if state.wifi_connected:
        state.output_lines.append("[+]Already connected to the Wifi network.")
        return
    parts = exploit_cmd.split(" ")
    if len(parts) == 2:
        wifi_name = parts[1]
        available_networks = [net[0] for net in wifi_networks]
        if wifi_name == available_networks[0]:
            state.output_lines.append(f"[+]Attempting to crack the Wifi network: {wifi_name}...")
            wait_func(state, 3)
            on_wifi_crack_success(state, wifi_name)
        elif wifi_name in available_networks:
            state.output_lines.append(f"[+]Attempting to crack the Wifi network: {wifi_name}...")
            wait_func(state, 3)
            dialog_handler.start_dialog(state, [
                    f"Awesome! You've cracked the Wifi network '{wifi_name}'.",
                    "But........",
                    "This network isn't the one we need to access the router.",
                    "Try to find the correct one.",
                ], char_delay=20)
        else:
            state.output_lines.append(f"[-]Wifi network '{wifi_name}' not found nearby.")
    else:
        state.output_lines.append("[-]Invalid command format. Use: fern-wifi-cracker <wifi_name>")

def on_wifi_crack_success(state, wifi_name: str):
    """Handle state updates when Wifi cracking succeeds."""
    state.output_lines.append(f"[+]Successfully cracked the Wifi network: {wifi_name}!")
    state.go_to_page_by_id("route_simple_login")
    state.number_of_hacked_devices = getattr(state, "number_of_hacked_devices", 0) + 1
    send_command_to_arduino("2")
    dialog_handler.start_dialog(state, [
            f"Great! You've cracked the Wifi network '{wifi_name}'.",
            "Now we're inside the home network.",
            "I sent you to the router's login page.",
            "From here, you can access the router's admin panel and take control of the network.",
            "To do so, there is a folder with the same name as the router that contains exploits my Dark Web friends sent me.",
            "Try to find the right exploit and run it to hack the router.",
        ], char_delay=20)