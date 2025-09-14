import pygame
import os
import random
import math
from pygame.locals import *
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
PUZZLE_AREA_WIDTH  = 800          # was 600
PUZZLE_AREA_HEIGHT = 550          # unchanged
CAROUSEL_HEIGHT    = 90           # was 140
CAROUSEL_Y         = PUZZLE_AREA_HEIGHT          # starts right under the board

SCREEN_WIDTH  = PUZZLE_AREA_WIDTH
SCREEN_HEIGHT = PUZZLE_AREA_HEIGHT + CAROUSEL_HEIGHT


PIECE_SIZE = 100  # Base size for jigsaw pieces
FPS = 60
MAX_VISIBLE_IMAGES = 5
POPUP_COLS = 3
# --- Carousel layout ---
THUMB_SIZE   = 70          # size of one thumbnail
THUMB_GAP    = 10          # gap between thumbnails
STEP         = THUMB_SIZE + THUMB_GAP

# Colors
BACKGROUND = (249, 246, 239)
SIDEBAR = (230, 230, 250)
TILE_BG = (255, 255, 255)
ACCENT_1 = (255, 182, 193)
ACCENT_2 = (176, 224, 230)
ACCENT_3 = (255, 250, 141)
ACCENT_4 = (197, 176, 205)
SETTINGS_BG = (220, 220, 240)
TEXT_COLOR = (70, 70, 70)
HIGHLIGHT = (152, 251, 152)
CORRECT_COLOR = (144, 238, 144, 150)  # Light green with transparency
CAROUSEL_BG = (220, 220, 220)

# Fonts
def safe_load_fonts():
    try:
        title = pygame.font.Font("assets/fonts/cute.ttf", 60)
        header = pygame.font.Font("assets/fonts/cute.ttf", 36)
        button = pygame.font.Font("assets/fonts/cute.ttf", 28)
        info = pygame.font.Font("assets/fonts/cute.ttf", 32)
        small = pygame.font.Font("assets/fonts/cute.ttf", 22)
    except:
        title = pygame.font.Font(None, 60)
        header = pygame.font.Font(None, 36)
        button = pygame.font.Font(None, 28)
        info = pygame.font.Font(None, 32)
        small = pygame.font.Font(None, 22)

    emoji = pygame.font.SysFont("Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji", 28)
    return title, header, button, info, small, emoji

title_font, header_font, button_font, info_font, show_more, emoji_font = safe_load_fonts()

# Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jigsaw Puzzle")
clock = pygame.time.Clock()

# Game state
image_data = []
current_image_idx = -1
original_image = None
pieces = []
placed_pieces = []  # Pieces placed on the puzzle board
carousel_pieces = []  # Pieces in the carousel
selected_piece = None
offset_x, offset_y = 0, 0
show_preview = False
show_settings = False
carousel_scroll = 0
sound_settings = {
    'piece_sound': True,
    'background_music': False,
    'music_volume': 0.5
}
game_time = 0  # Timer for the game

# Sounds
correct_piece_sound = pygame.mixer.Sound("assets/sounds/right.mp3")
win_sound = pygame.mixer.Sound("assets/sounds/winning.mp3")  # Load winning sound
win_sound_played = False  # Flag to prevent win sound from repeating
piece_sound = pygame.mixer.Sound("assets/sounds/right.mp3")

