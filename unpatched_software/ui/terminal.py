import pygame
from config import BLACK, GREEN, BORDER

def draw_terminal(state):
    """Draw the terminal pane (left side)"""
    # Background
    pygame.draw.rect(state.screen, BLACK, state.terminal_rect)
    
    # Separator line
    pygame.draw.line(state.screen, BORDER, 
                     (state.terminal_rect.right, 0), 
                     (state.terminal_rect.right, state.HEIGHT), 2)
    
    # Output lines
    y = 10
    line_h = state.mono_font.get_linesize()
    max_lines = max(1, (state.terminal_rect.height - 40) // line_h)
    
    for line in state.output_lines[-max_lines:]:
        rendered = state.mono_font.render(line, True, GREEN)
        state.screen.blit(rendered, (state.terminal_rect.x + 10, y))
        y += line_h
    
    # Input line with cursor
    prompt = state.current_folder + "> " + state.input_text
    if state.cursor_visible:
        prompt += "_"
    rendered_input = state.mono_font.render(prompt, True, GREEN)
    state.screen.blit(rendered_input, (state.terminal_rect.x + 10, y))