import pygame
import random
import sys
from enum import Enum
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)

# Rainbow colors
RAINBOW_COLORS = [
    (255, 0, 0),    # Red
    (255, 127, 0),  # Orange
    (255, 255, 0),  # Yellow
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (75, 0, 130),   # Indigo
    (148, 0, 211)   # Violet
]

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = 4
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(5, 10)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = 100
        self.gravity = 0.2

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 2
        return self.lifetime > 0

    def draw(self, screen):
        alpha = int(255 * (self.lifetime / 100))
        color = (*self.color[:3], alpha)
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (self.size, self.size), self.size)
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

class Firework:
    def __init__(self, x, y):
        self.particles = []
        for _ in range(50):  # Number of particles
            color = random.choice(RAINBOW_COLORS)
            self.particles.append(Particle(x, y, color))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]
        return len(self.particles) > 0

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        self.fireworks = []
        self.reset_game()

    def reset_game(self):
        self.snake = [(GRID_COUNT // 2, GRID_COUNT // 2)]
        self.direction = Direction.RIGHT
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.fireworks = []

    def generate_food(self):
        while True:
            food = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
            if food not in self.snake:
                return food

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                if event.key == pygame.K_RETURN and self.game_over:
                    self.reset_game()
                if not self.game_over:
                    if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                        self.direction = Direction.UP
                    elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                        self.direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                        self.direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                        self.direction = Direction.RIGHT
        return True

    def update(self):
        if self.game_over:
            return

        # Update fireworks
        self.fireworks = [fw for fw in self.fireworks if fw.update()]

        # Get the current head position
        head_x, head_y = self.snake[0]

        # Update the head position based on direction
        if self.direction == Direction.UP:
            head_y -= 1
        elif self.direction == Direction.DOWN:
            head_y += 1
        elif self.direction == Direction.LEFT:
            head_x -= 1
        elif self.direction == Direction.RIGHT:
            head_x += 1

        # Check for collisions with walls
        if head_x < 0 or head_x >= GRID_COUNT or head_y < 0 or head_y >= GRID_COUNT:
            self.game_over = True
            return

        # Check for collisions with self
        new_head = (head_x, head_y)
        if new_head in self.snake[1:]:
            self.game_over = True
            return

        # Add new head
        self.snake.insert(0, new_head)

        # Check if food is eaten
        if new_head == self.food:
            self.score += 1
            self.food = self.generate_food()
            
            # Check if we completed a RACCOON word
            if len(self.snake) % 7 == 0:  # RACCOON has 7 letters
                # Create firework at a random position
                fx = random.randint(GRID_SIZE, WINDOW_SIZE - GRID_SIZE)
                fy = random.randint(GRID_SIZE, WINDOW_SIZE - GRID_SIZE)
                self.fireworks.append(Firework(fx, fy))
        else:
            self.snake.pop()

    def draw(self):
        self.screen.fill(BLACK)

        # Draw snake
        word = "RACCOON"
        for i, (x, y) in enumerate(self.snake):
            color = DARK_GREEN if i == 0 else GREEN  # Different color for head
            # Draw the background rectangle
            pygame.draw.rect(self.screen, color, 
                           (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))
            
            # Draw the letter
            letter = word[i % len(word)]  # Cycle through the letters
            rainbow_color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]  # Cycle through rainbow colors
            font = pygame.font.Font(None, GRID_SIZE)
            text = font.render(letter, True, rainbow_color)  # Use rainbow color for text
            text_rect = text.get_rect(center=(x * GRID_SIZE + GRID_SIZE//2, 
                                            y * GRID_SIZE + GRID_SIZE//2))
            self.screen.blit(text, text_rect)

        # Draw food
        pygame.draw.rect(self.screen, RED,
                        (self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE, 
                         GRID_SIZE - 1, GRID_SIZE - 1))

        # Draw fireworks
        for firework in self.fireworks:
            firework.draw(self.screen)

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw game over message
        if self.game_over:
            font = pygame.font.Font(None, 72)
            game_over_text = font.render('Game Over!', True, WHITE)
            restart_text = font.render('Press Enter to Restart', True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_SIZE/2, WINDOW_SIZE/2))
            restart_rect = restart_text.get_rect(center=(WINDOW_SIZE/2, WINDOW_SIZE/2 + 50))
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == '__main__':
    game = SnakeGame()
    game.run()
