import pygame

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

    def move_left(self):
        self.direction = "left"

    def move_right(self):
        self.direction = "right"

class Ball:
    def __init__(self):
        self.radius = 10
        self.x = width // 2
        self.y = height // 2
        self.speed_x = .2
        self.speed_y = -.2

    def draw(self):
        pygame.draw.circle(screen, RED, (self.x, self.y), self.radius)

    def update(self):
            self.x += self.speed_x
            self.y += self.speed_y

            if self.x - self.radius < 0 or self.x + self.radius > width:
                self.speed_x = -self.speed_x
            if self.y - self.radius < 0 or self.y + self.radius > height:
                self.speed_y = -self.speed_y

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
                bricks_to_remove.append(brick)
                brick_collision.play()

        for brick in bricks_to_remove:
            bricks.remove(brick)
            self.speed_x = self.speed_y = -self.speed_y

class Bricks:
    def __init__(self):
        self.width = 50
        self.height = 20
        self.spacing = 10
        self.rows = 5
        self.cols = (width - self.spacing) // (self.width + self.spacing)
        self.bricks = []
        for row in range(self.rows):
            for col in range(self.cols):
                brick_x = col * (self.width + self.spacing) + self.spacing
                brick_y = row * (self.height + self.spacing) + self.spacing
                self.bricks.append(pygame.Rect(brick_x, brick_y, self.width, self.height))

    def draw(self):
        for brick in self.bricks:
            pygame.draw.rect(screen, WHITE, brick)

    def handle_collision(self, ball):
        for brick in self.bricks:
            if brick.colliderect(ball):
                self.bricks.remove(brick)
                ball.speed_y = -ball.speed_y

# Create game objects
paddle = Paddle()
ball = Ball()
bricks = Bricks()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                paddle.move_left()
            elif event.key == pygame.K_RIGHT:
                paddle.move_right()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and paddle.direction == "left":
                paddle.direction = None
            elif event.key == pygame.K_RIGHT and paddle.direction == "right":
                paddle.direction = None

    # Update paddle direction
    paddle.update()

    # Update the ball position
    ball.update()

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw game objects
    paddle.draw()
    ball.draw()
    bricks.draw()

    # Handle ball-to-brick collision detection
    ball.handle_collision(bricks.bricks)

    # Update the display
    pygame.display.flip()

# Quit the game
pygame.quit()
