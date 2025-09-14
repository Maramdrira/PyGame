# -----------------------------------------------------------
#  snake.py  (Enhanced Snake game with better visuals)
# -----------------------------------------------------------
import pygame
import random
import sys
import math
from pygame.locals import *

# ------------------ CONSTANTS ------------------------------
SNAKE_CELL_SIZE = 20
SNAKE_GRID_WIDTH = 30  # 30 cells wide
SNAKE_GRID_HEIGHT = 25  # 25 cells tall
SNAKE_GAME_WIDTH = SNAKE_GRID_WIDTH * SNAKE_CELL_SIZE
SNAKE_GAME_HEIGHT = SNAKE_GRID_HEIGHT * SNAKE_CELL_SIZE

SNAKE_SCREEN_WIDTH = 800
SNAKE_SCREEN_HEIGHT = 650

# Colors
SNAKE_BACKGROUND = (40, 44, 52)
SNAKE_GRID_COLOR = (58, 63, 72)
SNAKE_HEAD_COLOR = (46, 204, 113)  # Emerald green
SNAKE_BODY_COLOR = (39, 174, 96)   # Darker green
SNAKE_FOOD_COLOR = (231, 76, 60)   # Red
SNAKE_OBSTACLE_COLOR = (241, 196, 15)  # Sun flower yellow
SNAKE_TEXT_COLOR = (236, 240, 241)  # Clouds white
SNAKE_GAME_OVER_BG = (44, 62, 80, 200)  # Semi-transparent dark blue
SNAKE_ACCENT_COLOR = (52, 152, 219)  # Peter river blue

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# ------------------ SNAKE GAME CLASS -----------------------
class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SNAKE_SCREEN_WIDTH, SNAKE_SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        
        # Load fonts
        self.font = pygame.font.SysFont("Arial", 24)
        self.big_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 72, bold=True)
        
        # Calculate offset to center the game grid
        self.grid_offset_x = (SNAKE_SCREEN_WIDTH - SNAKE_GAME_WIDTH) // 2
        self.grid_offset_y = (SNAKE_SCREEN_HEIGHT - SNAKE_GAME_HEIGHT) // 2
        
        # Visual effects
        self.particles = []
        self.food_pulse = 0
        self.obstacle_glow = 0
        
        # Initialize obstacles list first
        self.obstacles = []
        self.reset_game()
        
    def reset_game(self):
        # Initialize snake in the middle of the grid
        self.snake = [(SNAKE_GRID_WIDTH // 2, SNAKE_GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.obstacles = []  # Reset obstacles
        self.current_obstacle = None
        self.obstacle_timer = 0
        self.obstacle_duration = 10 * 60  # 10 seconds at 60 FPS
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.speed = 10  # Initial speed (frames per movement)
        self.frame_count = 0
        self.particles = []
        
    def generate_food(self):
        while True:
            food = (random.randint(0, SNAKE_GRID_WIDTH - 1), 
                    random.randint(0, SNAKE_GRID_HEIGHT - 1))
            if food not in self.snake and food not in self.obstacles:
                return food
    
    def generate_obstacle(self):
        # Generate a 2x2 obstacle
        while True:
            x = random.randint(0, SNAKE_GRID_WIDTH - 2)
            y = random.randint(0, SNAKE_GRID_HEIGHT - 2)
            
            # Check if the position is free
            positions = [(x, y), (x+1, y), (x, y+1), (x+1, y+1)]
            valid = True
            
            for pos in positions:
                if pos in self.snake or pos == self.food:
                    valid = False
                    break
                    
            if valid:
                return positions
    
    def update_obstacles(self):
        # Only start generating obstacles when score reaches 4
        if self.score < 4:
            return
            
        self.obstacle_timer += 1
        
        # If no current obstacle, create one
        if self.current_obstacle is None:
            self.current_obstacle = self.generate_obstacle()
            self.obstacles = self.current_obstacle
            self.obstacle_timer = 0
            # Create particles for new obstacle
            for pos in self.current_obstacle:
                x = self.grid_offset_x + pos[0] * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2
                y = self.grid_offset_y + pos[1] * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2
                for _ in range(10):
                    self.particles.append({
                        'x': x, 'y': y,
                        'dx': random.uniform(-2, 2),
                        'dy': random.uniform(-2, 2),
                        'color': SNAKE_OBSTACLE_COLOR,
                        'life': random.randint(20, 40)
                    })
        
        # If obstacle has been visible for 10 seconds, remove it
        elif self.obstacle_timer >= self.obstacle_duration:
            self.current_obstacle = None
            self.obstacles = []
            self.obstacle_timer = 0
    
    def create_food_particles(self):
        # Create particles around food
        food_x = self.grid_offset_x + self.food[0] * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2
        food_y = self.grid_offset_y + self.food[1] * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2
        
        for _ in range(3):
            self.particles.append({
                'x': food_x, 'y': food_y,
                'dx': random.uniform(-1, 1),
                'dy': random.uniform(-1, 1),
                'color': SNAKE_FOOD_COLOR,
                'life': random.randint(30, 60)
            })
    
    def update_particles(self):
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self):
        for particle in self.particles:
            alpha = min(255, particle['life'] * 6)
            size = max(1, particle['life'] // 10)
            color = list(particle['color'])
            if len(color) == 3:
                color.append(alpha)
            
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (size, size), size)
            self.screen.blit(s, (particle['x'] - size, particle['y'] - size))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if self.game_over:
                    if event.key == K_r:
                        self.reset_game()
                    elif event.key == K_ESCAPE or event.key == K_q:
                        return False  # Return to menu
                else:
                    if event.key == K_UP and self.direction != DOWN:
                        self.next_direction = UP
                    elif event.key == K_DOWN and self.direction != UP:
                        self.next_direction = DOWN
                    elif event.key == K_LEFT and self.direction != RIGHT:
                        self.next_direction = LEFT
                    elif event.key == K_RIGHT and self.direction != LEFT:
                        self.next_direction = RIGHT
                    elif event.key == K_ESCAPE or event.key == K_q:
                        return False  # Return to menu
        return True
    
    def update(self):
        if self.game_over:
            return
        
        # Update visual effects
        self.food_pulse = (self.food_pulse + 0.1) % (2 * math.pi)
        self.obstacle_glow = (self.obstacle_glow + 0.05) % (2 * math.pi)
        self.update_particles()
        
        # Update obstacles (only if score >= 4)
        self.update_obstacles()
        
        # Update direction
        self.direction = self.next_direction
        
        # Move snake based on frame count and speed
        self.frame_count += 1
        if self.frame_count >= self.speed:
            self.frame_count = 0
            
            # Calculate new head position
            head_x, head_y = self.snake[0]
            dx, dy = self.direction
            new_head = (head_x + dx, head_y + dy)
            
            # Check for collision with walls
            if (new_head[0] < 0 or new_head[0] >= SNAKE_GRID_WIDTH or 
                new_head[1] < 0 or new_head[1] >= SNAKE_GRID_HEIGHT):
                self.game_over = True
                # Create explosion particles
                head_x_px = self.grid_offset_x + head_x * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2
                head_y_px = self.grid_offset_y + head_y * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2
                for _ in range(30):
                    self.particles.append({
                        'x': head_x_px, 'y': head_y_px,
                        'dx': random.uniform(-3, 3),
                        'dy': random.uniform(-3, 3),
                        'color': SNAKE_HEAD_COLOR,
                        'life': random.randint(20, 40)
                    })
                return
            
            # Check for collision with self
            if new_head in self.snake:
                self.game_over = True
                # Create explosion particles
                head_x_px = self.grid_offset_x + head_x * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2
                head_y_px = self.grid_offset_y + head_y * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2
                for _ in range(30):
                    self.particles.append({
                        'x': head_x_px, 'y': head_y_px,
                        'dx': random.uniform(-3, 3),
                        'dy': random.uniform(-3, 3),
                        'color': SNAKE_HEAD_COLOR,
                        'life': random.randint(20, 40)
                    })
                return
                
            # Check for collision with obstacles
            if new_head in self.obstacles:
                self.game_over = True
                # Create explosion particles
                head_x_px = self.grid_offset_x + head_x * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2
                head_y_px = self.grid_offset_y + head_y * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2
                for _ in range(30):
                    self.particles.append({
                        'x': head_x_px, 'y': head_y_px,
                        'dx': random.uniform(-3, 3),
                        'dy': random.uniform(-3, 3),
                        'color': SNAKE_OBSTACLE_COLOR,
                        'life': random.randint(20, 40)
                    })
                return
            
            # Move snake
            self.snake.insert(0, new_head)
            
            # Check for food collision
            if new_head == self.food:
                self.score += 1
                # Create food particles
                food_x = self.grid_offset_x + self.food[0] * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2
                food_y = self.grid_offset_y + self.food[1] * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2
                for _ in range(20):
                    self.particles.append({
                        'x': food_x, 'y': food_y,
                        'dx': random.uniform(-2, 2),
                        'dy': random.uniform(-2, 2),
                        'color': SNAKE_FOOD_COLOR,
                        'life': random.randint(20, 40)
                    })
                
                self.food = self.generate_food()
                # Increase speed slightly with each food eaten
                if self.speed > 5:
                    self.speed -= 0.2
            else:
                self.snake.pop()  # Remove tail if no food eaten
    
    def draw(self):
        # Draw background
        self.screen.fill(SNAKE_BACKGROUND)
        
        # Draw decorative border
        pygame.draw.rect(self.screen, SNAKE_ACCENT_COLOR, 
                        (self.grid_offset_x - 3, self.grid_offset_y - 3, 
                         SNAKE_GAME_WIDTH + 6, SNAKE_GAME_HEIGHT + 6), 3)
        
        # Draw grid with subtle pattern
        for x in range(SNAKE_GRID_WIDTH):
            for y in range(SNAKE_GRID_HEIGHT):
                rect = pygame.Rect(
                    self.grid_offset_x + x * SNAKE_CELL_SIZE,
                    self.grid_offset_y + y * SNAKE_CELL_SIZE,
                    SNAKE_CELL_SIZE, SNAKE_CELL_SIZE
                )
                # Alternate grid cell shades
                if (x + y) % 2 == 0:
                    pygame.draw.rect(self.screen, (SNAKE_GRID_COLOR[0]-5, SNAKE_GRID_COLOR[1]-5, SNAKE_GRID_COLOR[2]-5), rect)
                else:
                    pygame.draw.rect(self.screen, SNAKE_GRID_COLOR, rect)
                pygame.draw.rect(self.screen, (SNAKE_GRID_COLOR[0]-15, SNAKE_GRID_COLOR[1]-15, SNAKE_GRID_COLOR[2]-15), rect, 1)
        
        # Draw particles
        self.draw_particles()
        
        # Draw food with pulsing effect
        pulse_size = math.sin(self.food_pulse) * 2 + 2
        food_rect = pygame.Rect(
            self.grid_offset_x + self.food[0] * SNAKE_CELL_SIZE + pulse_size,
            self.grid_offset_y + self.food[1] * SNAKE_CELL_SIZE + pulse_size,
            SNAKE_CELL_SIZE - pulse_size * 2,
            SNAKE_CELL_SIZE - pulse_size * 2
        )
        pygame.draw.ellipse(self.screen, SNAKE_FOOD_COLOR, food_rect)
        
        # Draw food glow
        glow_size = math.sin(self.food_pulse) * 3 + 8
        glow_surface = pygame.Surface((SNAKE_CELL_SIZE + glow_size * 2, SNAKE_CELL_SIZE + glow_size * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surface, (SNAKE_FOOD_COLOR[0], SNAKE_FOOD_COLOR[1], SNAKE_FOOD_COLOR[2], 50), 
                           glow_surface.get_rect())
        self.screen.blit(glow_surface, 
                        (self.grid_offset_x + self.food[0] * SNAKE_CELL_SIZE - glow_size, 
                         self.grid_offset_y + self.food[1] * SNAKE_CELL_SIZE - glow_size))
        
        # Create food particles occasionally
        if random.random() < 0.1:
            self.create_food_particles()
        
        # Draw obstacles with glowing effect
        glow_intensity = int(math.sin(self.obstacle_glow) * 30 + 30)
        for obs in self.obstacles:
            obs_rect = pygame.Rect(
                self.grid_offset_x + obs[0] * SNAKE_CELL_SIZE,
                self.grid_offset_y + obs[1] * SNAKE_CELL_SIZE,
                SNAKE_CELL_SIZE, SNAKE_CELL_SIZE
            )
            # Draw glow
            glow_surface = pygame.Surface((SNAKE_CELL_SIZE + 10, SNAKE_CELL_SIZE + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, 
                            (SNAKE_OBSTACLE_COLOR[0], SNAKE_OBSTACLE_COLOR[1], SNAKE_OBSTACLE_COLOR[2], glow_intensity), 
                            glow_surface.get_rect(), border_radius=5)
            self.screen.blit(glow_surface, 
                            (self.grid_offset_x + obs[0] * SNAKE_CELL_SIZE - 5, 
                             self.grid_offset_y + obs[1] * SNAKE_CELL_SIZE - 5))
            
            # Draw obstacle
            pygame.draw.rect(self.screen, SNAKE_OBSTACLE_COLOR, obs_rect, border_radius=3)
            pygame.draw.rect(self.screen, (200, 160, 0), obs_rect, 2, border_radius=3)
        
        # Draw snake with rounded segments
        for i, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(
                self.grid_offset_x + x * SNAKE_CELL_SIZE + 1,
                self.grid_offset_y + y * SNAKE_CELL_SIZE + 1,
                SNAKE_CELL_SIZE - 2, SNAKE_CELL_SIZE - 2
            )
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
            
            # Draw snake segment with rounded corners
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            
            # Draw eyes on head
            if i == 0:
                eye_size = 4
                # Determine eye positions based on direction
                if self.direction == RIGHT:
                    left_eye = (rect.right - 6, rect.top + 6)
                    right_eye = (rect.right - 6, rect.bottom - 6)
                elif self.direction == LEFT:
                    left_eye = (rect.left + 6, rect.top + 6)
                    right_eye = (rect.left + 6, rect.bottom - 6)
                elif self.direction == UP:
                    left_eye = (rect.left + 6, rect.top + 6)
                    right_eye = (rect.right - 6, rect.top + 6)
                else:  # DOWN
                    left_eye = (rect.left + 6, rect.bottom - 6)
                    right_eye = (rect.right - 6, rect.bottom - 6)
                
                pygame.draw.circle(self.screen, (0, 0, 0), left_eye, eye_size)
                pygame.draw.circle(self.screen, (0, 0, 0), right_eye, eye_size)
        
        # Draw UI panel
        pygame.draw.rect(self.screen, (30, 34, 42), (0, 0, SNAKE_SCREEN_WIDTH, 60))
        pygame.draw.line(self.screen, SNAKE_ACCENT_COLOR, (0, 60), (SNAKE_SCREEN_WIDTH, 60), 2)
        
        # Draw score with icon
        score_text = self.font.render(f"Score: {self.score}", True, SNAKE_TEXT_COLOR)
        self.screen.blit(score_text, (80, 20))
        
        # Draw score icon
        pygame.draw.rect(self.screen, SNAKE_ACCENT_COLOR, (30, 20, 30, 20), border_radius=3)
        pygame.draw.rect(self.screen, SNAKE_ACCENT_COLOR, (40, 15, 10, 5))
        
        # Draw obstacle timer if obstacle is active
        if self.current_obstacle and self.score >= 4:
            time_left = (self.obstacle_duration - self.obstacle_timer) // 60
            timer_text = self.font.render(f"Obstacle: {time_left}s", True, SNAKE_OBSTACLE_COLOR)
            self.screen.blit(timer_text, (SNAKE_SCREEN_WIDTH - 150, 20))
            
            # Draw obstacle icon
            pygame.draw.rect(self.screen, SNAKE_OBSTACLE_COLOR, 
                            (SNAKE_SCREEN_WIDTH - 180, 20, 15, 15), border_radius=2)
        
        # Draw warning when obstacles are about to appear
        if self.score == 3:
            warning_text = self.font.render("Warning: Obstacles will appear at next score!", True, SNAKE_OBSTACLE_COLOR)
            self.screen.blit(warning_text, (SNAKE_SCREEN_WIDTH // 2 - warning_text.get_width() // 2, 20))
        
        # Draw controls help
        controls_bg = pygame.Rect(10, SNAKE_SCREEN_HEIGHT - 50, 350, 40)
        pygame.draw.rect(self.screen, (30, 34, 42), controls_bg, border_radius=5)
        pygame.draw.rect(self.screen, SNAKE_ACCENT_COLOR, controls_bg, 2, border_radius=5)
        controls_text = self.font.render("Controls: Arrow Keys | Q/ESC: Quit", True, SNAKE_TEXT_COLOR)
        self.screen.blit(controls_text, (20, SNAKE_SCREEN_HEIGHT - 40))
        
        # Draw game over screen
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((SNAKE_SCREEN_WIDTH, SNAKE_SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(SNAKE_GAME_OVER_BG)
            self.screen.blit(overlay, (0, 0))
            
            # Game over text with shadow
            game_over_text = self.big_font.render("GAME OVER", True, (200, 0, 0))
            shadow_text = self.big_font.render("GAME OVER", True, (100, 0, 0))
            self.screen.blit(shadow_text, (SNAKE_SCREEN_WIDTH // 2 - shadow_text.get_width() // 2 + 2, 
                                         SNAKE_SCREEN_HEIGHT // 2 - 50 + 2))
            self.screen.blit(game_over_text, 
                            (SNAKE_SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                             SNAKE_SCREEN_HEIGHT // 2 - 50))
            
            # Final score
            score_text = self.font.render(f"Final Score: {self.score}", True, SNAKE_TEXT_COLOR)
            self.screen.blit(score_text, 
                            (SNAKE_SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                             SNAKE_SCREEN_HEIGHT // 2 + 10))
            
            # Restart instructions
            restart_text = self.font.render("Press R to Restart or Q/ESC to Quit", True, SNAKE_TEXT_COLOR)
            self.screen.blit(restart_text, 
                            (SNAKE_SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                             SNAKE_SCREEN_HEIGHT // 2 + 60))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        return True  # Return to menu

# ------------------ SNAKE GAME ENTRY POINT -----------------
def run_snake():
    game = SnakeGame()
    game.run()

# For testing the game directly
if __name__ == "__main__":
    pygame.init()
    run_snake()