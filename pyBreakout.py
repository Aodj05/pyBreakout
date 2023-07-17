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

def load_high_scores():
    high_scores = []
    with open("high_scores.txt", "r") as file:
        for line in file:
            name, score = line.strip().split(",")
            high_scores.append((name, int(score)))
    return high_scores

high_scores = load_high_scores()

def update_high_scores(name, score):
    high_scores.append((name, score))
    high_scores.sort(key=lambda x: x[1], reverse=True)  # Sort scores in descending order
    with open("high_scores.txt", "w") as file:
        for name, score in high_scores:
            file.write(f"{name},{score}\n")

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
        if not ball.speed_power_up:  # Increase speed only if speed power-up is not active
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
        self.speed_power_up = False
        self.speed_power_up_timer = 0
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
        
        # Update power-up timers
        if self.speed_power_up:
            self.speed_power_up_timer -= 1
            if self.speed_power_up_timer <= 0:
                self.speed_power_up = False
                paddle.speed -= 2

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
        for brick in bricks:
            if brick.colliderect(ball_rect):
                if isinstance(brick, PowerUpBrick):
                    brick.apply_power_up(self, paddle)  # Apply power-up directly
                    bricks_to_remove.append(brick)
                else:
                    if abs(ball_rect.bottom - brick.y) < 2 or abs(ball_rect.top - brick.y - brick.height) < 2:
                        self.speed_y = -self.speed_y
                    if abs(ball_rect.right - brick.x) < 2 or abs(ball_rect.left - brick.x - brick.width) < 2:
                        self.speed_x = -self.speed_x
                    bricks_to_remove.append(brick)
                brick_collision.play()

        for brick in bricks_to_remove:
            bricks.remove(brick)

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
        self.power_up_icon = PowerUp(x, y, color)

    def apply_power_up(self, ball, paddle):
        if self.power_up_effect:
            self.power_up_effect(ball, paddle)
            self.power_up_effect = None

    def draw(self):
        super().draw()
        if self.power_up_effect:
            self.power_up_icon.x = self.x + self.width // 2 - self.power_up_icon.width // 2
            self.power_up_icon.y = self.y + self.height // 2 - self.power_up_icon.height // 2
            self.power_up_icon.draw()

class PowerUp:
    def __init__(self, x, y, color):
        self.width = 20
        self.height = 20
        self.x = x
        self.y = y
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

# Class for the enlarge power-up brick
class EnlargePowerUpBrick(PowerUpBrick):
    def __init__(self, x, y):
        super().__init__(x, y, YELLOW)
        self.power_up_effect = self.handle_power_up

    def handle_power_up(self, ball, paddle):
        paddle.enlarge_paddle()

# Class for the speed power-up brick
class SpeedPowerUpBrick(PowerUpBrick):
    def __init__(self, x, y):
        super().__init__(x, y, GREEN)
        self.power_up_effect = self.handle_power_up

    def handle_power_up(self, ball, paddle):
        ball.speed_power_up = True
        ball.speed_power_up_timer = 300
        paddle.increase_speed()


# Class for the explosion power-up brick
class ExplosionPowerUpBrick(PowerUpBrick):
    def __init__(self, x, y):
        super().__init__(x, y, BLUE)
        self.power_up_effect = self.handle_power_up

    def handle_power_up(self, ball, paddle):
        ball.power_up_explosion = True
        ball.explosion_timer = 300

# Generate regular bricks
brick_width = 50
brick_height = 20
brick_spacing = 10

bricks = []
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

# Create the paddle and ball objects
paddle = Paddle()
ball = Ball()

# Game loop
running = True
lives = 3
game_over = False

# Define custom events
SPEED_POWERUP_EVENT = pygame.USEREVENT + 1

def display_high_scores():
    font = pygame.font.Font(None, 30)
    y_offset = 100
    for i, (name, score) in enumerate(high_scores):
        text = font.render(f"{i + 1}. {name}: {score}", True, WHITE)
        screen.blit(text, (width // 2 - text.get_width() // 2, y_offset))
        y_offset += 30

font = pygame.font.Font(None, 42)

# Name input variables
name_input_active = False
name = ""

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
            if not name_input_active and (len(high_scores) < 10 or lives > high_scores[-1][1]):
                name_input_active = True
                name = ""
                name_prompt_text = font.render("Enter your name:", True, RED)
                screen.blit(name_prompt_text, (width // 2 - name_prompt_text.get_width() // 2, height // 2))
                pygame.display.flip()
                continue

        # ... (previous code)

        if name_input_active:
            name_text = font.render(name, True, WHITE)
            screen.blit(name_text, (width // 2 - name_text.get_width() // 2, height // 2 + 50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        update_high_scores(name, lives)
                        name_input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode

    else:
        # Update the display
        pygame.display.flip()
        continue

    # Draw power-ups in the lower right corner
    for brick in bricks:
        if isinstance(brick, PowerUpBrick) and brick.power_up_effect:
            brick.power_up_icon.x = width - brick.power_up_icon.width - 5
            brick.power_up_icon.y = height - brick.power_up_icon.height - 5
            brick.power_up_icon.draw()

    # Update the display
    pygame.display.flip()

# Quit the game
pygame.quit()
