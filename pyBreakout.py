import pygame
import random

# Initialize Pygame
pygame.init()

pygame.mixer.init()

paddle_collision = pygame.mixer.Sound("sounds/Blip_Select7.wav")
brick_collision = pygame.mixer.Sound("sounds/Explosion6.wav")

# Define the game window dimensions
width = 800
height = 600

# Create the game window
screen = pygame.display.set_mode((width, height))

# Color Definitions
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

class Paddle:
    def __init__(self):
        self.width = 100
        self.height = 10
        self.x = (width - self.width) // 2
        self.y = height - 20
        self.speed = 2
        self.direction = None
        self.move_delay = 10
        self.last_move_time = pygame.time.get_ticks()
        self.power_up_enlarged = False
        self.enlarge_timer = 0

    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))

    def update(self):
        current_time = pygame.time.get_ticks()
        if self.direction == "left" and current_time - self.last_move_time >= self.move_delay:
            self.x -= self.speed
            if self.x < 0:
                self.x = 0
            self.last_move_time = current_time
        elif self.direction == "right" and current_time - self.last_move_time >= self.move_delay:
            self.x += self.speed
            if self.x + self.width > width:
                self.x = width - self.width
            self.last_move_time = current_time

        if self.power_up_enlarged:
            self.enlarge_timer -= 1
            if self.enlarge_timer <= 0:
                self.power_up_enlarged = False
                self.width = 100

    def move_left(self):
        self.direction = "left"

    def move_right(self):
        self.direction = "right"

    def enlarge_paddle(self):
        self.power_up_enlarged = True
        self.width = 200
        self.enlarge_timer = 2

    def increase_speed(self):
        self.speed += 2
        pygame.time.set_timer(SPEED_POWERUP_EVENT, 3000)

class Ball:
    def __init__(self):
        self.radius = 10
        self.x = width // 2
        self.y = height // 2
        self.speed_x = .2
        self.speed_y = -.2
        self.power_up_explosion = False
        self.explosion_timer = 0

    def draw(self):
        pygame.draw.circle(screen, RED, (self.x, self.y), self.radius)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x - self.radius < 0 or self.x + self.radius > width:
            self.speed_x = -self.speed_x
        if self.y - self.radius < 0:
            self.speed_y = -self.speed_y
        elif self.y + self.radius > height:
            self.reset_ball()
            global lives
            lives -= 1

        if self.power_up_explosion:
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                self.power_up_explosion = False

    def handle_collision(self, bricks):
        # Collision detection with paddle
        paddle_rect = pygame.Rect(paddle.x, paddle.y, paddle.width, paddle.height)
        ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        if ball_rect.colliderect(paddle_rect):
            self.speed_y = -self.speed_y
            paddle_collision.play()

        # Collision detection with bricks
        ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        bricks_to_remove = []
        power_up_effects = []
        for brick in bricks:
            if brick.colliderect(ball_rect):
                bricks_to_remove.append(brick)
                brick_collision.play()
                if isinstance(brick, PowerUpBrick):
                    power_up_effects.append(brick.power_up_effect)

        for brick in bricks_to_remove:
            if not isinstance(brick, PowerUpBrick):
                bricks.remove(brick)

        for effect in power_up_effects:
            effect(paddle, self)

        if not bricks:
            # All bricks cleared, game over
            global game_over
            game_over = True

    def reset_ball(self):
        self.x = width // 2
        self.y = height // 2
        self.speed_x = .2
        self.speed_y = -.2

class Brick:
    def __init__(self, x, y, color):
        self.width = 50
        self.height = 20
        self.x = x
        self.y = y
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def colliderect(self, other_rect):
        return pygame.Rect(self.x, self.y, self.width, self.height).colliderect(other_rect)

class PowerUpBrick(Brick):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.power_up_effect = None

class EnlargePowerUpBrick(PowerUpBrick):
    def __init__(self, x, y):
        super().__init__(x, y, YELLOW)
        self.power_up_effect = self.handle_power_up

    def handle_power_up(self, paddle, ball):
        paddle.enlarge_paddle()

