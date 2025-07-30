import pygame
import random
import sys
import time
from pygame import mixer

# Initialize Pygame
pygame.init()
mixer.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)

# Tetris colors
CYAN = (0, 255, 255)      # I piece
BLUE = (0, 0, 255)        # J piece
ORANGE = (255, 165, 0)    # L piece
YELLOW = (255, 255, 0)    # O piece
GREEN = (0, 255, 0)       # S piece
PURPLE = (128, 0, 128)    # T piece
RED = (255, 0, 0)         # Z piece

# Background gradient colors
BG_TOP = (25, 25, 50)
BG_BOTTOM = (50, 25, 75)

# Game dimensions
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_OFFSET_X = 200
GRID_OFFSET_Y = 50

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Beautiful Tetris Game")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.Font(None, 48)
large_font = pygame.font.Font(None, 36)
medium_font = pygame.font.Font(None, 28)
small_font = pygame.font.Font(None, 24)

# Tetris pieces (tetrominoes)
PIECES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]   # Z
]

PIECE_COLORS = [CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED]

class TetrisGame:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_color = None
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.difficulty = "Easy"
        self.game_over = False
        self.paused = False
        self.drop_time = 0
        self.drop_speed = 1000  # milliseconds
        self.next_piece = None
        self.next_color = None
        self.particles = []
        
        # Difficulty settings
        self.difficulty_speeds = {
            "Easy": 1000,
            "Medium": 600,
            "Hard": 300,
            "Impossible": 150
        }
        
        self.spawn_new_piece()
        self.generate_next_piece()
    
    def generate_next_piece(self):
        piece_idx = random.randint(0, len(PIECES) - 1)
        self.next_piece = PIECES[piece_idx]
        self.next_color = PIECE_COLORS[piece_idx]
    
    def spawn_new_piece(self):
        if self.next_piece is None:
            self.generate_next_piece()
        
        self.current_piece = self.next_piece
        self.current_color = self.next_color
        self.current_x = GRID_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.current_y = 0
        
        self.generate_next_piece()
        
        # Check if game over
        if not self.is_valid_move(self.current_piece, self.current_x, self.current_y):
            self.game_over = True
    
    def is_valid_move(self, piece, x, y):
        for row_idx, row in enumerate(piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = x + col_idx
                    new_y = y + row_idx
                    
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True
    
    def place_piece(self):
        for row_idx, row in enumerate(self.current_piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    grid_y = self.current_y + row_idx
                    grid_x = self.current_x + col_idx
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = self.current_color
        
        self.clear_lines()
        self.spawn_new_piece()
    
    def clear_lines(self):
        lines_to_clear = []
        for row_idx in range(GRID_HEIGHT):
            if all(self.grid[row_idx]):
                lines_to_clear.append(row_idx)
        
        if lines_to_clear:
            # Create particle effects
            for line_idx in lines_to_clear:
                for col_idx in range(GRID_WIDTH):
                    self.particles.append({
                        'x': GRID_OFFSET_X + col_idx * BLOCK_SIZE + BLOCK_SIZE // 2,
                        'y': GRID_OFFSET_Y + line_idx * BLOCK_SIZE + BLOCK_SIZE // 2,
                        'vx': random.uniform(-3, 3),
                        'vy': random.uniform(-5, -2),
                        'life': 60,
                        'color': self.grid[line_idx][col_idx]
                    })
            
            # Remove lines
            for line_idx in reversed(lines_to_clear):
                del self.grid[line_idx]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            
            # Update score
            lines_cleared = len(lines_to_clear)
            self.lines_cleared += lines_cleared
            self.score += lines_cleared * 100 * self.level
            
            # Level up every 10 lines
            self.level = self.lines_cleared // 10 + 1
    
    def rotate_piece(self):
        if self.current_piece:
            # Transpose and reverse rows to rotate 90 degrees clockwise
            rotated = list(zip(*self.current_piece[::-1]))
            rotated = [list(row) for row in rotated]
            
            if self.is_valid_move(rotated, self.current_x, self.current_y):
                self.current_piece = rotated
    
    def move_piece(self, dx, dy):
        if self.current_piece:
            new_x = self.current_x + dx
            new_y = self.current_y + dy
            
            if self.is_valid_move(self.current_piece, new_x, new_y):
                self.current_x = new_x
                self.current_y = new_y
                return True
        return False
    
    def drop_piece(self):
        while self.move_piece(0, 1):
            pass
        self.place_piece()
    
    def update(self, dt):
        if self.game_over or self.paused:
            return
        
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # gravity
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        # Auto drop
        self.drop_time += dt
        if self.drop_time >= self.drop_speed:
            if not self.move_piece(0, 1):
                self.place_piece()
            self.drop_time = 0
    
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.drop_speed = self.difficulty_speeds[difficulty]
    
    def draw(self):
        # Draw gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
            g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
            b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Draw grid background
        grid_rect = pygame.Rect(GRID_OFFSET_X - 5, GRID_OFFSET_Y - 5, 
                               GRID_WIDTH * BLOCK_SIZE + 10, 
                               GRID_HEIGHT * BLOCK_SIZE + 10)
        pygame.draw.rect(screen, DARK_GRAY, grid_rect, 3)
        
        # Draw placed pieces
        for row_idx in range(GRID_HEIGHT):
            for col_idx in range(GRID_WIDTH):
                if self.grid[row_idx][col_idx]:
                    x = GRID_OFFSET_X + col_idx * BLOCK_SIZE
                    y = GRID_OFFSET_Y + row_idx * BLOCK_SIZE
                    pygame.draw.rect(screen, self.grid[row_idx][col_idx], 
                                   (x, y, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(screen, WHITE, 
                                   (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # Draw current piece
        if self.current_piece and not self.game_over:
            for row_idx, row in enumerate(self.current_piece):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = GRID_OFFSET_X + (self.current_x + col_idx) * BLOCK_SIZE
                        y = GRID_OFFSET_Y + (self.current_y + row_idx) * BLOCK_SIZE
                        pygame.draw.rect(screen, self.current_color, 
                                       (x, y, BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(screen, WHITE, 
                                       (x, y, BLOCK_SIZE, BLOCK_SIZE), 2)
        
        # Draw particles
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 60))
            color = (*particle['color'][:3], alpha)
            pygame.draw.circle(screen, color, 
                             (int(particle['x']), int(particle['y'])), 3)
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self):
        # Title
        title_text = title_font.render("TETRIS", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_text, title_rect)
        
        # Score
        score_text = large_font.render(f"Score: {self.score:,}", True, WHITE)
        screen.blit(score_text, (20, 100))
        
        # Lines
        lines_text = large_font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        screen.blit(lines_text, (20, 140))
        
        # Level
        level_text = large_font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(level_text, (20, 180))
        
        # Difficulty
        diff_text = large_font.render(f"Difficulty: {self.difficulty}", True, WHITE)
        screen.blit(diff_text, (20, 220))
        
        # Next piece
        next_text = large_font.render("Next:", True, WHITE)
        screen.blit(next_text, (GRID_OFFSET_X + GRID_WIDTH * BLOCK_SIZE + 20, 100))
        
        if self.next_piece:
            next_x = GRID_OFFSET_X + GRID_WIDTH * BLOCK_SIZE + 50
            next_y = 140
            for row_idx, row in enumerate(self.next_piece):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = next_x + col_idx * BLOCK_SIZE
                        y = next_y + row_idx * BLOCK_SIZE
                        pygame.draw.rect(screen, self.next_color, 
                                       (x, y, BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(screen, WHITE, 
                                       (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # Controls
        controls = [
            "Controls:",
            "← → : Move",
            "↓ : Soft Drop",
            "Space : Hard Drop",
            "↑ : Rotate",
            "P : Pause",
            "R : Restart"
        ]
        
        for i, control in enumerate(controls):
            color = WHITE if i == 0 else LIGHT_GRAY
            font = medium_font if i == 0 else small_font
            text = font.render(control, True, color)
            screen.blit(text, (20, 300 + i * 25))
        
        # Game over or pause overlay
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            game_over_text = title_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(game_over_text, game_over_rect)
            
            restart_text = medium_font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            screen.blit(restart_text, restart_rect)
        
        elif self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            pause_text = title_font.render("PAUSED", True, YELLOW)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(pause_text, pause_rect)

def draw_menu():
    # Draw gradient background
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    # Title
    title_text = title_font.render("TETRIS", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
    screen.blit(title_text, title_rect)
    
    # Subtitle
    subtitle_text = large_font.render("Select Difficulty", True, LIGHT_GRAY)
    subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
    screen.blit(subtitle_text, subtitle_rect)
    
    # Difficulty buttons
    difficulties = ["Easy", "Medium", "Hard", "Impossible"]
    button_y = 300
    
    for i, difficulty in enumerate(difficulties):
        button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, button_y + i * 60, 200, 50)
        color = CYAN if i == 0 else BLUE if i == 1 else ORANGE if i == 2 else RED
        
        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, WHITE, button_rect, 3)
        
        text = large_font.render(difficulty, True, WHITE)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)
    
    # Instructions
    instructions = [
        "How to Play:",
        "• Move pieces left/right with arrow keys",
        "• Rotate with up arrow",
        "• Drop faster with down arrow",
        "• Instant drop with spacebar",
        "• Pause with P key",
        "• Restart with R key"
    ]
    
    for i, instruction in enumerate(instructions):
        color = WHITE if i == 0 else LIGHT_GRAY
        font = medium_font if i == 0 else small_font
        text = font.render(instruction, True, color)
        screen.blit(text, (50, 550 + i * 25))

def main():
    game = TetrisGame()
    in_menu = True
    selected_difficulty = 0
    
    while True:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if in_menu:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_difficulty = (selected_difficulty - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        selected_difficulty = (selected_difficulty + 1) % 4
                    elif event.key == pygame.K_RETURN:
                        difficulties = ["Easy", "Medium", "Hard", "Impossible"]
                        game.set_difficulty(difficulties[selected_difficulty])
                        in_menu = False
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        game.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:
                        game.move_piece(0, 1)
                    elif event.key == pygame.K_UP:
                        game.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        game.drop_piece()
                    elif event.key == pygame.K_p:
                        game.paused = not game.paused
                    elif event.key == pygame.K_r:
                        game = TetrisGame()
                        in_menu = True
                        selected_difficulty = 0
        
        if in_menu:
            draw_menu()
        else:
            game.update(dt)
            game.draw()
        
        pygame.display.flip()

if __name__ == "__main__":
    main() 