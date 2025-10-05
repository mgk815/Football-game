import pygame, sys, math, random, time, os, sys

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lane's Birthday Game")
clock = pygame.time.Clock()

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

menu_bg = pygame.image.load(resource_path("samuel_surprised.jpg")).convert()
gameover_bg = pygame.image.load(resource_path("samuel_surprised.jpg")).convert()
game_bg = pygame.image.load(resource_path("panthers_field.webp")).convert()
goal_sound = pygame.mixer.Sound(resource_path("goal_ping.mp3"))
icon = pygame.image.load(resource_path("panthers_logo.png")).convert_alpha()


# Set it as the window icon
pygame.display.set_icon(icon)

# Colors
PANTHERS_BLUE = (0, 133, 202)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
BLACK = (0, 0, 0)

# optional: scale to current window size
menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))
gameover_bg = pygame.transform.scale(gameover_bg, (WIDTH, HEIGHT))
game_bg = pygame.transform.scale(game_bg, (WIDTH, HEIGHT))


# Game settings
game_state = "menu"  # can be 'menu', 'playing', 'gameover'
timer = 30  # seconds
start_ticks = 0

# Ball settings
ball_x = WIDTH // 2
ball_y = HEIGHT - 80
ball_vx = 0
ball_vy = 0
kicked = False
charging = False
power = 0
angle = 90  # straight up

# Goal setup
goal_width = 100
goal_height = 10
goal_x = WIDTH // 2
goal_y = 300
goal_speed_x = random.choice([-3, 3])
goal_speed_y = random.choice([-2, 2])

# Scoring
score = 0
font = pygame.font.SysFont(None, 60)
small_font = pygame.font.SysFont(None, 40)


def reset_ball():
    global ball_x, ball_y, kicked, ball_vx, ball_vy, power, angle
    ball_x = WIDTH // 2
    ball_y = HEIGHT - 80
    ball_vx = 0
    ball_vy = 0
    kicked = False
    power = 0
    angle = 90

def draw_football(x, y):
    football_rect = pygame.Rect(x - 20, y - 10, 40, 20)
    pygame.draw.ellipse(screen, BROWN, football_rect)
    pygame.draw.line(screen, WHITE, (x - 10, y), (x + 10, y), 2)
    pygame.draw.line(screen, WHITE, (x, y - 5), (x, y + 5), 2)
    pygame.draw.line(screen, WHITE, (x - 5, y - 5), (x - 5, y + 5), 2)
    pygame.draw.line(screen, WHITE, (x + 5, y - 5), (x + 5, y + 5), 2)

