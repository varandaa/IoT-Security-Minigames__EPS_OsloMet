import pygame
import sys
from game_state import GameState
from ui.terminal import draw_terminal
from ui.browser import draw_browser
from handlers.event_handler import handle_events
from handlers.resize_handler import handle_resize

def main():
    pygame.init()
    
    # Initialize game state
    state = GameState()
    
    # Main loop
    while True:
        dt = state.clock.tick(30)
        state.update_cursors(dt)
        state.check_transition()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(state, event.w, event.h)
            else:
                handle_events(state, event)
        
        draw_terminal(state)
        draw_browser(state)
        pygame.display.flip()

if __name__ == "__main__":
    main()