def load_images():
    try:
        image_files = [f for f in os.listdir("assets/images") if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    except FileNotFoundError:
        image_files = []
    images = []
    for file in image_files:
        try:
            img = pygame.image.load(os.path.join("assets/images", file))
            img = pygame.transform.scale(img, (600, 600))
            images.append((file, img))
        except:
            print(f"Failed to load: {file}")
    if not images:
        fallback = pygame.Surface((600, 600))
        fallback.fill(ACCENT_2)
        pygame.draw.rect(fallback, TILE_BG, (50, 50, 500, 500))
        images.append(("fallback.png", fallback))
    return images

def upload_image():
    file_path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    if file_path:
        try:
            next_num = len(image_data) + 1
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png']:
                ext = '.jpg'
            new_filename = f"image{next_num}{ext}"
            new_path = os.path.join("assets/images", new_filename)
            
            # Use PIL to resize and save the image
            pil_img = Image.open(file_path)
            pil_img = pil_img.resize((600, 600))
            pil_img.save(new_path)
            
            img = pygame.image.load(new_path)
            return (new_filename, img)
        except Exception as e:
            print(f"Failed to load/copy uploaded image: {e}")
    return None

def create_jigsaw_pieces(image):
    pieces = []
    rows = 4
    cols = 4
    piece_width = image.get_width() // cols
    piece_height = image.get_height() // rows
    
    for row in range(rows):
        for col in range(cols):
            piece_rect = pygame.Rect(col * piece_width, row * piece_height, piece_width, piece_height)
            piece = image.subsurface(piece_rect).copy()
            
            # Ensure pieces are shown properly
            piece.set_colorkey((0, 0, 0))  # Set black as transparent

            if row > 0 or col > 0:  # Skip first piece (top-left corner)
                if random.random() > 0.5 and col > 0:
                    tab_pos = random.randint(int(piece_height*0.2), int(piece_height*0.8))
                    pygame.draw.circle(piece, (0, 0, 0), (0, tab_pos), 15)
                if random.random() > 0.5 and row > 0:
                    tab_pos = random.randint(int(piece_width*0.2), int(piece_width*0.8))
                    pygame.draw.circle(piece, (0, 0, 0), (tab_pos, 0), 15)
            
            piece_info = {
                'image': piece,
                'rect': pygame.Rect(0, 0, piece_width, piece_height),
                'target_pos': (col * piece_width, row * piece_height),
                'current_pos': (0, 0),
                'size': (piece_width, piece_height),
                'correct': False,
                'id': row * cols + col
            }
            pieces.append(piece_info)
    
    return pieces

def reset_game():
    global pieces, placed_pieces, carousel_pieces, selected_piece, carousel_scroll, game_time, win_sound_played, start_time    
    win_sound_played = False
    game_time = 0  # Reset timer to 0
    start_time = pygame.time.get_ticks()      # <─ restart the timer

    if original_image:
        all_pieces = create_jigsaw_pieces(original_image)
        carousel_pieces = all_pieces.copy()
        placed_pieces = []
        
        for i, piece in enumerate(carousel_pieces):
            piece['current_pos'] = (50 + i * 110, SCREEN_HEIGHT - 120)
            piece['display_size'] = (100, 100)
        
        selected_piece = None
        carousel_scroll = 0

def draw_button(rect, color, text, text_color=TEXT_COLOR, border_radius=10):
    pygame.draw.rect(screen, color, rect, border_radius=border_radius)
    pygame.draw.rect(screen, (200, 200, 200), rect, 2, border_radius=border_radius)

    text_surface = button_font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)
    return rect


