import pygame, sys
from player import Player
import obstacle
from alien import Alien, Miniboss
from random import choice, randint
from laser import Laser
import os
os.chdir('E:\\Project_Hope\\Source_Code\\Hope')

#Game States
Main_Menu = 0
Settings = 1
Playing = 2

class Game:
    def __init__(self):
        self.state = Main_Menu
        # Player Setup
        self.player = Player((screen_width / 2, screen_height))
        self.player_group = pygame.sprite.GroupSingle(self.player)
        
        # Health & Score Setup
        self.lives = 3
        self.live_surface = pygame.image.load(r'E:\Project_Hope\Source_Code\assets\spaceship_basic.png').convert_alpha()
        self.live_x_start_pos = screen_width - (self.live_surface.get_size()[0] * 2 + 20)
        self.score = 0
        self.font = pygame.font.Font(r'E:\Project_Hope\Source_Code\assets\rnbw.otf', 30)
        
        # Obstacle Setup
        self.shape = obstacle.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        self.obstacle_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.create_multiple_obstacle(*self.obstacle_x_positions, x_start=screen_width / 15, y_start=400)
        
        # Alien Setup
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.alien_setup(rows = 5, cols = 10)
        self.alien_direction = 1
        
    
        # Miniboss Setup
        self.miniboss = pygame.sprite.GroupSingle()
        self.miniboss_spawn_time = randint (40, 80)
        
        # Audio
        music = pygame.mixer.Sound(r'E:\Project_Hope\Source_Code\assets\bg_music.wav')
        music.set_volume(0.2)
        music.play(loops =-1)
        self.laser_sound = pygame.mixer.Sound(r'E:\Project_Hope\Source_Code\assets\spaceship_1_laser.mp3')
        self.laser_sound.set_volume(0.5)
        self.explosion_sound = pygame.mixer.Sound(r'E:\Project_Hope\Source_Code\assets\alien_laser.mp3')
        self.explosion_sound.set_volume(0.3)
    
    def draw_main_menu(self):
        pass
    
    def draw_settings(self):
        pass
    
            
    def create_obstacle(self, x_start, y_start, offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = obstacle.Block(self.block_size,(241,79,80),x, y)
                    self.blocks.add(block)
        
    def create_multiple_obstacle(self, *offset, x_start, y_start):
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)
    
    def alien_setup(self, rows, cols, x_distance=60, y_distance=48, x_offset = 470, y_offset = 100):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset
                
                if row_index == 0:
                    alien_sprite = Alien ('beige', x,  y)
                elif 1 <= row_index <= 2: 
                    alien_sprite = Alien ('green', x, y)
                else:
                    alien_sprite = Alien ('blue', x, y)
                self.aliens.add(alien_sprite)
                
    def alien_position_checker(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= screen_width:
                self.alien_direction = -1
                self.alien_move_down(2)
            elif alien.rect.left <= 0:
                self.alien_direction = 1
                self.alien_move_down(2)
                
    def alien_move_down(self, distance):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance
    
    def alien_shoot(self):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, 6, screen_height)
            self.alien_lasers.add(laser_sprite)
            self.laser_sound.play()
    
    def miniboss_timer(self):
        self.miniboss_spawn_time -= 1
        if self.miniboss_spawn_time <= 0:
            self.miniboss.add(Miniboss(choice(['right', 'left']), screen_width))
            self.miniboss_spawn_time = randint(400, 800)
    
    def collision_checks(self):
        # player lasers
        if self.player.lasers:
            for laser in self.player.lasers:
                # obstacle
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()
                    
                # aliens
                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.value
                    laser.kill()
                    self.explosion_sound.play()
                                  
                # miniboss
                if pygame.sprite.spritecollide(laser, self.miniboss, True):
                    self.score += 500
                    laser.kill()
                    
        #alien lasers
        if self.alien_lasers:
            for laser in self.alien_lasers:
                #obstacle
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill() 
                
                #player
                if pygame.sprite.spritecollide(laser, self.player_group, False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        pygame.quit()
                        sys.exit()
        
        # aliens
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)
                    
                if pygame.sprite.spritecollide(alien, self.player_group, True):
                    pygame.quit()
                    sys.exit()
                           
    def display_lives(self):
        for live in range(self.lives - 1):
            x = self.live_x_start_pos + (live * (self.live_surface.get_size()[0] + 10))
            screen.blit(self.live_surface,(x,8))
    
    def display_score(self):
        score_surf = self.font.render(f'score: {self.score}', False, 'white')
        score_rect = score_surf.get_rect(topleft = (10,0))
        screen.blit(score_surf, score_rect)
        
    def victory_message(self):
        if not self.aliens.sprites():
            victory_surf = self.font.render('You won', False, 'white')
            victory_rect = victory_surf.get_rect(center = (screen_width / 2, screen_height / 2))
            screen.blit(victory_surf, victory_rect)    
        
    def run(self):
        self.alien_position_checker()
        self.alien_lasers.update()
        self.alien_lasers.draw(screen)
        self.aliens.update(self.alien_direction)
        self.aliens.draw(screen)
        self.collision_checks()
        
        
        self.miniboss.draw(screen)
        self.miniboss.update()
        self.miniboss_timer()
        
        self.player.get_input()
        self.player_group.update()
        self.blocks.draw(screen)
        
        self.player.lasers.draw(screen)
        for player in self.player_group:
            player.rect.x = max(0, min(player.rect.x, screen_width - player.image.get_width()))
            player.rect.y = max(0, min(player.rect.y, screen_height - player.image.get_height()))
        self.player_group.draw(screen)
        self.player.recharge()
        self.player.lasers.update()
        
        self.display_lives()
        self.display_score()
        self.victory_message()
        
    
if __name__ == '__main__':
    pygame.init()
    screen_width = 1440
    screen_height = 920
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    
    game = Game()
    
    ALIENLASER = pygame.USEREVENT +1
    pygame.time.set_timer(ALIENLASER, 800)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                game.alien_shoot()
        
        screen.fill((30,30,30))
        
        game.run()
        
        if game.state == Main_Menu:
            game.draw_main_menu()
        elif game.state == Settings:
            game.draw_settings()
        elif game.state == Playing:
            game.run()
        pygame.display.flip()
        clock.tick(60)