import pygame
import time
import random
pygame.font.init()

WIDTH = 1440
HEIGHT = 920
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Project Hope")

BG = pygame.transform.scale(pygame.image.load("backg.jpg"), (WIDTH, HEIGHT))

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_VEL = 5

PRJ_WIDTH = 10
PRJ_HEIGHT = 20
PRJ_VEL = 20

FONT = pygame.font.SysFont("comicsans", 30)

def draw(player, elapsed_time, prjs):
    WIN.blit(BG, (0, 0))
    
    time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "white")
    WIN.blit(time_text, (10, 10))
    
    pygame.draw.rect(WIN, "red", player)
    
    for prj in prjs:
        pygame.draw.rect(WIN, "white", prj)
    
    pygame.display.update()

def main():
    run = True
    
    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    
    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0
    
    #prj/s = projectile
    prj_add_increment = 2000
    prj_count = 0
    
    prjs = []
    hit = False
    
    while run:
        prj_count += clock.tick(60)
        elapsed_time = time.time() - start_time
        
        if prj_count > prj_add_increment:
            for _ in range(3):
                prj_x = random.randint(0, WIDTH - PRJ_WIDTH)
                prj = pygame.Rect(prj_x, -PRJ_HEIGHT, PRJ_WIDTH, PRJ_HEIGHT)
                prjs.append(prj)
            
            prj_add_increment = max(200, prj_add_increment - 50)    
            prj_count = 0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        #making sure we have boundries left and right as well as button mapping
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_d] and player.x - PLAYER_VEL + player.width  <= WIDTH:
            player.x += PLAYER_VEL
        
        for prj in prjs[:]:
            prj.y += PRJ_VEL
            if prj.y > HEIGHT:
                prjs.remove(prj)
            elif prj.y + prj.height >= player.y and prj.colliderect(player):
                prjs.remove(prj)
                hit = True
                break
            
        if hit:
            lost_text = FONT.render("You Lost!", 1, "white")
            WIN.blit(lost_text, (WIDTH/2 - lost_text.get_width()*2, HEIGHT - lost_text.get_height()*2))
            pygame.display.update()
            pygame.time.delay(4000)
            break
        
        draw(player, elapsed_time, prjs)
        
    pygame.quit()

if __name__ == "__main__":
    main()