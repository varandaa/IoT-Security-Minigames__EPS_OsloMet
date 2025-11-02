import pygame
import os
import random

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Audio files to check for in assets folder
AUDIO_FILES = {
    "homepod_recording": "audio_test.mp3",
    "homepod_audio": "audio_test.mp3",
    "homepod": "audio_test.mp3",
}

# Audio visualization state
audio_visualization_state = {
    "is_playing": False,
    "start_time": 0,
    "wave_heights": [0] * 20,  # 20 bars for the visualization
    "animation_timer": 0,
}

def update_visualization(dt):
    """Update the visualization animation based on time"""
    if is_audio_playing():
        audio_visualization_state["is_playing"] = True
        audio_visualization_state["animation_timer"] += dt
        
        # Update wave heights with some oscillation
        for i in range(len(audio_visualization_state["wave_heights"])):
            # Create an oscillating wave effect
            base_height = 20 + 15 * abs(os.urandom(1)[0] / 128 - 1)
            audio_visualization_state["wave_heights"][i] = base_height
    else:
        if audio_visualization_state["is_playing"]:
            # Audio just stopped, fade out
            for i in range(len(audio_visualization_state["wave_heights"])):
                audio_visualization_state["wave_heights"][i] *= 0.7
            
            # Check if all are essentially zero
            if max(audio_visualization_state["wave_heights"]) < 1:
                audio_visualization_state["is_playing"] = False
                audio_visualization_state["wave_heights"] = [0] * 20

def draw_sound_wave(screen, x, y, width, height, color=(100, 200, 255)):
    """Draw animated sound wave bars"""
    if not audio_visualization_state["wave_heights"]:
        return
    
    bar_count = len(audio_visualization_state["wave_heights"])
    bar_width = max(2, (width - (bar_count - 1)) // bar_count)
    spacing = 2
    current_x = x
    
    for i, wave_height in enumerate(audio_visualization_state["wave_heights"]):
        bar_height = min(height, int(wave_height))
        bar_y = y + (height - bar_height) // 2
        
        # Draw bar with gradient effect
        pygame.draw.rect(screen, color, (current_x, bar_y, bar_width, bar_height), border_radius=2)
        
        # Add brighter top for glow effect
        if bar_height > 2:
            bright_color = tuple(min(255, c + 50) for c in color)
            pygame.draw.rect(screen, bright_color, (current_x, bar_y, bar_width, 2), border_radius=2)
        
        current_x += bar_width + spacing

def get_audio_path(audio_name):
    """Get the full path to an audio file in the assets folder"""
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    
    # If audio_name is a key in AUDIO_FILES, use the mapped filename
    if audio_name in AUDIO_FILES:
        filename = AUDIO_FILES[audio_name]
    else:
        filename = audio_name
    
    full_path = os.path.join(assets_dir, filename)
    return full_path if os.path.exists(full_path) else None

def play_audio(audio_name):
    """Play an audio file from the assets folder"""
    audio_path = get_audio_path(audio_name)
    
    if not audio_path:
        print(f"[-] Audio file '{audio_name}' not found in assets folder")
        return False
    
    try:
        sound = pygame.mixer.Sound(audio_path)
        sound.play()
        # Initialize visualization state
        audio_visualization_state["is_playing"] = True
        audio_visualization_state["wave_heights"] = [20] * 20
        return True
    except Exception as e:
        print(f"[-] Error playing audio: {e}")
        return False

def stop_audio():
    """Stop all audio playback"""
    pygame.mixer.stop()

def is_audio_playing():
    """Check if audio is currently playing"""
    return pygame.mixer.get_busy()

def get_available_audio_files():
    """Get list of all audio files available in assets folder"""
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    audio_extensions = ('.wav', '.mp3', '.ogg', '.flac')
    
    available_files = []
    try:
        if os.path.exists(assets_dir):
            for filename in os.listdir(assets_dir):
                if filename.lower().endswith(audio_extensions):
                    available_files.append(filename)
    except Exception as e:
        print(f"[-] Error listing audio files: {e}")
    
    return available_files
