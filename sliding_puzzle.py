import pygame
import os
import random
import shutil
from pygame.locals import *
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Initialize tkinter for file dialog
root = tk.Tk()
root.withdraw()

# Grid options
GRID_OPTIONS = {3: "3x3", 4: "4x4"}
current_grid_size = 3  # Default to 3x3

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650
TILE_SIZE = 600 // current_grid_size
FPS = 60
MAX_VISIBLE_IMAGES = 5
POPUP_COLS = 3

# Ensure assets directories exist
os.makedirs("assets/images", exist_ok=True)
os.makedirs("assets/sounds", exist_ok=True)

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
pygame.display.set_caption("Sliding Puzzle Pro")
clock = pygame.time.Clock()

# Sounds
sound_settings = {
    'slide_sound': True,
    'background_music': False,
    'music_volume': 0.5
}

def get_next_image_number():
    existing = [f for f in os.listdir("assets/images") if f.startswith('image') and f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    nums = []
    for f in existing:
        try:
            nums.append(int(''.join(filter(str.isdigit, f))))
        except:
            pass
    return max(nums) + 1 if nums else 1

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
            next_num = get_next_image_number()
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png']:
                ext = '.jpg'
            new_filename = f"image{next_num}{ext}"
            new_path = os.path.join("assets/images", new_filename)
            shutil.copy(file_path, new_path)
            img = pygame.image.load(new_path)
            img = pygame.transform.scale(img, (600, 600))
            return (new_filename, img)
        except Exception as e:
            print(f"Failed to load/copy uploaded image: {e}")
    return None

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

def load_sound(name):
    try:
        return pygame.mixer.Sound(os.path.join("assets/sounds", name))
    except:
        return None

def toggle_background_music():
    global sound_settings
    sound_settings['background_music'] = not sound_settings['background_music']
    if sound_settings['background_music']:
        try:
            pygame.mixer.music.load(os.path.join("assets/sounds", "background.mp3"))
            pygame.mixer.music.set_volume(sound_settings['music_volume'])
            pygame.mixer.music.play(-1)
        except:
            print("Could not load background music")
            sound_settings['background_music'] = False
    else:
        pygame.mixer.music.stop()

def adjust_music_volume(change):
    global sound_settings
    sound_settings['music_volume'] = max(0.0, min(1.0, sound_settings['music_volume'] + change))
    if sound_settings['background_music']:
        pygame.mixer.music.set_volume(sound_settings['music_volume'])

# Game state
image_data = load_images()
current_image_idx = 0 if image_data else -1
original_image = image_data[current_image_idx][1] if image_data else None
tiles = []
empty_pos = current_grid_size ** 2 - 1
moves = 0
start_time = 0
timer_active = False
show_preview = False
show_settings = False
slide_sound = load_sound("slide.wav")
win_sound = load_sound("win.wav")

def shuffle_tiles(tiles_in):
    shuffled = tiles_in[:-1]
    random.shuffle(shuffled)
    shuffled.append(tiles_in[-1])
    return shuffled

def create_tiles(image):
    global TILE_SIZE  # Ensure TILE_SIZE is updated according to the current grid size
    TILE_SIZE = 600 // current_grid_size  # Update TILE_SIZE dynamically
    tiles_local = []
    
    # Check if the original image is large enough
    if image.get_width() < TILE_SIZE * current_grid_size or image.get_height() < TILE_SIZE * current_grid_size:
        print("Image size is too small for the selected grid size.")
        return []

    for row in range(current_grid_size):
        for col in range(current_grid_size):
            tile_rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tile = image.subsurface(tile_rect)
            tiles_local.append(tile)
    return tiles_local

def reset_game():
    global tiles, empty_pos, moves, start_time, timer_active
    if original_image:
        tiles = create_tiles(original_image)
        tiles = shuffle_tiles(tiles)
        empty_pos = current_grid_size ** 2 - 1
        moves = 0
        start_time = pygame.time.get_ticks()
        timer_active = True

if image_data:
    reset_game()

def move_tile(direction):
    global empty_pos, moves, timer_active
    row, col = empty_pos // current_grid_size, empty_pos % current_grid_size
    new_pos = None

    if direction == "up" and row < current_grid_size - 1:
        new_pos = empty_pos + current_grid_size
    elif direction == "down" and row > 0:
        new_pos = empty_pos - current_grid_size
    elif direction == "left" and col < current_grid_size - 1:
        new_pos = empty_pos + 1
    elif direction == "right" and col > 0:
        new_pos = empty_pos - 1

    if new_pos is not None:
        tiles[empty_pos], tiles[new_pos] = tiles[new_pos], tiles[empty_pos]
        empty_pos = new_pos
        moves += 1
        if slide_sound and sound_settings['slide_sound']:
            slide_sound.play()
        return True
    return False

def is_solved():
    for i in range(len(tiles) - 1):
        expected_tile = original_image.subsurface(
            (i % current_grid_size * TILE_SIZE, i // current_grid_size * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        )
        if tiles[i] != expected_tile:
            return False
    return True

# --- Emoji-aware text rendering ---

def font_has_glyph(fnt, ch: str) -> bool:
    m = fnt.metrics(ch)
    return m is not None and len(m) == 1 and m[0] is not None

def render_text_with_fallback(text: str, primary_font, fallback_font, color):
    glyphs = []
    total_w = 0
    max_h = 0
    for ch in text:
        use_font = primary_font if font_has_glyph(primary_font, ch) else fallback_font
        surf = use_font.render(ch, True, color)
        glyphs.append(surf)
        total_w += surf.get_width()
        max_h = max(max_h, surf.get_height())
    if total_w == 0:
        total_w = 1
    surface = pygame.Surface((total_w, max_h), pygame.SRCALPHA)
    x = 0
    for g in glyphs:
        surface.blit(g, (x, (max_h - g.get_height()) // 2))
        x += g.get_width()
    return surface

# UI

def draw_button(rect, color, text, text_color=TEXT_COLOR, border_radius=10):
    pygame.draw.rect(screen, color, rect, border_radius=border_radius)
    pygame.draw.rect(screen, (200, 200, 200), rect, 2, border_radius=border_radius)

    text_surface = render_text_with_fallback(text, button_font, emoji_font, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)
    return rect

def draw_volume_control(x, y, width, height):
    pygame.draw.rect(screen, (200, 200, 200), (x, y, width, height), border_radius=5)
    volume_width = int(width * sound_settings['music_volume'])
    pygame.draw.rect(screen, ACCENT_2, (x, y, volume_width, height), border_radius=5)

    dec_btn = pygame.Rect(x - 30, y, 25, height)
    draw_button(dec_btn, ACCENT_1, "-")

    inc_btn = pygame.Rect(x + width + 5, y, 25, height)
    draw_button(inc_btn, ACCENT_1, "+")

    vol_text = info_font.render(f"{int(sound_settings['music_volume'] * 100)}%", True, TEXT_COLOR)
    screen.blit(vol_text, (x + width//2 - vol_text.get_width()//2, y + height//2 - vol_text.get_height()//2))

    return dec_btn, inc_btn

def draw_settings():
    settings_panel = pygame.Rect(200, 150, 400, 400)
    pygame.draw.rect(screen, SETTINGS_BG, settings_panel, border_radius=15)
    pygame.draw.rect(screen, (180, 180, 200), settings_panel, 2, border_radius=15)

    title_text = header_font.render("Settings", True, TEXT_COLOR)
    screen.blit(title_text, (400 - title_text.get_width()//2, 170))

    slide_btn = draw_button(
        pygame.Rect(250, 220, 300, 50),
        ACCENT_2 if sound_settings['slide_sound'] else TILE_BG,
        "Slide Sound: ON" if sound_settings['slide_sound'] else "Slide Sound: OFF"
    )

    music_btn = draw_button(
        pygame.Rect(250, 290, 300, 50),
        ACCENT_3 if sound_settings['background_music'] else TILE_BG,
        "Background Music: ON" if sound_settings['background_music'] else "Background Music: OFF"
    )

    # --- Volume bar right under the music button ---
    vol_dec_btn, vol_inc_btn = draw_volume_control(250, 350, 300, 30)

    grid_size_btn = draw_button(
        pygame.Rect(250, 390, 300, 50),
        ACCENT_4,
        f"Switch to {GRID_OPTIONS[3 if current_grid_size == 4 else 4]}"
    )

    quit_btn = draw_button(pygame.Rect(250, 450, 300, 50), ACCENT_4, "Quit Game")

    # Return every button that can be clicked
    return slide_btn, music_btn, vol_dec_btn, vol_inc_btn, grid_size_btn, quit_btn

def draw_sidebar():
    sidebar = pygame.Rect(600, 0, 200, SCREEN_HEIGHT)
    pygame.draw.rect(screen, SIDEBAR, sidebar)

    settings_btn = draw_button(pygame.Rect(610, 10, 180, 45), ACCENT_4, " Settings")

    elapsed = (pygame.time.get_ticks() - start_time) // 1000 if timer_active else 0
    time_text = info_font.render(f"Time: {elapsed}s", True, TEXT_COLOR)
    screen.blit(time_text, (610, 75))

    moves_text = info_font.render(f"Moves: {moves}", True, TEXT_COLOR)
    screen.blit(moves_text, (610, 115))

    y_offset = 155

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
        y_offset += 90
    else:
        show_more_btn = None

    upload_btn = draw_button(pygame.Rect(610, y_offset, 180, 45), ACCENT_3, "Upload Image")
    y_offset += 50

    preview_btn = draw_button(pygame.Rect(610, y_offset, 180, 45), ACCENT_4, "Preview (P)")
    y_offset += 50

    reset_btn = draw_button(pygame.Rect(610, y_offset, 180, 45), ACCENT_1, "Reset Game")
    y_offset += 50

    return button_rects, show_more_btn, upload_btn, preview_btn, reset_btn, settings_btn

def draw_puzzle():
    if show_preview:
        screen.blit(original_image, (0, 0))
        overlay = pygame.Surface((600, 600), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 128))
        screen.blit(overlay, (0, 0))

        preview_text = header_font.render("Preview Mode", True, TEXT_COLOR)
        screen.blit(preview_text, (300 - preview_text.get_width()//2, 300))
    else:
        for i, tile in enumerate(tiles):
            if i != empty_pos:
                row, col = i // current_grid_size, i % current_grid_size
                x, y = col * TILE_SIZE, row * TILE_SIZE

                shadow = pygame.Rect(x + 3, y + 3, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, (200, 200, 200, 100), shadow, border_radius=5)

                tile_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(tile_surface, (255, 255, 255), (0, 0, TILE_SIZE, TILE_SIZE), border_radius=5)
                tile_surface.blit(tile, (0, 0))
                screen.blit(tile_surface, (x, y))

def main():
    global current_image_idx, original_image, show_preview, timer_active, tiles, empty_pos, moves, start_time, image_data, show_settings, current_grid_size

    running = True
    while running:
        screen.fill(BACKGROUND)

        draw_puzzle()

        button_rects, show_more_btn, upload_btn, preview_btn, reset_btn, settings_btn = draw_sidebar()

        if show_settings:
            slide_btn, music_btn, vol_dec_btn, vol_inc_btn, grid_size_btn, quit_btn = draw_settings()
        if is_solved():
            timer_active = False
            if win_sound:
                win_sound.play()

            overlay = pygame.Surface((600, 600), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 150))
            screen.blit(overlay, (0, 0))

            win_text = title_font.render("You Win!", True, ACCENT_1)
            text_shadow = title_font.render("You Win!", True, (255, 255, 255))

            screen.blit(text_shadow, (303 - win_text.get_width()//2, 303 - win_text.get_height()//2))
            screen.blit(win_text, (300 - win_text.get_width()//2, 300 - win_text.get_height()//2))

            stats_text = info_font.render(f"Time: {(pygame.time.get_ticks() - start_time) // 1000}s  Moves: {moves}", True, TEXT_COLOR)
            screen.blit(stats_text, (300 - stats_text.get_width()//2, 370 - stats_text.get_height()//2))

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == KEYDOWN:
                if event.key == K_p:
                    show_preview = not show_preview
                elif event.key in (K_UP, K_DOWN, K_LEFT, K_RIGHT):
                    direction = ["up", "down", "left", "right"][[K_UP, K_DOWN, K_LEFT, K_RIGHT].index(event.key)]
                    move_tile(direction)
                elif event.key == K_r:
                    reset_game()

            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if show_settings:
                    if slide_btn.collidepoint(mouse_pos):
                        sound_settings['slide_sound'] = not sound_settings['slide_sound']
                    elif music_btn.collidepoint(mouse_pos):
                        toggle_background_music()
                    elif vol_dec_btn.collidepoint(mouse_pos):
                        adjust_music_volume(-0.1)
                    elif vol_inc_btn.collidepoint(mouse_pos):
                        adjust_music_volume(0.1)
                    elif grid_size_btn.collidepoint(mouse_pos):
                        current_grid_size = 4 if current_grid_size == 3 else 3
                        reset_game()  # Reset the game with the new grid size
                    elif quit_btn.collidepoint(mouse_pos):
                        running = False
                    else:
                        show_settings = False
                else:
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
                        for i, btn_rect in enumerate(button_rects):
                            if btn_rect.collidepoint(mouse_pos) and i != current_image_idx:
                                current_image_idx = i
                                original_image = image_data[current_image_idx][1]
                                reset_game()
                                break

                        if mouse_pos[0] < 600:
                            clicked_col = mouse_pos[0] // TILE_SIZE
                            clicked_row = mouse_pos[1] // TILE_SIZE
                            clicked_pos = clicked_row * current_grid_size + clicked_col

                            if abs(clicked_pos - empty_pos) == 1 and clicked_pos // current_grid_size == empty_pos // current_grid_size:
                                direction = "left" if clicked_pos > empty_pos else "right"
                                move_tile(direction)
                            elif abs(clicked_pos - empty_pos) == current_grid_size:
                                direction = "up" if clicked_pos > empty_pos else "down"
                                move_tile(direction)

        pygame.display.flip()
        clock.tick(FPS)

def run_sliding_puzzle():
    main()      # launches the sliding puzzle