from __future__ import division
import pygame
import random
import sqlite3
from os import path

# Paths
img_dir = path.join(path.dirname(__file__), 'assets')
sound_folder = path.join(path.dirname(__file__), 'sounds')

# Screen Dimensions
WIDTH = 550
HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Pygame Initialization
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RamPage")
clock = pygame.time.Clock()
font_name = pygame.font.match_font('arial')

# Database Setup
DB_PATH = 'game_history.db'

def setup_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            score INTEGER NOT NULL
        )
    ''')
    connection.commit()
    connection.close()

# Functions for Database Interaction
def save_score(username, score):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('INSERT INTO history (username, score) VALUES (?, ?)', (username, score))
    connection.commit()
    connection.close()

def view_history():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('SELECT username, score FROM history ORDER BY score DESC')
    records = cursor.fetchall()
    connection.close()
    return records

# Main Menu
def main_menu():
    global screen
    pygame.mixer.music.load(path.join(sound_folder, "menu.ogg"))
    pygame.mixer.music.play(-1)

    title = pygame.image.load(path.join(img_dir, "main.jpg")).convert()
    title = pygame.transform.scale(title, (WIDTH, HEIGHT), screen)
    screen.blit(title, (0, 0))
    pygame.display.update()

    while True:
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                break
            elif ev.key == pygame.K_b:
                history = view_history()
                screen.fill(BLACK)
                y_offset = 50
                draw_text(screen, "High Scores:", 30, WIDTH / 2, 10)
                for record in history[:10]:  # Show top 10 scores
                    draw_text(screen, f"{record[0]}: {record[1]}", 20, WIDTH / 2, y_offset)
                    y_offset += 30
                pygame.display.update()
                pygame.time.wait(5000)
            elif ev.key == pygame.K_q:
                pygame.quit()
                quit()
        elif ev.type == pygame.QUIT:
            pygame.quit()
            quit()
        else:
            draw_text(screen, "Press [ENTER] To Begin", 30, WIDTH / 2, HEIGHT / 2)
            draw_text(screen, "[B] To View History", 30, WIDTH / 2, (HEIGHT / 2) + 40)
            draw_text(screen, "[Q] To Quit", 30, WIDTH / 2, (HEIGHT / 2) + 80)
            pygame.display.update()

# Draw Text
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# Game Classes (Player, Mob, Bullet, etc.)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_dir, 'playerShip1_orange.png')).convert()
        self.image = pygame.transform.scale(self.image, (86, 69))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.lives = 3

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        elif keystate[pygame.K_RIGHT]:
            self.speedx = 5
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

# Other Classes (e.g., Mob, Bullet) remain similar to the original code...

# Main Game Loop
setup_database()  # Ensure the database is set up
running = True
menu_display = True
username = input("Enter your username: ")  # Get the username once before starting the game

while running:
    if menu_display:
        main_menu()
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path.join(sound_folder, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
        pygame.mixer.music.play(-1)

        menu_display = False
        all_sprites = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        mobs = pygame.sprite.Group()
        for i in range(8):
            mob = Mob()  # Assuming Mob class is defined
            all_sprites.add(mob)
            mobs.add(mob)
        bullets = pygame.sprite.Group()
        score = 0

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()
    # Add collision detection, game logic, etc., as in the original code

    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    pygame.display.flip()

# Save score when the game ends
save_score(username, score)
pygame.quit()