def draw_goalpost():
    upright_height = 100
    post_thickness = 8
    stem_height = 80
    left_post_x = goal_x - goal_width // 2
    right_post_x = goal_x + goal_width // 2
    crossbar_y = goal_y

    pygame.draw.rect(screen, GOLD, (goal_x - post_thickness // 2, crossbar_y, post_thickness, stem_height))  # stem
    pygame.draw.rect(screen, GOLD, (left_post_x, crossbar_y - post_thickness, goal_width, post_thickness))     # crossbar
    pygame.draw.rect(screen, GOLD, (left_post_x, crossbar_y - upright_height - post_thickness, post_thickness, upright_height))  # left upright
    pygame.draw.rect(screen, GOLD, (right_post_x - post_thickness, crossbar_y - upright_height - post_thickness, post_thickness, upright_height))  # right upright

def draw_power_meter():
    bar_x, bar_y = 30, HEIGHT - 60
    bar_width, bar_height = 200, 25
    pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
    fill_width = (power / 100) * bar_width
    pygame.draw.rect(screen, GOLD, (bar_x, bar_y, fill_width, bar_height))
    label = pygame.font.SysFont(None, 40).render(f"Power: {int(power)}", True, BLACK)
    screen.blit(label, (bar_x, bar_y - 35))

def draw_aim_arrow():
    arrow_length = 80
    rad = math.radians(angle)
    end_x = ball_x + arrow_length * math.cos(rad)
    end_y = ball_y - arrow_length * math.sin(rad)
    pygame.draw.line(screen, BLACK, (ball_x, ball_y), (end_x, end_y), 3)
    pygame.draw.polygon(screen, BLACK, [
        (end_x, end_y),
        (end_x - 8 * math.cos(rad - 0.1), end_y + 8 * math.sin(rad - 0.1)),
        (end_x - 8 * math.cos(rad + 0.1), end_y + 8 * math.sin(rad + 0.1)),
    ])

def ball_in_goal():
    left_edge = goal_x - goal_width // 2 + 8
    right_edge = goal_x + goal_width // 2 - 8
    top_edge = goal_y - 100
    bottom_edge = goal_y
    return left_edge < ball_x < right_edge and top_edge < ball_y < bottom_edge

def draw_game():
    screen.blit(game_bg, (0, 0))
    draw_goalpost()
    draw_football(ball_x, ball_y)
    score_text = pygame.font.SysFont(None, 40).render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (30, 40))

    # Timer
    seconds_passed = int((pygame.time.get_ticks() - start_ticks) / 1000)
    remaining = max(0, timer - seconds_passed)
    timer_text = pygame.font.SysFont(None, 40).render(f"Time: {remaining}", True, BLACK)
    screen.blit(timer_text, (WIDTH - 150, 40))

    draw_power_meter()
    if not kicked:
        draw_aim_arrow()
    pygame.display.flip()

def draw_menu():
    # Draw menu background image
    screen.blit(menu_bg, (0, 0))

    title = font.render("Lane's Birthday Game", True, WHITE)
    screen.blit(title, (WIDTH // 1.6 - title.get_width() // 2, 150))
    instructions = [
        "Use LEFT/RIGHT arrows to aim",
        "Hold SPACE to charge power",
        "Release SPACE to kick",
        "Score as many goals as possible in 30 seconds",
        "Press SPACE to start!"
    ]
    for i, line in enumerate(instructions):
        text = small_font.render(line, True, WHITE)
        screen.blit(text, (WIDTH // 1.6 - text.get_width() // 2, 300 + i * 50))
    pygame.display.flip()

def draw_gameover():
    # Draw gameover background image
    screen.blit(gameover_bg, (0, 0))

    title = font.render("Time's Up!", True, WHITE)
    screen.blit(title, (WIDTH // 1.6 - title.get_width() // 2, 200))
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 1.6 - score_text.get_width() // 2, 300))
    prompt = small_font.render("Press SPACE to play again", True, WHITE)
    screen.blit(prompt, (WIDTH // 1.6 - prompt.get_width() // 2, 400))
    pygame.display.flip()


# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == "menu":
                    game_state = "playing"
                    start_ticks = pygame.time.get_ticks()
                    score = 0
                    reset_ball()
                elif game_state == "playing" and not kicked:
                    charging = True
                elif game_state == "gameover":
                    game_state = "playing"
                    start_ticks = pygame.time.get_ticks()
                    score = 0
                    reset_ball()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and game_state == "playing" and not kicked:
                charging = False
                kicked = True

                # Determine max jump height (in pixels)
                max_jump_height = HEIGHT *1.2   # 70% of screen height

                # Use basic kinematic formula to compute initial velocity to reach that height
                # v = sqrt(2 * g * h)
                gravity = 0.6  # same as used in ball movement
                velocity = (power / 100) * math.sqrt(2 * gravity * max_jump_height)

                rad = math.radians(angle)
                ball_vx = velocity * math.cos(rad)
                ball_vy = -velocity * math.sin(rad)



    keys = pygame.key.get_pressed()
    if game_state == "playing" and not kicked:
        if keys[pygame.K_LEFT]:
            angle += 1.5
        if keys[pygame.K_RIGHT]:
            angle -= 1.5
        angle = max(30, min(150, angle))

    if charging:
        power = (power + 1) % 101

    if game_state == "playing":
        # Move goal
        goal_x += goal_speed_x
        goal_y += goal_speed_y
        if goal_x < 100 or goal_x > WIDTH - 100:
            goal_speed_x *= -1
        if goal_y < 150 or goal_y > HEIGHT - 200:
            goal_speed_y *= -1

        # Move ball
        if kicked:
            ball_x += ball_vx
            ball_y += ball_vy
            ball_vy += 0.6  # gravity

            if ball_in_goal():
                score += 1
                goal_sound.play()  # play sound
                reset_ball()
            if ball_y > HEIGHT or ball_x < 0 or ball_x > WIDTH:
                reset_ball()

        # Check timer
        seconds_passed = int((pygame.time.get_ticks() - start_ticks) / 1000)
        if seconds_passed >= timer:
            game_state = "gameover"

        draw_game()
    elif game_state == "menu":
        draw_menu()
    elif game_state == "gameover":
        draw_gameover()

    clock.tick(60)

pygame.quit()
sys.exit()
