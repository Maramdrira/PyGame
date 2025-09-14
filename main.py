# -----------------------------------------------------------
#  main.py  (launcher + original sliding puzzle + stub jigsaw)
# -----------------------------------------------------------
import pygame, sys, os
from pygame.locals import *
from jigsaw import run_jigsaw
from sudoku import run_sudoku
from snake import run_snake

pygame.init()
pygame.mixer.init()

# ------------------ CONSTANTS ------------------------------
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 650
BACKGROUND = (249, 246, 239)
ACCENT_1   = (255, 182, 193)  # Pink - Sliding Puzzle
ACCENT_2   = (176, 224, 230)  # Blue - Jigsaw
ACCENT_3   = (173, 255, 173)  # Green - Snake
ACCENT_4   = (255, 253, 182)  # Yellow - Sudoku
TEXT_COLOR = (70, 70, 70)
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Puzzle Selector")
clock  = pygame.time.Clock()

# ------------------ BACKGROUND IMAGE -----------------------
try:
    background_img = pygame.image.load("assets/background.jpg")
    background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    background_img = None
    print("Background image not found. Using solid color background.")

# ------------------ FONTS ----------------------------------
def safe_font(size):
    try:
        return pygame.font.Font("assets/fonts/cute.ttf", size)
    except:
        return pygame.font.SysFont("comicsansms", size)

title_font = safe_font(60)
btn_font   = safe_font(28)
icon_font  = safe_font(40)  # For button icons

# ------------------ ENHANCED BUTTON ------------------------
def draw_button(rect, color, text, icon=None):
    # Draw button with shadow effect
    shadow_rect = rect.copy()
    shadow_rect.x += 5
    shadow_rect.y += 5
    pygame.draw.rect(screen, (50, 50, 50, 100), shadow_rect, border_radius=15)
    
    # Draw main button
    pygame.draw.rect(screen, color, rect, border_radius=15)
    pygame.draw.rect(screen, (220, 220, 220), rect, 3, border_radius=15)
    
    # Add hover effect
    mouse_pos = pygame.mouse.get_pos()
    if rect.collidepoint(mouse_pos):
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill((255, 255, 255, 30))
        screen.blit(s, rect)
    
    # Add text and icon
    if icon:
        icon_text = icon_font.render(icon, True, TEXT_COLOR)
        screen.blit(icon_text, icon_text.get_rect(center=(rect.centerx, rect.centery - 15)))
        
        txt = btn_font.render(text, True, TEXT_COLOR)
        screen.blit(txt, txt.get_rect(center=(rect.centerx, rect.centery + 20)))
    else:
        txt = btn_font.render(text, True, TEXT_COLOR)
        screen.blit(txt, txt.get_rect(center=rect.center))
    
    return rect

# ------------------ PLACEHOLDER JIGSAW SCENE ---------------
def jigsaw_scene():
    run_jigsaw()

# ------------------ PLACEHOLDER SNAKE SCENE ----------------
def snake_scene():
    run_snake()

# ------------------ PLACEHOLDER SUDOKU SCENE ---------------
def sudoku_scene():
    run_sudoku()

# ------------------ LAUNCHER -------------------------------
def launcher():
    # Calculate button positions for 2x2 grid
    button_width, button_height = 280, 180
    margin_x, margin_y = 100, 150
    spacing_x, spacing_y = 40, 40
    
    btn_slide  = pygame.Rect(margin_x, margin_y, button_width, button_height)
    btn_jigsaw = pygame.Rect(margin_x + button_width + spacing_x, margin_y, button_width, button_height)
    btn_snake  = pygame.Rect(margin_x, margin_y + button_height + spacing_y, button_width, button_height)
    btn_sudoku = pygame.Rect(margin_x + button_width + spacing_x, margin_y + button_height + spacing_y, button_width, button_height)

    while True:
        # Draw background
        if background_img:
            screen.blit(background_img, (0, 0))
            # Add semi-transparent overlay for better text visibility
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 100))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill(BACKGROUND)
        
        # Draw title
        title = title_font.render("Choose a Game", True, TEXT_COLOR)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 80)))
        
        # Draw buttons with icons
        draw_button(btn_slide,  ACCENT_1, "Sliding Puzzle")
        draw_button(btn_jigsaw, ACCENT_2, "Jigsaw Puzzle")
        draw_button(btn_snake,  ACCENT_3, "Snake Game")
        draw_button(btn_sudoku, ACCENT_4, "Sudoku Puzzle")
        
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit(); sys.exit()
            if ev.type == MOUSEBUTTONDOWN:
                if btn_slide.collidepoint(ev.pos):
                    run_sliding_puzzle()  # original game
                if btn_jigsaw.collidepoint(ev.pos):
                    jigsaw_scene()
                if btn_snake.collidepoint(ev.pos):
                    snake_scene()
                if btn_sudoku.collidepoint(ev.pos):
                    sudoku_scene()

        clock.tick(FPS)

# ------------------ ORIGINAL SLIDING-PUZZLE MAIN -----------
from sliding_puzzle import run_sliding_puzzle

# ------------------ ENTRY POINT ----------------------------
if __name__ == "__main__":
    launcher()