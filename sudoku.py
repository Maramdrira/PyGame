# -----------------------------------------------------------
#  sudoku.py  (Sudoku game implementation)
# -----------------------------------------------------------
import pygame
import random
import time
from pygame.locals import *

# ------------------ SUDOKU GENERATION ----------------------
def generate_sudoku(difficulty=0.5):
    """
    Generates a valid Sudoku puzzle with the specified difficulty.
    Difficulty is a value between 0 and 1, where higher values mean more empty cells.
    """
    # Create a solved Sudoku board
    base = 3
    side = base * base

    # Pattern for a baseline valid solution
    def pattern(r, c): 
        return (base * (r % base) + r // base + c) % side

    # Randomize rows, columns and numbers (of valid base pattern)
    def shuffle(s): 
        return random.sample(s, len(s))
    
    rBase = range(base)
    rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
    cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
    nums = shuffle(range(1, base * base + 1))

    # Produce board using randomized baseline pattern
    board = [[nums[pattern(r, c)] for c in cols] for r in rows]
    
    # Create puzzle by removing numbers based on difficulty
    squares = side * side
    empties = int(squares * difficulty)
    for p in random.sample(range(squares), empties):
        board[p // side][p % side] = 0
        
    return board

# ------------------ SUDOKU VALIDATION ----------------------
def is_valid_move(board, row, col, num):
    """
    Checks if placing a number at the given position is valid according to Sudoku rules.
    """
    # Check row - no duplicate numbers in the same row
    for x in range(9):
        if board[row][x] == num:
            return False

    # Check column - no duplicate numbers in the same column
    for x in range(9):
        if board[x][col] == num:
            return False

    # Check 3x3 box - no duplicate numbers in the same 3x3 box
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
                
    return True

def is_board_complete(board):
    """
    Checks if the board is completely filled (no zeros).
    """
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return False
    return True

# ------------------ SUDOKU GAME CLASS ----------------------
class SudokuGame:
    def __init__(self, difficulty=0.5):
        """
        Initializes a new Sudoku game with the specified difficulty.
        """
        # Generate a new puzzle
        self.board = generate_sudoku(difficulty)
        # Keep a copy of the original puzzle to distinguish between given and player numbers
        self.original = [[cell for cell in row] for row in self.board]
        # Currently selected cell (row, col)
        self.selected = None
        # Size of each cell in pixels
        self.cell_size = 50
        # Total size of the grid (9 cells * cell_size)
        self.grid_size = self.cell_size * 9
        # X offset to center the grid horizontally
        self.offset_x = (800 - self.grid_size) // 2
        # Y offset to position the grid vertically
        self.offset_y = 150
        
    def draw(self, screen, font, small_font):
        """
        Draws the entire Sudoku game board, numbers, and grid lines.
        """
        # Draw grid background with a white color
        pygame.draw.rect(screen, (255, 255, 255), 
                         (self.offset_x, self.offset_y, self.grid_size, self.grid_size))
        
        # Draw subtle background colors for each 3x3 box to distinguish them
        for box_row in range(3):
            for box_col in range(3):
                # Alternate colors for adjacent boxes for better visual distinction
                box_color = (245, 250, 255) if (box_row + box_col) % 2 == 0 else (250, 250, 245)
                box_rect = pygame.Rect(
                    self.offset_x + box_col * 3 * self.cell_size,
                    self.offset_y + box_row * 3 * self.cell_size,
                    3 * self.cell_size, 3 * self.cell_size
                )
                pygame.draw.rect(screen, box_color, box_rect)
        
        # Draw grid lines with different styles for cell borders and 3x3 box borders
        for i in range(10):
            # Thicker lines for 3x3 box borders, thinner for cell borders
            line_width = 4 if i % 3 == 0 else 2
            # Different colors for box borders vs cell borders
            line_color = (120, 120, 150) if i % 3 == 0 else (180, 180, 200)
            
            # Draw horizontal grid lines
            pygame.draw.line(screen, line_color, 
                            (self.offset_x, self.offset_y + i * self.cell_size),
                            (self.offset_x + self.grid_size, self.offset_y + i * self.cell_size), 
                            line_width)
            # Draw vertical grid lines
            pygame.draw.line(screen, line_color, 
                            (self.offset_x + i * self.cell_size, self.offset_y),
                            (self.offset_x + i * self.cell_size, self.offset_y + self.grid_size), 
                            line_width)
        
        # Draw numbers and cell backgrounds
        for row in range(9):
            for col in range(9):
                # Draw cell background for original numbers (pre-filled)
                if self.original[row][col] != 0:
                    cell_rect = pygame.Rect(
                        self.offset_x + col * self.cell_size,
                        self.offset_y + row * self.cell_size,
                        self.cell_size, self.cell_size
                    )
                    pygame.draw.rect(screen, (235, 245, 255), cell_rect)
                
                # Draw number if not zero (empty cell)
                if self.board[row][col] != 0:
                    # Different colors for original numbers vs player-placed numbers
                    if self.original[row][col] != 0:
                        num_color = (70, 70, 120)  # Dark blue for original numbers
                    else:
                        num_color = (0, 100, 0)  # Dark green for player numbers
                    
                    # Render the number text
                    num_text = font.render(str(self.board[row][col]), True, num_color)
                    
                    # Calculate centered position for the number
                    text_x = self.offset_x + col * self.cell_size + (self.cell_size - num_text.get_width()) // 2
                    text_y = self.offset_y + row * self.cell_size + (self.cell_size - num_text.get_height()) // 2
                    
                    # Draw the number centered in the cell
                    screen.blit(num_text, (text_x, text_y))
        
        # Draw soft borders around each 3x3 box to make them more distinct
        for i in range(4):  # 4 lines needed to create 3 boxes in each direction
            # Draw thicker, softer colored borders around each 3x3 box
            border_width = 6
            border_color = (200, 210, 230)
            
            # Horizontal borders
            pygame.draw.rect(screen, border_color, 
                            (self.offset_x, self.offset_y + i * 3 * self.cell_size - border_width//2,
                             self.grid_size, border_width))
            
            # Vertical borders
            pygame.draw.rect(screen, border_color, 
                            (self.offset_x + i * 3 * self.cell_size - border_width//2, self.offset_y,
                             border_width, self.grid_size))
        
        # Highlight selected cell with a different color
        if self.selected:
            row, col = self.selected
            highlight_rect = pygame.Rect(
                self.offset_x + col * self.cell_size, 
                self.offset_y + row * self.cell_size, 
                self.cell_size, self.cell_size
            )
            pygame.draw.rect(screen, (255, 220, 180), highlight_rect, 4)
    
    def handle_click(self, pos):
        """
        Handles mouse clicks on the Sudoku grid.
        Returns True if a valid cell was clicked, False otherwise.
        """
        x, y = pos
        # Check if click is within the grid boundaries
        if (self.offset_x <= x <= self.offset_x + self.grid_size and 
            self.offset_y <= y <= self.offset_y + self.grid_size):
            # Calculate which cell was clicked
            col = (x - self.offset_x) // self.cell_size
            row = (y - self.offset_y) // self.cell_size
            
            # Only allow selection of empty cells (not original numbers)
            if 0 <= row < 9 and 0 <= col < 9 and self.original[row][col] == 0:
                self.selected = (row, col)
                return True
        
        # If click was outside grid or on an original number, deselect
        self.selected = None
        return False
    
    def place_number(self, num):
        """
        Places a number in the selected cell.
        Returns True if successful, False otherwise.
        """
        if self.selected:
            row, col = self.selected
            # Only allow changing empty cells (not original numbers)
            if self.original[row][col] == 0:
                self.board[row][col] = num
                return True
        return False
    
    def check_solution(self):
        """
        Checks the current solution for errors.
        Returns a list of coordinates for incorrect cells.
        """
        incorrect_cells = []
        
        # Check rows for duplicates
        for row in range(9):
            seen = set()
            for col in range(9):
                num = self.board[row][col]
                if num != 0:
                    if num in seen:
                        incorrect_cells.append((row, col))
                    seen.add(num)
        
        # Check columns for duplicates
        for col in range(9):
            seen = set()
            for row in range(9):
                num = self.board[row][col]
                if num != 0:
                    if num in seen:
                        incorrect_cells.append((row, col))
                    seen.add(num)
        
        # Check 3x3 boxes for duplicates
        for box_row in range(3):
            for box_col in range(3):
                seen = set()
                for i in range(3):
                    for j in range(3):
                        row = box_row * 3 + i
                        col = box_col * 3 + j
                        num = self.board[row][col]
                        if num != 0:
                            if num in seen:
                                incorrect_cells.append((row, col))
                            seen.add(num)
        
        # Remove duplicates from the list
        incorrect_cells = list(set(incorrect_cells))
        
        # Also check if any cell violates the rules individually
        for row in range(9):
            for col in range(9):
                if self.board[row][col] != 0:
                    num = self.board[row][col]
                    # Temporarily remove the number to check if it's valid
                    self.board[row][col] = 0
                    if not is_valid_move(self.board, row, col, num):
                        incorrect_cells.append((row, col))
                    # Put the number back
                    self.board[row][col] = num
        
        return incorrect_cells

# ------------------ SUDOKU MAIN FUNCTION -------------------
def run_sudoku():
    """
    Main function to run the Sudoku game.
    Handles the game loop, user input, and rendering.
    """
    pygame.init()
    # Set up the display window (same size as main menu)
    screen = pygame.display.set_mode((800, 650))
    pygame.display.set_caption("Sudoku")
    clock = pygame.time.Clock()
    
    # Load fonts with fallback to system fonts if custom font isn't available
    try:
        font = pygame.font.Font("assets/fonts/cute.ttf", 36)
        small_font = pygame.font.Font("assets/fonts/cute.ttf", 24)
        title_font = pygame.font.Font("assets/fonts/cute.ttf", 40)
    except:
        font = pygame.font.SysFont("comicsansms", 36)
        small_font = pygame.font.SysFont("comicsansms", 24)
        title_font = pygame.font.SysFont("comicsansms", 40)
    
    # Create a new Sudoku game with medium difficulty
    game = SudokuGame(difficulty=0.5)
    
    # Define button positions and sizes
    new_game_btn = pygame.Rect(50, 80, 120, 40)
    check_btn = pygame.Rect(200, 80, 120, 40)
    solve_btn = pygame.Rect(350, 80, 120, 40)
    back_btn = pygame.Rect(630, 80, 150, 40)
    
    # Initialize game state variables
    start_time = time.time()  # For the timer
    running = True
    message = ""
    message_timer = 0
    incorrect_cells = []
    showing_solution = False
    
    # Main game loop
    while running:
        # Fill the screen with the background color
        screen.fill((249, 246, 239))
        
        # Calculate and format elapsed time
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        # Draw the game title
        title = title_font.render("Sudoku Puzzle", True, (90, 90, 140))
        screen.blit(title, (400 - title.get_width()//2, 30))
        
        # Draw the timer in the top right corner
        timer_text = small_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, (100, 100, 100))
        screen.blit(timer_text, (650, 30))
        
        # Draw the Sudoku grid and numbers
        game.draw(screen, font, small_font)
        
        # Highlight incorrect cells if we're showing the solution
        if showing_solution:
            for row, col in incorrect_cells:
                # Draw a red background for incorrect cells
                cell_rect = pygame.Rect(
                    game.offset_x + col * game.cell_size,
                    game.offset_y + row * game.cell_size,
                    game.cell_size, game.cell_size
                )
                pygame.draw.rect(screen, (255, 200, 200), cell_rect)
                
                # Redraw the number in red to indicate it's incorrect
                if game.board[row][col] != 0:
                    num_text = font.render(str(game.board[row][col]), True, (220, 0, 0))
                    # Center the number in the cell
                    text_x = game.offset_x + col * game.cell_size + (game.cell_size - num_text.get_width()) // 2
                    text_y = game.offset_y + row * game.cell_size + (game.cell_size - num_text.get_height()) // 2
                    screen.blit(num_text, (text_x, text_y))
        
        # Draw buttons with nice colors
        button_colors = [
            (180, 230, 180),  # New Game - Light green
            (180, 200, 230),  # Check - Light blue
            (230, 200, 180),  # Solve - Light orange
            (220, 220, 220)   # Back - Light gray
        ]
        
        buttons = [new_game_btn, check_btn, solve_btn, back_btn]
        button_texts = ["New Game", "Check", "Solve", "Back to Menu"]
        
        for i, (btn, text) in enumerate(zip(buttons, button_texts)):
            # Draw button background
            pygame.draw.rect(screen, button_colors[i], btn, border_radius=8)
            # Draw button border
            pygame.draw.rect(screen, (150, 150, 150), btn, 2, border_radius=8)
            
            # Draw button text
            btn_text = small_font.render(text, True, (50, 50, 50))
            screen.blit(btn_text, (btn.centerx - btn_text.get_width()//2, 
                                  btn.centery - btn_text.get_height()//2))
        
        # Draw message with a colored background if there is one to display
        if message and message_timer > 0:
            # Create a background for the message
            msg_bg = pygame.Rect(300 - small_font.size(message)[0]//2 - 10, 
                                590, small_font.size(message)[0] + 20, 30)
            pygame.draw.rect(screen, (240, 240, 240), msg_bg, border_radius=5)
            pygame.draw.rect(screen, (200, 200, 200), msg_bg, 2, border_radius=5)
            
            # Draw the message text
            msg_text = small_font.render(message, True, (70, 70, 70))
            screen.blit(msg_text, (400 - msg_text.get_width()//2, 595))
            message_timer -= 1
        
        # Update the display
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                # Handle button clicks
                if new_game_btn.collidepoint(pos):
                    # Start a new game
                    game = SudokuGame(difficulty=0.5)
                    start_time = time.time()  # Reset timer
                    message = "New game started!"
                    message_timer = 60
                    incorrect_cells = []
                    showing_solution = False
                    
                elif check_btn.collidepoint(pos):
                    # Check the current solution
                    if is_board_complete(game.board):
                        incorrect_cells = game.check_solution()
                        if not incorrect_cells:
                            message = "Congratulations! Puzzle solved correctly!"
                            showing_solution = False
                        else:
                            message = f"Found {len(incorrect_cells)} incorrect cells!"
                            showing_solution = True
                    else:
                        message = "Puzzle is not complete yet!"
                    message_timer = 60
                    
                elif solve_btn.collidepoint(pos):
                    # Show all incorrect cells
                    incorrect_cells = game.check_solution()
                    message = f"Found {len(incorrect_cells)} incorrect cells!"
                    message_timer = 60
                    showing_solution = True
                    
                elif back_btn.collidepoint(pos):
                    # Return to main menu
                    running = False
                    
                else:
                    # Handle grid clicks
                    game.handle_click(pos)
            
            if event.type == KEYDOWN:
                # Handle keyboard input
                if event.key == K_ESCAPE:
                    running = False
                elif event.key in (K_1, K_KP1):
                    game.place_number(1)
                elif event.key in (K_2, K_KP2):
                    game.place_number(2)
                elif event.key in (K_3, K_KP3):
                    game.place_number(3)
                elif event.key in (K_4, K_KP4):
                    game.place_number(4)
                elif event.key in (K_5, K_KP5):
                    game.place_number(5)
                elif event.key in (K_6, K_KP6):
                    game.place_number(6)
                elif event.key in (K_7, K_KP7):
                    game.place_number(7)
                elif event.key in (K_8, K_KP8):
                    game.place_number(8)
                elif event.key in (K_9, K_KP9):
                    game.place_number(9)
                elif event.key in (K_BACKSPACE, K_DELETE, K_0):
                    game.place_number(0)
        
        # Cap the frame rate
        clock.tick(60)
    
    return