class SpeedPowerUpBrick(PowerUpBrick):
    def __init__(self, x, y):
        super().__init__(x, y, GREEN)
        self.power_up_effect = self.handle_power_up

    def handle_power_up(self, paddle, ball):
        paddle.increase_speed()

class ExplosionPowerUpBrick(PowerUpBrick):
    def __init__(self, x, y):
        super().__init__(x, y, BLUE)
        self.power_up_effect = self.handle_power_up

    def handle_power_up(self, paddle, ball):
        ball.handle_collision(bricks)

# Create game objects
paddle = Paddle()
ball = Ball()
bricks = []

# Generate regular bricks
brick_width = 50
brick_height = 20
brick_spacing = 10

for row in range(5):
    for col in range(16):
        brick_x = col * (brick_width + brick_spacing) + brick_spacing
        brick_y = row * (brick_height + brick_spacing) + brick_spacing
        bricks.append(Brick(brick_x, brick_y, WHITE))

# Generate power-up bricks
power_up_brick_count = 3
power_up_brick_types = [EnlargePowerUpBrick, SpeedPowerUpBrick, ExplosionPowerUpBrick]
power_up_brick_colors = [YELLOW, GREEN, BLUE]

for row in range(5):
    for col in range(power_up_brick_count):
        brick_x = col * (brick_width + brick_spacing) + brick_spacing
        brick_y = row * (brick_height + brick_spacing) + brick_spacing
        brick_type = random.choice(power_up_brick_types)
        brick_color = random.choice(power_up_brick_colors)
        bricks.append(brick_type(brick_x, brick_y))

# Game loop
running = True
lives = 3
game_over = False

# Define custom events
SPEED_POWERUP_EVENT = pygame.USEREVENT + 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                paddle.move_left()
            elif event.key == pygame.K_RIGHT:
                paddle.move_right()
            elif event.key == pygame.K_q and game_over:
                running = False
            elif event.key == pygame.K_r and game_over:
                # Reset game
                paddle = Paddle()
                ball = Ball()
                bricks = []

                # Generate regular bricks
                for row in range(5):
                    for col in range(16):
                        brick_x = col * (brick_width + brick_spacing) + brick_spacing
                        brick_y = row * (brick_height + brick_spacing) + brick_spacing
                        bricks.append(Brick(brick_x, brick_y, WHITE))

                # Generate power-up bricks
                for row in range(5):
                    for col in range(power_up_brick_count):
                        brick_x = col * (brick_width + brick_spacing) + brick_spacing
                        brick_y = row * (brick_height + brick_spacing) + brick_spacing
                        brick_type = random.choice(power_up_brick_types)
                        brick_color = random.choice(power_up_brick_colors)
                        bricks.append(brick_type(brick_x, brick_y))

                lives = 3
                game_over = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and paddle.direction == "left":
                paddle.direction = None
            elif event.key == pygame.K_RIGHT and paddle.direction == "right":
                paddle.direction = None
        elif event.type == SPEED_POWERUP_EVENT:
            paddle.speed -= 2
            pygame.time.set_timer(SPEED_POWERUP_EVENT, 0)

    if not game_over:
        # Update paddle direction
        paddle.update()

        # Update the ball position
        ball.update()

        # Clear the screen
        screen.fill((0, 0, 0))

        # Draw game objects
        paddle.draw()
        ball.draw()
        for brick in bricks:
            brick.draw()

        # Handle ball-to-brick collision detection
        ball.handle_collision(bricks)

        if lives <= 0:
            game_over = True

        if game_over:
            # Game over
            font = pygame.font.Font(None, 42)
            game_over_text = font.render("Game Over", True, RED)
            screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2))

            # Restart or Quit prompt
            prompt_text = font.render("Press R to Restart or Q to Quit", True, RED)
            screen.blit(prompt_text, (width // 2 - prompt_text.get_width() // 2, height // 2 + 50))
    else:
        # Update the display
        pygame.display.flip()
        continue

    # Update the display
    pygame.display.flip()

# Quit the game
pygame.quit()
