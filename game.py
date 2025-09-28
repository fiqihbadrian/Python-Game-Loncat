import pygame
import sys
import random 
import math 

pygame.init()

WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Loncat - Wildan Parkour")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0) 
YELLOW = (255, 255, 0) 
GREEN = (0, 255, 0) 

font = pygame.font.Font(None, 20) 
warning_font = pygame.font.Font(None, 50) 
win_font = pygame.font.Font(None, 70) 
restart_font = pygame.font.Font(None, 30)

ground = HEIGHT - 40 
mario_width, mario_height = 40, 40
PLAYER_START_POS = pygame.Rect(50, ground - mario_height, mario_width, mario_height) 
PLAYER_SPEED = 5 
PROJECTILE_SPEED = 6 

mario_vel_y = 0
gravity = 1
jump_power = -15

HIT_DURATION = 1000 
hit_timer = 0 
lives = 1 

game_active = True 
on_platform = False 
player_won = False 
player_lost = False 

try:
    mario_image = pygame.image.load("wil.png").convert_alpha() 
    mario_image = pygame.transform.scale(mario_image, (mario_width, mario_height)) 
except pygame.error as e:
    mario_image = None 

ENEMY_WIDTH, ENEMY_HEIGHT = 40, 40
ENEMY_X = WIDTH - ENEMY_WIDTH - 50 
ENEMY_Y = ground - ENEMY_HEIGHT 
enemy = pygame.Rect(ENEMY_X, ENEMY_Y, ENEMY_WIDTH, ENEMY_HEIGHT)

try:
    enemy_image = pygame.image.load("arab.png").convert_alpha()
    enemy_image = pygame.transform.scale(enemy_image, (ENEMY_WIDTH, ENEMY_HEIGHT))
except pygame.error:
    enemy_image = None
    
class Projectile:
    def __init__(self, start_x, start_y, target_x, target_y):
        self.rect = pygame.Rect(start_x, start_y, 10, 5) 
        self.color = RED 

        dx = target_x - start_x
        dy = target_y - start_y
        angle = math.atan2(dy, dx)
        
        self.vel_x = PROJECTILE_SPEED * math.cos(angle)
        self.vel_y = PROJECTILE_SPEED * math.sin(angle)
        
    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

platforms = [
    pygame.Rect(0, ground, WIDTH, 5), 
    pygame.Rect(150, ground - 60, 100, 20),
    pygame.Rect(300, ground - 120, 100, 20),
    pygame.Rect(450, ground - 180, 100, 20),
    pygame.Rect(600, ground - 120, 100, 20),
]

FINISH_RECT = pygame.Rect(ENEMY_X + ENEMY_WIDTH + 10, ENEMY_Y, 5, ENEMY_HEIGHT + 5)

mario = PLAYER_START_POS.copy()
projectiles = [] 
SHOOT_COOLDOWN = 1500 
last_shot_time = pygame.time.get_ticks() 

def restart_game():
    global mario, mario_vel_y, game_active, hit_timer, projectiles, last_shot_time, on_platform, player_won, player_lost, lives
    
    mario = PLAYER_START_POS.copy() 
    mario_vel_y = 0
    
    game_active = True
    on_platform = False
    player_won = False
    player_lost = False
    hit_timer = 0
    lives = 1 
    
    projectiles.clear()
    last_shot_time = pygame.time.get_ticks()

text_surface_mario = font.render("Wildan", True, BLACK)
text_rect_mario = text_surface_mario.get_rect()
text_surface_enemy = font.render("ARAB", True, BLACK)
text_rect_enemy = text_surface_enemy.get_rect()

clock = pygame.time.Clock()
running = True

while running:
    current_time = pygame.time.get_ticks() 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if game_active:
                if event.key == pygame.K_SPACE and (mario.bottom >= ground or on_platform):
                    mario_vel_y = jump_power
            elif player_won or player_lost: 
                if event.key == pygame.K_r: 
                    restart_game()

    if game_active:
        keys = pygame.key.get_pressed() 
        if keys[pygame.K_LEFT]:
            mario.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            mario.x += PLAYER_SPEED

        if mario.left < 0:
            mario.left = 0
        if mario.right > WIDTH:
            mario.right = WIDTH
        
        mario_vel_y += gravity
        mario.y += mario_vel_y
        
        on_platform = False
        for platform in platforms:
            if mario_vel_y > 0 and mario.colliderect(platform):
                if mario.bottom <= platform.top + abs(mario_vel_y):
                    mario.bottom = platform.top 
                    mario_vel_y = 0      
                    on_platform = True 
                    break 

        if mario.bottom >= ground:
            mario.bottom = ground 
            mario_vel_y = 0 
            on_platform = True
        
        if mario.right < enemy.left:
            if current_time - last_shot_time > SHOOT_COOLDOWN:
                new_projectile = Projectile(
                    enemy.centerx, 
                    enemy.centery, 
                    mario.centerx, 
                    mario.centery
                )
                projectiles.append(new_projectile)
                last_shot_time = current_time 

        projectiles_to_keep = []
        for projectile in projectiles:
            projectile.update()
            if projectile.rect.right > 0 and projectile.rect.left < WIDTH: 
                projectiles_to_keep.append(projectile)
            
        projectiles = projectiles_to_keep
        
        for projectile in projectiles:
            if mario.colliderect(projectile.rect):
                hit_timer = current_time 
                projectiles.remove(projectile)
                lives -= 1 

                if lives <= 0:
                    game_active = False 
                    player_lost = True   
                
                break 
                
        if mario.colliderect(FINISH_RECT):
            game_active = False 
            player_won = True   

    screen.fill(WHITE)

    for platform in platforms:
        pygame.draw.rect(screen, (139, 69, 19), platform)

    if mario_image:
        screen.blit(mario_image, mario)
    else:
        pygame.draw.rect(screen, BLUE, mario)

    text_rect_mario.centerx = mario.centerx
    text_rect_mario.bottom = mario.top - 5
    screen.blit(text_surface_mario, text_rect_mario)

    if enemy_image:
        screen.blit(enemy_image, enemy)
    else:
        pygame.draw.rect(screen, RED, enemy) 
    
    text_rect_enemy.centerx = enemy.centerx
    text_rect_enemy.bottom = enemy.top - 5
    screen.blit(text_surface_enemy, text_rect_enemy)
    
    pygame.draw.rect(screen, GREEN, FINISH_RECT) 

    for projectile in projectiles:
        projectile.draw(screen)

    if current_time < hit_timer + HIT_DURATION and game_active:
        warning_text_surface = warning_font.render("TERKENA TEMBAKAN!", True, RED)
        warning_text_rect = warning_text_surface.get_rect()
        warning_text_rect.centerx = WIDTH // 2 
        warning_text_rect.top = 50 
        screen.blit(warning_text_surface, warning_text_rect)

    if player_won:
        win_text = win_font.render("WILDAN MENANG!", True, GREEN)
        win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_text, win_rect)
        
        restart_text = restart_font.render("Tekan 'R' untuk Mulai Ulang", True, BLACK)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_rect)

    if player_lost:
        lose_text = win_font.render("KALAH!", True, RED)
        lose_rect = lose_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(lose_text, lose_rect)

        restart_text = restart_font.render("Tekan 'R' untuk Mulai Ulang", True, BLACK)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()