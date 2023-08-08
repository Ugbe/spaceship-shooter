import time

import pygame
import os

pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

YELLOW_VEL = 5
RED_VEL = 2
BULLET_VEL = 7
MAX_BULLETS = 4

YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2
DURABILITY_FONT = pygame.font.SysFont('arial', 40)
WINNER_FONT = pygame.font.SysFont('Arial', 100)

SHIP_WIDTH, SHIP_HEIGHT = 55, 45
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 100, 0)

BORDER = pygame.Rect(WIDTH // 2 - 5, 0, 10, HEIGHT)

BG = (63, 66, 193)
FPS = 60
YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets', 'yellow_spaceship.png'))
YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SHIP_WIDTH, SHIP_HEIGHT)),
                                           270)
RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets', 'red_spaceship.png'))
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, (SHIP_WIDTH, SHIP_HEIGHT)), 90)


def draw(red, yellow, red_bullets, yellow_bullets, red_durability, yellow_durability):
    WIN.fill(BG)
    pygame.draw.rect(WIN, BLACK, BORDER)

    red_durability_text = DURABILITY_FONT.render("Durability: " + str(red_durability), 1, WHITE)
    yellow_durability_text = DURABILITY_FONT.render("Durability: " + str(yellow_durability), 1, WHITE)
    WIN.blit(red_durability_text, (WIDTH - red_durability_text.get_width() - 10, 10))
    WIN.blit(yellow_durability_text, (10, 10))

    WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    WIN.blit(RED_SPACESHIP, (red.x, red.y))

    for bullet in red_bullets:
        pygame.draw.rect(WIN, RED, bullet)

    for bullet in yellow_bullets:
        pygame.draw.rect(WIN, ORANGE, bullet)

    pygame.display.update()


def draw_winner(text):
    draw_text = WINNER_FONT.render(text, True, WHITE)
    WIN.blit(draw_text, (WIDTH // 2 - draw_text.get_width() / 2, HEIGHT / 2 - draw_text.get_height() / 2))
    pygame.display.update()
    pygame.time.delay(7000)


def yellow_movement(keys, yellow):
    if keys[pygame.K_LEFT] and yellow.x - YELLOW_VEL >= 0:
        yellow.x -= YELLOW_VEL
    if keys[pygame.K_RIGHT] and yellow.x + YELLOW_VEL + yellow.width < BORDER.x:
        yellow.x += YELLOW_VEL
    if keys[pygame.K_UP] and yellow.y - YELLOW_VEL >= 0:
        yellow.y -= YELLOW_VEL
    if keys[pygame.K_DOWN] and yellow.y + YELLOW_VEL + SHIP_HEIGHT <= HEIGHT - 15:
        yellow.y += YELLOW_VEL


def red_movement(yellow, red, red_bullets):
    moves_required = yellow.y - red.y  # Calculate the vertical distance
    if moves_required > 0 and red.y + RED_VEL + SHIP_HEIGHT <= HEIGHT - 15:
        red.y += RED_VEL
    elif moves_required < 0 <= red.y - RED_VEL:
        red.y -= RED_VEL

    if abs(moves_required) <= YELLOW_VEL and len(red_bullets) < MAX_BULLETS:
        return True

    return moves_required == 0


def handle_bullets(red, yellow, red_bullets, yellow_bullets):
    for bullet in yellow_bullets:
        bullet.x += BULLET_VEL
        if red.colliderect(bullet):
            sound_effect = pygame.mixer.Sound(os.path.join('Assets', "explosion.wav"))
            sound_effect.play()
            pygame.event.post(pygame.event.Event(RED_HIT))
            yellow_bullets.remove(bullet)

        elif bullet.x > WIDTH:
            yellow_bullets.remove(bullet)
        for red_bullet in red_bullets:
            if red_bullet.colliderect(bullet):
                sound_effect = pygame.mixer.Sound(os.path.join('Assets', "explosion.wav"))
                sound_effect.play()
                yellow_bullets.remove(bullet)
                red_bullets.remove(red_bullet)

    for bullet in red_bullets:
        bullet.x -= BULLET_VEL
        if yellow.colliderect(bullet):
            sound_effect = pygame.mixer.Sound(os.path.join('Assets', "explosion.wav"))
            sound_effect.play()
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            red_bullets.remove(bullet)
        elif bullet.x < 0:
            red_bullets.remove(bullet)


def main():
    red = pygame.Rect(700, 300, SHIP_WIDTH, SHIP_HEIGHT)
    yellow = pygame.Rect(100, 300, SHIP_WIDTH, SHIP_HEIGHT)

    red_bullets = []
    yellow_bullets = []
    SHOT_VOLUME = 0.3

    red_durability = 10
    yellow_durability = 10
    red_last_shot_time = 0

    clock = pygame.time.Clock()
    pygame.mixer.music.load(os.path.join('Assets', "background.mp3"))
    pygame.mixer.music.play(-1)
    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL and len(yellow_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(yellow.x + yellow.width - 2, yellow.y + yellow.height // 2 + 4, 10, 5)
                    sound_effect = pygame.mixer.Sound(os.path.join('Assets', "shot.mp3"))
                    sound_effect.set_volume(SHOT_VOLUME)
                    sound_effect.play()
                    yellow_bullets.append(bullet)

            if event.type == RED_HIT:
                red_durability -= 1
            if event.type == YELLOW_HIT:
                yellow_durability -= 1

        winner_text = ""
        if red_durability <= 0:
            winner_text = "Yellow wins!"

        if yellow_durability <= 0:
            winner_text = "Red wins!"

        if winner_text != "":
            sound_effect = pygame.mixer.Sound(os.path.join('Assets', "victory.wav"))
            sound_effect.play()
            draw_winner(winner_text)
            break

        keys = pygame.key.get_pressed()
        yellow_movement(keys, yellow)

        red_shoot = red_movement(yellow, red, red_bullets)

        # Red spaceship shooting
        if red_shoot and len(red_bullets) < MAX_BULLETS:
            current_time = pygame.time.get_ticks()
            if current_time - red_last_shot_time > 600:  # Add a 500ms delay between shots
                bullet = pygame.Rect(red.x, red.y + red.height // 2 - 2, 10, 5)
                sound_effect = pygame.mixer.Sound(os.path.join('Assets', "shot.mp3"))
                sound_effect.set_volume(SHOT_VOLUME)
                sound_effect.play()
                red_bullets.append(bullet)
                red_last_shot_time = current_time

        handle_bullets(red, yellow, red_bullets, yellow_bullets)

        draw(red, yellow, red_bullets, yellow_bullets, red_durability, yellow_durability)

    main()


if __name__ == "__main__":
    main()
