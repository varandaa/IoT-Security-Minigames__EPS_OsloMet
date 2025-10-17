import pygame
import os

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "assets")
CLIPPY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "hacker_clippy.png")


def start_dialog(state, lines, char_delay=25, image_path=None):
    """Start a dialog sequence.

    lines: list of strings (each dialog entry)
    char_delay: ms per character (lower == faster)
    image_path: optional path to portrait image; defaults to hacker_clippy.png in assets
    """
    if image_path is None:
        image_path = CLIPPY_PATH

    # Ensure state has a dialog container
    state.dialog = {
        "lines": list(lines),
        "index": 0,
        "char_index": 0,
        "char_timer": 0,
        "char_delay": char_delay,
        "image_path": image_path,
        "image": None,
        "visible": True,
    }


def _ensure_image_loaded(state):
    dlg = getattr(state, "dialog", None)
    if not dlg:
        return
    if dlg.get("image") is None:
        try:
            img = pygame.image.load(dlg["image_path"]).convert_alpha()
            # scale to a reasonable height for dialog (bigger now)
            target_h = 180
            scale = target_h / img.get_height()
            img = pygame.transform.smoothscale(img, (int(img.get_width() * scale), target_h))
            dlg["image"] = img
        except Exception:
            dlg["image"] = None


def update_dialog(state, dt):
    """Advance the typewriter animation. dt in milliseconds."""
    dlg = getattr(state, "dialog", None)
    if not dlg or not dlg.get("visible"):
        return

    _ensure_image_loaded(state)

    lines = dlg["lines"]
    idx = dlg["index"]
    if idx >= len(lines):
        # finished
        dlg["visible"] = False
        state.dialog = None
        return

    line = lines[idx]
    if dlg["char_index"] < len(line):
        dlg["char_timer"] += dt
        while dlg["char_timer"] >= dlg["char_delay"] and dlg["char_index"] < len(line):
            dlg["char_index"] += 1
            dlg["char_timer"] -= dlg["char_delay"]


def _render_wrapped_text(surface, text, font, color, x, y, max_width, line_spacing=2):
    """Render text with word-wrapping; returns final y after drawing."""
    words = text.split(" ")
    line = ""
    for w in words:
        test_line = (line + " " + w).strip()
        w_surf = font.render(test_line, True, color)
        if w_surf.get_width() <= max_width:
            line = test_line
        else:
            # draw current line
            if line:
                surf = font.render(line, True, color)
                surface.blit(surf, (x, y))
                y += surf.get_height() + line_spacing
            line = w

    if line:
        surf = font.render(line, True, color)
        surface.blit(surf, (x, y))
        y += surf.get_height() + line_spacing

    return y


def draw_dialog(state):
    """Draw the dialog box if active."""
    dlg = getattr(state, "dialog", None)
    if not dlg or not dlg.get("visible"):
        return

    screen = state.screen
    sw = state.WIDTH
    sh = state.HEIGHT

    # Bigger dialog box and centered horizontally at the bottom
    box_h = 220
    box_w = sw - 120
    box_x = 60
    box_y = sh - box_h - 40

    # Dim overlay to focus attention on dialog
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))

    # Background
    rect = pygame.Rect(box_x, box_y, box_w, box_h)
    pygame.draw.rect(screen, (20, 20, 20), rect, border_radius=8)
    pygame.draw.rect(screen, (140, 140, 140), rect, 2, border_radius=8)

    # Image
    img = dlg.get("image")
    img_x = box_x + 18
    img_y = box_y + (box_h - 180) // 2
    text_x = img_x + 180 + 18
    text_w = box_w - (text_x - box_x) - 24

    if img:
        screen.blit(img, (img_x, img_y))

    # Current composed text (typewriter)
    idx = dlg["index"]
    if idx >= len(dlg["lines"]):
        return
    full_line = dlg["lines"][idx]
    visible_text = full_line[: dlg["char_index"]]

    # Draw name area (optional) - we don't have speaker name in this simple implementation

    # Render wrapped visible text
    _render_wrapped_text(screen, visible_text, state.ui_font, (230, 230, 230), text_x, box_y + 20, text_w, line_spacing=6)


def handle_key(state, event):
    """Handle keyboard while dialog active. Returns True if event consumed."""
    dlg = getattr(state, "dialog", None)
    if not dlg or not dlg.get("visible"):
        return False

    # Only handle ENTER/RETURN
    if event.key == pygame.K_RETURN:
        idx = dlg["index"]
        if idx >= len(dlg["lines"]):
            # no more
            dlg["visible"] = False
            state.dialog = None
            return True

        line = dlg["lines"][idx]
        if dlg["char_index"] < len(line):
            # finish current line immediately
            dlg["char_index"] = len(line)
            dlg["char_timer"] = 0
            return True
        else:
            # advance to next line
            dlg["index"] += 1
            dlg["char_index"] = 0
            dlg["char_timer"] = 0
            if dlg["index"] >= len(dlg["lines"]):
                dlg["visible"] = False
                state.dialog = None
            return True

    return False
