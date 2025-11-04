import pygame
import sys
import time
from game_state import GameState
from ui.terminal import draw_terminal
from ui.browser import draw_browser
from handlers.event_handler import handle_events
from handlers.resize_handler import handle_resize
from handlers import dialog_handler
from handlers import audio_handler
from minigames import smart_lock

def main():
    pygame.init()
    
    # Initialize game state
    state = GameState()
    
    # Initialize smart lock minigame
    lock_game = smart_lock.init_smart_lock(state.screen, state.WIDTH, state.HEIGHT)
    
    # DEBUG: Start with smart lock active
    #lock_game.start()
    
    # Track when door was unlocked for delay
    door_unlock_time = None
    
    # Main loop
    while True:
        dt = state.clock.tick(30)
        state.update_cursors(dt)
        # Update dialog handler (typewriter animation)
        dialog_handler.update_dialog(state, dt)
        # Update audio visualization
        audio_handler.update_visualization(dt)
        state.check_transition()
        
        # Track when door is unlocked
        if lock_game.active and lock_game.won and door_unlock_time is None:
            door_unlock_time = time.time()
        
        # Check if door was just unlocked and show victory dialog after 1 second
        if lock_game.active and lock_game.won and not lock_game.victory_dialog_shown:
            if door_unlock_time and (time.time() - door_unlock_time >= 1.0):
                lock_game.victory_dialog_shown = True
                dialog_handler.start_dialog(state, [
                    "Congratulations!",
                    "You've successfully completed all the hacking challenges!",
                    "You've infiltrated the smart home network and unlocked the door.",
                    "Mission accomplished!",
                    "Press ESC to exit the game."
                ], char_delay=20)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(state, event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if smart lock is active first
                if lock_game.active:
                    lock_game.handle_click(event.pos)
                else:
                    handle_events(state, event)
            elif event.type == pygame.KEYDOWN:
                # Allow ESC to exit the game after winning
                if lock_game.active and lock_game.won and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                else:
                    handle_events(state, event)
            else:
                handle_events(state, event)
        
        # Draw main game
        draw_terminal(state)
        draw_browser(state)
        
        # Draw smart lock overlay if active
        if lock_game.active:
            lock_game.draw()
        
        # Draw dialog overlay if active (on top of everything)
        dialog_handler.draw_dialog(state)
        pygame.display.flip()

if __name__ == "__main__":
    main()