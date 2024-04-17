import pygame, sys
from player import Player
import obstacle
from alien import Alien, Miniboss
from random import choice, randint
from laser import Laser
import os
os.chdir('E:\\Project_Hope\\Source_Code\\Hope')

pygame.init()

ALIENLASER = pygame.USEREVENT + 1

#Game States
Main_Menu = 0
Settings = 1
Playing = 2
Store = 3

screen_width = 1440
screen_height = 920
screen = pygame.display.set_mode((screen_width, screen_height))

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

font = pygame.font.Font(None, 36)

#Menu Options
main_menu_options = ['Start Game', 'Settings', 'Store', 'Quit']
settings_menu_options = ['Volume', 'Difficulty', 'Back']
store_menu_options = ['Items here', 'Items there', 'Items everywhere']
selected_option = 0
current_menu = Main_Menu

def draw_menu(options, selected_option):
    screen.fill((0, 0, 0))
    for i, option in enumerate(options):
        if i == selected_option:
            label = font.render(f"{option} +", True, WHITE)
        else:
            label = font.render(option, True, GRAY)
        screen.blit(label, (screen_width//2 - label.get_rect().width//2, 300 + i*40))
    pygame.display.flip()

class Game:
    def __init__(self):
        self.state = Main_Menu
        # Player Setup
        self.player = Player((screen_width / 2, screen_height))
        self.player_group = pygame.sprite.GroupSingle(self.player)
        
        # Health & Score Setup
        self.lives = [3, 3]
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
        music.set_volume(0.02) 
        music.play(loops =-1)
        self.laser_sound = pygame.mixer.Sound(r'E:\Project_Hope\Source_Code\assets\spaceship_1_laser.mp3')
        self.laser_sound.set_volume(0.02)
        self.explosion_sound = pygame.mixer.Sound(r'E:\Project_Hope\Source_Code\assets\alien_laser.mp3')
        self.explosion_sound.set_volume(0.03)
        
                   
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
        for i, player in enumerate(self.player_group.sprites()):
            collision = pygame.sprite.spritecollide(player, self.aliens, True)
            if collision:
                self.lives[i] -= 1
                print(f"Player {i+1} hit! Lives left: {self.lives[i]}")
                if self.lives[i] <= 0:
                    print(f"Player {i+1} is out of lives!")
        
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
                    
        #player and alien collisions
        for player in self.player_group.sprites():
            collision = pygame.sprite.spritecollide(player, self.aliens, False)
            if collision:
                player_index = self.player_group.sprites().index(player)
                self.lives[player_index] -= 1
                for alien in collision:
                    self.aliens.remove(alien)
                print(f"Player {player_index +1} hit! Lives left: {self.lives[player_index]}")
                if self.lives[player_index] <= 0:
                    print(f"Player {player_index + 1} is out of lives!")

                break
        if all(life <= 0 for life in self.lives):
            print("All players out of lives. Game over.")
            self.reset_game()

    def reset_game(self):
         self.lives = [3, 3]
         print("Game reset. Lives: ", self.lives)   
                           
    def display_lives(self):     
        player_positions = [(10, 10), (screen_width - 110, 10)]
            
        for index, lives in enumerate(self.lives):
            for live in range(lives):
                x_pos = player_positions[index][0] + (live * 30)
                y_pos = player_positions[index][1]
                screen.blit(self.live_surface, (x_pos, y_pos))
    
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
        screen.fill((30, 30, 30))
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

def draw_menu(options, selected_option):
    screen.fill((0, 0, 0))
    for i, option in enumerate(options):
        if i == selected_option:
            label = font.render(f"{option} *", True, WHITE)
        else:
            label = font.render(option, True, GRAY)
        screen.blit(label, (screen_width // 2 - label.get_rect().width // 2, 150 + i * 300))
    pygame.display.flip()        

def check_game_over(self):
    if all(life <= 0 for life in self.lives):
        print("Game Over. You have failed this planet...")
        self.reset_game()
    else:
        print("Your wingmate is bollocks. It's all on you now, skipper.")

game = Game()

current_menu = Main_Menu
previous_menus = []
  
#Main Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if previous_menus:
                    current_menu = previous_menus.pop()                    
                continue
                
            if current_menu == Main_Menu:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option -1) % len(main_menu_options if current_menu == Main_Menu else settings_menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(main_menu_options if current_menu == Main_Menu else settings_menu_options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0: #Start game
                        game.state = Playing
                        pygame.time.set_timer(ALIENLASER, 800)
                        previous_menus.append(current_menu)
                        current_menu = None
                    elif selected_option == 1: #Settings
                        previous_menus.append(current_menu)
                        current_menu = Settings
                    elif selected_option == 2: #Store
                        previous_menus.append(current_menu)
                        current_menu = Store                      
                    elif selected_option == 3: #Quit
                        running = False
            
            elif current_menu == Settings:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(settings_menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(settings_menu_options)

            elif current_menu == Store:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(store_menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(store_menu_options)                                
        
        elif event.type == ALIENLASER and game.state == Playing:
            game.alien_shoot()    
    
    if current_menu == Main_Menu:
        draw_menu(main_menu_options, selected_option)
    elif current_menu == Settings:
        draw_menu(settings_menu_options, selected_option)
    elif current_menu == Store:
        draw_menu(store_menu_options, selected_option)
    elif game.state == Playing:
        game.run()    
    
    game.collision_checks()
    
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
sys.exit()
        