def draw_carousel():
    carousel_rect = pygame.Rect(0, CAROUSEL_Y +10,
                                PUZZLE_AREA_WIDTH, CAROUSEL_HEIGHT)
    pygame.draw.rect(screen, CAROUSEL_BG, carousel_rect)
    pygame.draw.rect(screen, (180, 180, 180), carousel_rect, 2)

    piece_thumb_size = 70                                    # smaller thumbnails
    gap = 10
    for i, piece in enumerate(carousel_pieces):
        if piece in placed_pieces:
            continue
        x_pos = gap + i * (piece_thumb_size + gap) - carousel_scroll
        if -piece_thumb_size < x_pos < PUZZLE_AREA_WIDTH:
            thumb = pygame.transform.scale(piece['image'],
                                           (piece_thumb_size, piece_thumb_size))
            screen.blit(thumb, (x_pos, CAROUSEL_Y + 10))
            border = pygame.Rect(x_pos, CAROUSEL_Y + 10,
                                 piece_thumb_size, piece_thumb_size)
            pygame.draw.rect(screen, (100, 100, 100), border, 2)
            piece['current_pos'] = (x_pos, CAROUSEL_Y + 10)
            piece['display_size'] = (piece_thumb_size, piece_thumb_size)

    # --- Arrow buttons inside the carousel ---
    btn_size = 30
    left_btn  = pygame.Rect(10,  CAROUSEL_Y + CAROUSEL_HEIGHT//2 - btn_size//2,btn_size, btn_size)
    right_btn = pygame.Rect(PUZZLE_AREA_WIDTH - btn_size - 10,CAROUSEL_Y + CAROUSEL_HEIGHT//2 - btn_size//2,btn_size, btn_size)
    pygame.draw.rect(screen, ACCENT_1, left_btn)
    pygame.draw.rect(screen, ACCENT_1, right_btn)
    for (btn, txt) in [(left_btn, "<"), (right_btn, ">")]:
        label = button_font.render(txt, True, TEXT_COLOR)
        screen.blit(label, (btn.centerx - label.get_width()//2,
                            btn.centery - label.get_height()//2))

def draw_puzzle():
    if show_preview:
        screen.blit(original_image, (0, 0))
        overlay = pygame.Surface((600, 600), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 128))
        screen.blit(overlay, (0, 0))

        preview_text = header_font.render("Preview Mode", True, TEXT_COLOR)
        screen.blit(preview_text, (300 - preview_text.get_width()//2, 300))
    else:
        pygame.draw.rect(screen, (240, 240, 240), (0, 0, 600, 600))
        
        for piece in carousel_pieces:
            if piece in placed_pieces:
                continue
                
            slot_rect = pygame.Rect(
                piece['target_pos'][0], piece['target_pos'][1],
                piece['size'][0], piece['size'][1]
            )
            pygame.draw.rect(screen, (220, 220, 220), slot_rect)
            pygame.draw.rect(screen, (180, 180, 180), slot_rect, 2)
        
        for piece in placed_pieces:
            if piece['correct']:
                highlight = pygame.Surface(piece['size'], pygame.SRCALPHA)
                highlight.fill(CORRECT_COLOR)
                screen.blit(highlight, piece['target_pos'])
            
            screen.blit(piece['image'], piece['target_pos'])
            
            border_color = (50, 200, 50) if piece['correct'] else (100, 100, 100)
            border_rect = pygame.Rect(
                piece['target_pos'][0], piece['target_pos'][1],
                piece['size'][0], piece['size'][1]
            )
            pygame.draw.rect(screen, border_color, border_rect, 2)
        
        if selected_piece and selected_piece not in placed_pieces:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(
                selected_piece['image'],
                (mouse_x - offset_x, mouse_y - offset_y)
            )
            border_rect = pygame.Rect(
                mouse_x - offset_x, mouse_y - offset_y,
                selected_piece['size'][0], selected_piece['size'][1]
            )
            pygame.draw.rect(screen, (200, 200, 0), border_rect, 2)

def check_piece_position(piece, mouse_pos):
    target_x, target_y = piece['target_pos']
    piece_x, piece_y = mouse_pos[0] - offset_x, mouse_pos[1] - offset_y
    distance = math.sqrt((target_x - piece_x)**2 + (target_y - piece_y)**2)

    if distance < 50:
        piece['correct'] = True
        placed_pieces.append(piece)
        if piece in carousel_pieces:
            carousel_pieces.remove(piece)
        if piece_sound and sound_settings['piece_sound']:
            piece_sound.play()
        if sound_settings['piece_sound']:  # Play the correct sound
            correct_piece_sound.play()
        return True
    return False



def select_image(index, image_list, popup):
    global current_image_idx, original_image
    current_image_idx = index
    original_image = image_list[current_image_idx][1]
    reset_game()
    popup.destroy()

def is_puzzle_complete():
    return len(placed_pieces) == len(carousel_pieces) + len(placed_pieces)

def show_instructions():
    messagebox.showinfo("Instructions", "To play the game:\n- Click and drag the pieces to move them.\n- Place them in the correct position to complete the puzzle.\n- The timer tracks how long you've been playing.\n- Enjoy the game!")



def show_image_popup():
    popup = tk.Toplevel()
    popup.title("Select Image")
    popup.geometry("500x500")
    popup.resizable(False, False)

    # Center the popup on the main window
    popup_width = 500
    popup_height = 500
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x = (screen_width - popup_width) // 2
    y = (screen_height - popup_height) // 2
    popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

    # Scrollable frame
    canvas = tk.Canvas(popup, highlightthickness=0)
    scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    THUMB_SIZE = 150
    for idx, (filename, _) in enumerate(image_data):
        col = idx % POPUP_COLS
        if col == 0:
            row_frame = tk.Frame(scrollable_frame)
            row_frame.pack()

        img_path = os.path.join("assets/images", filename)
        try:
            pil_img = Image.open(img_path).convert("RGBA")

            # Fill square, keep aspect
            pil_img.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
            square = Image.new("RGBA", (THUMB_SIZE, THUMB_SIZE), (255, 255, 255, 255))
            offset = ((THUMB_SIZE - pil_img.width) // 2,
                      (THUMB_SIZE - pil_img.height) // 2)
            square.paste(pil_img, offset, pil_img)

            photo = ImageTk.PhotoImage(square)

            btn = tk.Label(row_frame, image=photo, bd=2, relief="solid")
            btn.image = photo  # Keep reference
            btn.grid(row=0, column=col, padx=5, pady=5)
            btn.bind("<Button-1>", lambda e, i=idx: select_image(i))

            label = tk.Label(row_frame, text=os.path.splitext(filename)[0][:10])
            label.grid(row=1, column=col, padx=5, pady=5)
        except Exception as e:
            print(f"Thumbnail error for {filename}: {e}")

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def select_image(idx):
        global current_image_idx, original_image
        current_image_idx = idx
        original_image = image_data[current_image_idx][1]
        reset_game()
        popup.destroy()

    popup.wait_window()

def draw_sidebar():
    sidebar = pygame.Rect(600, 0, 200, SCREEN_HEIGHT)
    pygame.draw.rect(screen, SIDEBAR, sidebar)

    settings_btn = draw_button(pygame.Rect(610, 10, 180, 45), ACCENT_4, "Settings")

    # Draw timer
    timer_text = info_font.render(f"Time: {game_time // 60}:{game_time % 60:02}", True, TEXT_COLOR)
    screen.blit(timer_text, (610, 75))

    y_offset = 105
    button_rects = []
    visible_images = min(MAX_VISIBLE_IMAGES, len(image_data))
    for i in range(visible_images):
        filename, _ = image_data[i]
        btn_rect = pygame.Rect(610, y_offset, 180, 40)
        btn_color = HIGHLIGHT if i == current_image_idx else TILE_BG
        display_text = os.path.splitext(filename)[0][:12]
        btn = draw_button(btn_rect, btn_color, display_text)
        button_rects.append(btn)
        y_offset += 50

    if len(image_data) > MAX_VISIBLE_IMAGES:
        show_more_text = show_more.render("Show more", True, TEXT_COLOR)
        screen.blit(show_more_text, (660, y_offset + 5))
        show_more_btn = pygame.Rect(610, y_offset, 180, 45)
        y_offset += 40
    else:
        show_more_btn = None

    upload_btn = draw_button(pygame.Rect(610, y_offset, 180, 45), ACCENT_3, "Upload Image")
    y_offset += 50

    preview_btn = draw_button(pygame.Rect(610, y_offset, 180, 45), ACCENT_4, "Preview (P)")
    y_offset += 50

    reset_btn = draw_button(pygame.Rect(610, y_offset, 180, 45), ACCENT_1, "Reset Game")
    y_offset += 50

    return button_rects, show_more_btn, upload_btn, preview_btn, reset_btn, settings_btn


def run_jigsaw():
    global image_data, current_image_idx, original_image, show_preview, \
           show_settings, selected_piece, offset_x, offset_y, carousel_scroll, \
           game_time, win_sound_played, start_time
    
    start_time = pygame.time.get_ticks()   # <-- add this


    if not image_data:
        image_data = load_images()
        if image_data:
            current_image_idx = 0
            original_image = image_data[current_image_idx][1]
            reset_game()

    running = True
    start_time = pygame.time.get_ticks()

    # --- Arrow-button rectangles (fixed positions) ---
    btn_size = 30
    left_button_rect  = pygame.Rect(10,
                                    CAROUSEL_Y + CAROUSEL_HEIGHT // 2 - btn_size // 2,
                                    btn_size, btn_size)
    right_button_rect = pygame.Rect(PUZZLE_AREA_WIDTH - btn_size - 10,
                                    CAROUSEL_Y + CAROUSEL_HEIGHT // 2 - btn_size // 2,
                                    btn_size, btn_size)

    while running:
        screen.fill(BACKGROUND)
        elapsed = (pygame.time.get_ticks() - start_time) // 1000
        game_time = elapsed
        # 1. Sidebar (drawn first)
        button_rects, show_more_btn, upload_btn, preview_btn, reset_btn, settings_btn = draw_sidebar()


        # 2. Puzzle board
        draw_puzzle()

        # 3. Carousel (drawn last so arrows stay on top)
        draw_carousel()

        if not is_puzzle_complete():
            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
            game_time = elapsed_time
        # --- Settings panel (if open) ---
        if show_settings:
            settings_panel = pygame.Rect(200, 150, 400, 300)
            pygame.draw.rect(screen, SETTINGS_BG, settings_panel, border_radius=15)
            pygame.draw.rect(screen, (180, 180, 200), settings_panel, 2, border_radius=15)

            title_text = header_font.render("Settings", True, TEXT_COLOR)
            screen.blit(title_text, (400 - title_text.get_width() // 2, 170))

            piece_btn = draw_button(
                pygame.Rect(250, 220, 300, 50),
                ACCENT_2 if sound_settings['piece_sound'] else TILE_BG,
                "Piece Sound: ON" if sound_settings['piece_sound'] else "Piece Sound: OFF"
            )
            quit_btn = draw_button(pygame.Rect(250, 280, 300, 50), ACCENT_4, "Quit Game")

        # --- Win overlay ---
        if is_puzzle_complete():
            overlay = pygame.Surface((600, 600), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 150))
            screen.blit(overlay, (0, 0))

            win_text = title_font.render("Puzzle Complete!", True, ACCENT_1)
            text_shadow = title_font.render("Puzzle Complete!", True, (255, 255, 255))
            screen.blit(text_shadow, (303 - win_text.get_width() // 2,
                                      303 - win_text.get_height() // 2))
            screen.blit(win_text, (300 - win_text.get_width() // 2,
                                   300 - win_text.get_height() // 2))

            if not win_sound_played and sound_settings['piece_sound']:
                win_sound.play()
                win_sound_played = True

        # ------------------------------------------------------------------
        # EVENT LOOP
        # ------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == KEYDOWN:
                if event.key == K_p:
                    show_preview = not show_preview
                elif event.key == K_r:
                    reset_game()
                elif event.key == K_LEFT:
                    carousel_scroll = max(0, carousel_scroll - STEP)
                elif event.key == K_RIGHT:
                    max_scroll = max(0, len(carousel_pieces) * STEP - PUZZLE_AREA_WIDTH)
                    carousel_scroll = min(max_scroll, carousel_scroll + STEP)
                elif event.key == K_h:
                    show_instructions()

            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Carousel arrow clicks
                if left_button_rect.collidepoint(mouse_pos):
                    carousel_scroll = max(0, carousel_scroll - STEP)
                elif right_button_rect.collidepoint(mouse_pos):
                    max_scroll = max(0, len(carousel_pieces) * STEP  - PUZZLE_AREA_WIDTH)
                    carousel_scroll = min(max_scroll, carousel_scroll + STEP)

                # Settings panel clicks
                if show_settings:
                    if piece_btn.collidepoint(mouse_pos):
                        sound_settings['piece_sound'] = not sound_settings['piece_sound']
                    elif quit_btn.collidepoint(mouse_pos):
                        running = False
                    else:
                        show_settings = False
                else:
                    # Sidebar button clicks
                    if settings_btn.collidepoint(mouse_pos):
                        show_settings = True
                    elif preview_btn.collidepoint(mouse_pos):
                        show_preview = not show_preview
                    elif reset_btn.collidepoint(mouse_pos):
                        reset_game()
                    elif upload_btn.collidepoint(mouse_pos):
                        uploaded = upload_image()
                        if uploaded:
                            image_data.append(uploaded)
                            current_image_idx = len(image_data) - 1
                            original_image = image_data[current_image_idx][1]
                            reset_game()
                    elif show_more_btn and show_more_btn.collidepoint(mouse_pos):
                        show_image_popup()
                    else:
                        # Image-selection buttons
                        for i, btn_rect in enumerate(button_rects):
                            if btn_rect.collidepoint(mouse_pos) and i != current_image_idx:
                                current_image_idx = i
                                original_image = image_data[current_image_idx][1]
                                reset_game()
                                break

                        # Carousel piece pick-up
                        if mouse_pos[1] > CAROUSEL_Y:
                            for piece in carousel_pieces:
                                if piece in placed_pieces:
                                    continue
                                piece_rect = pygame.Rect(
                                    piece['current_pos'][0],
                                    piece['current_pos'][1],
                                    piece['display_size'][0],
                                    piece['display_size'][1]
                                )
                                if piece_rect.collidepoint(mouse_pos):
                                    selected_piece = piece
                                    offset_x = mouse_pos[0] - piece['current_pos'][0]
                                    offset_y = mouse_pos[1] - piece['current_pos'][1]
                                    break

            elif event.type == MOUSEBUTTONUP:
                if selected_piece and selected_piece not in placed_pieces:
                    mouse_pos = pygame.mouse.get_pos()
                    if mouse_pos[1] < CAROUSEL_Y:
                        check_piece_position(selected_piece, mouse_pos)
                    selected_piece = None

            elif event.type == MOUSEMOTION:
                if event.buttons[2]:  # right-drag to scroll
                    carousel_scroll = max(0,
                                          min(len(carousel_pieces) * STEP - PUZZLE_AREA_WIDTH,
                                              carousel_scroll - event.rel[0]))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.mixer.music.stop()

if __name__ == "__main__":
    run_jigsaw()