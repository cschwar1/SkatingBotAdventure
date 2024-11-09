import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Skating Bot Adventure")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN = (165, 42, 42)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)

# Fonts
font = pygame.font.Font(None, 36)

# Robot class
class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.speed = 5
        self.jump_power = 15
        self.velocity_y = 0
        self.is_jumping = False
        self.acrobatic_state = 0
        self.acrobatic_cooldown = 0
        self.score = 0
        self.lives = 3
        self.invincibility_timer = 0

    def draw(self):
        if self.invincibility_timer > 0 and self.invincibility_timer % 10 < 5:
            return  # Create a blinking effect when invincible
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))

    def move(self, dx):
        self.x += dx * self.speed
        self.x = max(0, min(self.x, WIDTH - self.width))

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = -self.jump_power
            self.is_jumping = True

    def perform_acrobatics(self):
        if self.is_jumping and self.acrobatic_cooldown == 0:
            self.acrobatic_state = (self.acrobatic_state + 1) % 3
            self.acrobatic_cooldown = 30
            self.score += 10

    def update(self, obstacles):
        self.y += self.velocity_y
        if self.is_jumping:
            self.velocity_y += 1  # Gravity
        
        # Check for collision with obstacles
        for obstacle in obstacles:
            if obstacle.collide(self) and self.invincibility_timer == 0:
                if self.velocity_y > 0:
                    self.y = obstacle.y - self.height
                    self.is_jumping = False
                    self.velocity_y = 0
                else:
                    self.lives -= 1
                    self.invincibility_timer = 60  # 1 second of invincibility
                break
        else:
            if self.y >= HEIGHT - self.height:
                self.y = HEIGHT - self.height
                self.is_jumping = False
                self.velocity_y = 0

        if self.acrobatic_cooldown > 0:
            self.acrobatic_cooldown -= 1

        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

        # Increase score over time
        self.score += 1

# Obstacle class
class Obstacle:
    def __init__(self, x, y, width, height, color, obstacle_type="normal"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.type = obstacle_type
        self.melting = False
        self.melt_speed = 0.5
        self.move_direction = random.choice([-1, 1])
        self.move_speed = random.uniform(0.5, 2)

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def update(self):
        if self.melting:
            self.height -= self.melt_speed
            self.y += self.melt_speed
            if self.height <= 0:
                return True
        
        if self.type == "moving":
            self.x += self.move_speed * self.move_direction
            if self.x <= 0 or self.x + self.width >= WIDTH:
                self.move_direction *= -1
        
        return False

    def collide(self, robot):
        return (robot.x < self.x + self.width and
                robot.x + robot.width > self.x and
                robot.y < self.y + self.height and
                robot.y + robot.height > self.y)

# Slope class
class Slope(Obstacle):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, BROWN, "slope")

    def draw(self):
        pygame.draw.polygon(screen, self.color, [(self.x, self.y + self.height),
                                                 (self.x + self.width, self.y),
                                                 (self.x + self.width, self.y + self.height)])

    def collide(self, robot):
        if super().collide(robot):
            # Calculate the y-position on the slope
            slope = self.height / self.width
            relative_x = robot.x + robot.width - self.x
            y_on_slope = self.y + self.height - (slope * relative_x)
            
            if robot.y + robot.height > y_on_slope:
                robot.y = y_on_slope - robot.height
                robot.is_jumping = False
                robot.velocity_y = 0
                return True
        return False

# Level class
class Level:
    def __init__(self, obstacles):
        self.obstacles = obstacles

    def update(self):
        for obstacle in self.obstacles:
            if obstacle.update():
                self.obstacles.remove(obstacle)

    def draw(self):
        for obstacle in self.obstacles:
            obstacle.draw()

# Create levels
levels = [
    Level([
        Obstacle(200, HEIGHT - 150, 100, 50, RED),
        Obstacle(500, HEIGHT - 200, 150, 100, GREEN),
        Slope(350, HEIGHT - 250, 200, 100)
    ]),
    Level([
        Obstacle(100, HEIGHT - 200, 150, 100, RED),
        Obstacle(400, HEIGHT - 150, 100, 50, GREEN, "moving"),
        Slope(600, HEIGHT - 300, 150, 150),
        Obstacle(300, HEIGHT - 100, 50, 50, RED)
    ]),
    Level([
        Obstacle(50, HEIGHT - 150, 75, 75, RED, "moving"),
        Obstacle(200, HEIGHT - 200, 100, 100, GREEN),
        Slope(400, HEIGHT - 250, 250, 150),
        Obstacle(700, HEIGHT - 175, 50, 100, CYAN, "moving")
    ])
]

# Create the robot
robot = Robot(50, HEIGHT - 100)  # Start the robot at the left side of the screen

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

def draw_text(text, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)

def show_menu():
    screen.fill(WHITE)
    draw_text("Skating Bot Adventure", BLUE, WIDTH // 2, HEIGHT // 3)
    draw_text("Press SPACE to Start", BLACK, WIDTH // 2, HEIGHT // 2)
    draw_text("Press Q to Quit", BLACK, WIDTH // 2, HEIGHT * 2 // 3)
    pygame.display.flip()

def show_game_over():
    screen.fill(WHITE)
    draw_text("Game Over", RED, WIDTH // 2, HEIGHT // 3)
    draw_text(f"Final Score: {robot.score}", BLUE, WIDTH // 2, HEIGHT // 2)
    draw_text("Press SPACE to Restart", BLACK, WIDTH // 2, HEIGHT * 2 // 3)
    draw_text("Press Q to Quit", BLACK, WIDTH // 2, HEIGHT * 5 // 6)
    pygame.display.flip()

# Game loop
clock = pygame.time.Clock()
game_state = MENU
running = True
frame_count = 0
current_level = 0

while running:
    if game_state == MENU:
        show_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_state = PLAYING
                    robot = Robot(50, HEIGHT - 100)
                    frame_count = 0
                    current_level = 0
                elif event.key == pygame.K_q:
                    running = False

    elif game_state == PLAYING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    robot.jump()
                elif event.key == pygame.K_a:
                    robot.perform_acrobatics()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            robot.move(-1)
        if keys[pygame.K_RIGHT]:
            robot.move(1)

        # Update robot
        robot.update(levels[current_level].obstacles)

        # Update and draw level
        levels[current_level].update()

        # Clear the screen
        screen.fill(WHITE)

        # Draw the level
        levels[current_level].draw()

        # Draw the robot
        robot.draw()

        # Draw the score and lives
        draw_text(f"Score: {robot.score}", BLACK, 70, 20)
        draw_text(f"Lives: {robot.lives}", BLACK, WIDTH - 70, 20)

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)
        
        frame_count += 1
        
        # Switch to next level every 1800 frames (30 seconds at 60 FPS)
        if frame_count % 1800 == 0:
            current_level = (current_level + 1) % len(levels)
            robot.x = 50
            robot.y = HEIGHT - 100

        # Randomly melt obstacles
        if frame_count % 300 == 0:
            for obstacle in levels[current_level].obstacles:
                if obstacle.type == "normal" and random.random() < 0.3:
                    obstacle.melting = True

        # Check for game over
        if robot.lives <= 0:
            game_state = GAME_OVER

    elif game_state == GAME_OVER:
        show_game_over()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_state = PLAYING
                    robot = Robot(50, HEIGHT - 100)
                    frame_count = 0
                    current_level = 0
                elif event.key == pygame.K_q:
                    running = False

# Quit the game
pygame.quit()
sys.exit()