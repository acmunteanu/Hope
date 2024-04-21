import pygame, sys
from player import Player
import obstacle
from alien import Alien, Miniboss
from random import choice, randint
from laser import Laser
from settings_manager import SettingsManager
import os

os.chdir('E:\\Project_Hope\\Source_Code\\Hope')
pygame.init()

ALIENLASER = pygame.USEREVENT + 1

settings_manager = SettingsManager()
settings = settings_manager.settings

screen_width = 1440
screen_height = 920

if settings['fullscreen']:
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
elif settings['borderless']:
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
else:
    screen = pygame.display.set_mode((screen_width, screen_height))

#Game States
Main_Menu = 0
Settings = 1
Playing = 2
Store = 3
Game_Over = 4
Paused = 5
Victory = 6

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
 
font = pygame.font.Font(None, 36)

#Menu Options
main_menu_options = ['Start Game', 'Settings', 'Quit']
settings_menu_options = ['Volume', 'Fullscreen', 'Borderless', 'Back']
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

def handle_key_events(event):
    global current_menu, selected_option, running, game, settings_manager

    if event.type == pygame.KEYDOWN:
        # Only process menu navigation if in the Main_Menu state
        if game.state == Main_Menu:
            if current_menu == Main_Menu:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(main_menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(main_menu_options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:  # Start game
                        game.reset_game()
                        game.state = Playing
                        pygame.time.set_timer(ALIENLASER, 800)  # Ensure timer for alien shooting starts
                    elif selected_option == 1:  # Enter Settings
                        previous_menus.append(current_menu)
                        current_menu = Settings
                        selected_option = 0  # Reset selection in settings
                    elif selected_option == 2:  # Quit game
                        running = False
            
            elif current_menu == Settings:
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    selected_option = (selected_option - 1 if event.key == pygame.K_UP else selected_option + 1) % len(settings_menu_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    handle_settings_interaction(selected_option)
                elif event.key == pygame.K_ESCAPE:
                    current_menu = previous_menus.pop() if previous_menus else Main_Menu

        # Additional game controls within the game play state
        elif game.state == Playing:
            if event.key == pygame.K_ESCAPE:
                # Pause the game
                previous_menus.append(current_menu)
                current_menu = Paused
                game.state = Paused

        # Handling key events in the paused state
        elif game.state == Paused:
            if event.key == pygame.K_ESCAPE:
                # Resume game
                game.state = Playing
                current_menu = previous_menus.pop() if previous_menus else Main_Menu

def handle_settings_interaction(selected_option):
    global settings_manager, screen, screen_width, screen_height
    setting_name = settings_menu_options[selected_option]
    
    if setting_name == 'Fullscreen':
        new_value = not settings_manager.get_settings('fullscreen')
        settings_manager.update_settings('fullscreen', new_value)
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if new_value else pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    elif setting_name == 'Volume':
        new_volume = (settings_manager.get_settings('volume') + 0.1) % 1.1
        settings_manager.update_settings('volume', new_volume)
        pygame.mixer.music.set_volume(new_volume)
    elif setting_name == 'Borderless':
        new_value = not settings_manager.get_settings('borderless')
        settings_manager.update_settings('borderless', new_value)
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME) if new_value else pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    elif setting_name == 'Back':
        # Assuming 'Back' should take the user back to the previous menu
        global current_menu, previous_menus
        current_menu = previous_menus.pop() if previous_menus else Main_Menu

def toggle_fullscreen():
    # Example implementation for toggling fullscreen
    is_fullscreen = settings_manager.get_settings('fullscreen')
    settings_manager.update_settings('fullscreen', not is_fullscreen)
    pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN if not is_fullscreen else pygame.RESIZABLE)

def adjust_volume():
    # Example volume adjustment
    volume_level = (settings_manager.get_settings('volume') + 0.1) % 1.1
    settings_manager.update_settings('volume', volume_level)
    pygame.mixer.music.set_volume(volume_level)

class Game:
    def __init__(self):
        self.screen = screen
        self.state = Main_Menu
        
        self.live_surface = pygame.image.load(r'E:\Project_Hope\Source_Code\assets\life.png').convert_alpha()
        
        
        self.player1_controls = {
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'shoot': pygame.K_SPACE
        }

        self.player2_controls = {
            'left': pygame.K_a,
            'right': pygame.K_d,
            'up': pygame.K_w,
            'down': pygame.K_s,
            'shoot': pygame.K_y
        }

        self.obstacle_x_positions = [num * (screen_width / 4) for num in range(4)]  # Adjusted for 4 obstacles as an example
        
        self.setup_game()
        
        player1 = Player((screen_width / 2, screen_height - 50), r'E:\Project_Hope\Source_Code\assets\spaceship_basic.png', self.player1_controls)
        self.player_group = pygame.sprite.Group(player1)

        self.player2 = None  # Placeholder for player2

        self.font = pygame.font.Font(None, 36)
        
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

        self.init_audio(settings_manager.get_settings('volume'))
        
    def init_audio(self, volume_level):
        self.music = pygame.mixer.Sound(r'E:\Project_Hope\Source_Code\assets\bg_music.wav')
        self.laser_sound = pygame.mixer.Sound(r'E:\Project_Hope\Source_Code\assets\spaceship_1_laser.mp3')
        self.explosion_sound = pygame.mixer.Sound(r'E:\Project_Hope\Source_Code\assets\alien_laser.mp3')
        
        self.music.set_volume(volume_level)
        self.laser_sound.set_volume(volume_level)
        self.explosion_sound.set_volume(volume_level)
        pygame.mixer.music.set_volume(volume_level)
        
    def add_second_player(self):
        if not self.player2:
            self.player2 = Player(
                (2 * screen_width / 3, screen_height - 50), r'E:\Project_Hope\Source_Code\assets\space_player2.png',
                self.player2_controls)
            self.player_group.add(self.player2)
                   
    def create_obstacle(self, x_start, y_start, offset_x):
        for row_index, row in enumerate(obstacle.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * 6 + offset_x
                    y = y_start + row_index * 6
                    block = obstacle.Block(6, (241, 79, 80), x, y)
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
        if self.aliens.sprites() and self.state == Playing:
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
        #player <> alien
        for player in self.player_group.sprites():
            for laser in player.lasers:
                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    player.increase_score(len(aliens_hit) * 100)
                    laser.kill()
                    self.explosion_sound.play()
                    
        # alien <> player
        for laser in self.alien_lasers:
            player_hit = pygame.sprite.spritecollideany(laser, self.player_group) 
            if player_hit:
                player_hit.lose_life()
                laser.kill() 

        #alive?
        if not self.player_group or all(player.lives <= 0 for player in self.player_group.sprites()):
            print("Game Over. Returning to main menu")
            self.state = Game_Over
            self.handle_game_over()
            
        #victory
        if not self.aliens.sprites():
            self.victory()
            
    def display_game_over_screen(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over", True, (255, 0, 0))
        text_rect = text.get_rect(center = (screen_width / 2, screen_height /2 - 50))
        self.screen.blit(text, text_rect)
        
        score_font = pygame.font.Font(None, 30)
        players = self.player_group.sprites()
        for i, player in enumerate(players):
            score_text = score_font.render(f"Player {i+1} Score: {player.score}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(screen_width / 2, screen_height / 2 + 30 + (i * 20)))
            self.screen.blit(score_text, score_rect)
        
        pygame.display.flip()
        pygame.time.delay(2000)
        
    def wait_for_player_action(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.state = Main_Menu
    
    def reset_game(self):
        # Clear all game components
        self.aliens.empty()
        self.alien_lasers.empty()
        self.blocks.empty()
        self.setup_game()

        # Reinitialize players
        if not hasattr(self, 'player1') or self.player1 not in self.player_group:
            self.player1 = Player((screen_width / 2, screen_height - 50), r'E:\Project_Hope\Source_Code\assets\spaceship_basic.png', self.player1_controls)
            self.player_group.add(self.player1)
        self.player1.lives = 3
        self.player1.score = 0
        self.player1.lasers.empty()

        if self.player2:
            self.player2 = Player((2 * screen_width / 3, screen_height - 50), r'E:\Project_Hope\Source_Code\assets\space_player2.png', self.player2_controls)
            self.player2.score = 0
            self.player2.lives = 3
            self.player2.lasers.empty()
            self.player_group.add(self.player2)

        # Setup the obstacles and aliens as if starting new
        self.create_multiple_obstacle(*self.obstacle_x_positions, x_start=screen_width / 15, y_start=400)
        self.alien_setup(rows=5, cols=10)

        # Restart background music
        pygame.mixer.music.load(r'E:\Project_Hope\Source_Code\assets\bg_music.wav')
        pygame.mixer.music.set_volume(0.02)
        pygame.mixer.music.play(loops=-1)

        # Set the game state back to playing
        self.state = Playing
    
    def setup_game(self):
        # Initialize players, aliens, etc.
        self.player_group = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        
        # Player setup
        self.player1 = Player((screen_width / 2, screen_height - 50), r'E:\Project_Hope\Source_Code\assets\spaceship_basic.png', self.player1_controls)
        self.player_group.add(self.player1)
        
        self.player2 = None  # Ensure player2 is None initially

        # Obstacle and alien setup
        self.create_multiple_obstacle(*self.obstacle_x_positions, x_start=screen_width / 15, y_start=400)
        self.alien_setup(rows=5, cols=10)

        # Miniboss and audio setup
        self.miniboss = pygame.sprite.GroupSingle()
        self.miniboss_spawn_time = randint(40, 80)
        self.init_audio(settings_manager.get_settings('volume'))
            
    def display_lives_and_score(self):      
        original_life_icon = pygame.image.load(r'E:\Project_Hope\Source_Code\assets\life.png').convert_alpha()
        scaled_life_icon = pygame.transform.scale(original_life_icon, (20, 20))
        icon_width = scaled_life_icon.get_width()
        
        for index, player in enumerate(self.player_group.sprites()):
            start_x = 10 if index == 0 else screen_width - (player.lives * icon_width) - 10
            score_text = self.font.render(f"Score: {player.score}", True, (255, 255, 255))
            score_pos_y = 35
            
            #p1 score
            if index == 0:
                score_pos_x = 10
                for i in range(player.lives):
                    self.screen.blit(scaled_life_icon, (start_x + i * icon_width, 10))
                    
            #p2 score
            else:
                score_pos_x = screen_width - score_text.get_width() - 10
                for i in range(player.lives):
                    self.screen.blit(scaled_life_icon, (screen_width - 10 - icon_width * (i + 1), 10))
            
            self.screen.blit(score_text, (score_pos_x, score_pos_y))                         
    
    def victory(self):
        self.state = Victory
        self.display_victory_screen()
                            
    def victory_message(self):
        if not self.aliens.sprites():
            self.state = Victory
            self.display_victory_screen()
    
    def display_victory_screen(self):
        # Clear the screen and display the victory message
        self.screen.fill((0, 0, 0))
        victory_text = "You are victorious! The enemy has been vanquished!"
        victory_font = pygame.font.Font(None, 74)  # You can adjust the font size
        # Render the text: anti-aliasing = True, white color = (255, 255, 255)
        victory_surf = victory_font.render(victory_text, True, (255, 255, 255))
        victory_rect = victory_surf.get_rect(center=(screen_width / 2, screen_height / 2))
        self.screen.blit(victory_surf, victory_rect)
        pygame.display.flip()
       
    def run(self):
        screen.fill((30, 30, 30))
        if self.state == Playing:
            # Define keys for players
            active_players = self.player_group.sprites()
            
            for player in active_players:
                player.get_input()  # This method should use the player's own controls
                player.update()
                player.lasers.update()
                player.lasers.draw(self.screen)
                # Ensure player stays within screen bounds
                player.rect.x = max(0, min(player.rect.x, screen_width - player.image.get_width()))
                player.rect.y = max(0, min(player.rect.y, screen_height - player.image.get_height()))
                player.recharge()
        
            #game entities draw + update       
            self.alien_position_checker()
            self.alien_lasers.update()
            self.alien_lasers.draw(screen)
            self.aliens.update(self.alien_direction)
            self.aliens.draw(screen)
            self.collision_checks()
        
            keys = pygame.key.get_pressed()
            if keys[pygame.K_p]:
                self.add_second_player()
        
            self.miniboss.draw(screen)
            self.miniboss.update()
            self.miniboss_timer()
        
            self.blocks.draw(screen)
               
            self.player_group.draw(screen)
            self.player_group.update()
        
            #UI
            self.display_lives_and_score()
            self.victory_message()
        
        elif self.state == Game_Over:
            self.display_game_over_screen()
            self.wait_for_player_action()   
            
    def handle_game_over(self):
        pygame.mixer.music.stop()
        self.laser_sound.stop()
        self.explosion_sound.stop()
        self.state = Game_Over
        self.display_game_over_screen()
        self.wait_for_player_action()
        
    def check_players_status(self):
        for player in self.player_group.sprites():
            if player.lives <= 0:
                self.player_group.remove(player)
    

def draw_menu(options, selected_option):
    screen.fill((0, 0, 0))
    for i, option in enumerate(options):
        display_text = option
        if option == 'Fullscreen':
            display_text += f": {'ON' if settings_manager.get_settings('fullscreen') else 'OFF'}"
        elif option == 'Volume':
            display_text += f": {int(settings_manager.get_settings('volume') * 100)}%"

        if i == selected_option:
            label = font.render(f"{display_text} +", True, WHITE)
        else:
            label = font.render(display_text, True, GRAY)
        screen.blit(label, (screen_width//2 - label.get_rect().width//2, 300 + i*40))
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
            if game.state == Victory:
                if event.key == pygame.K_RETURN:
                    game.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    game.state == Main_Menu
            else:
                handle_key_events(event)
        elif event.type == ALIENLASER and game.state == Playing:
            game.alien_shoot()


    # Only redraw menus if outside of gameplay (reduces redundant draws)
    if game.state == Victory:
        game.display_victory_screen()
    elif game.state in [Main_Menu, Settings, Store, Game_Over]:
        draw_menu(settings_menu_options if current_menu == Settings else main_menu_options if current_menu == Main_Menu else store_menu_options, selected_option)
    elif game.state == Playing:
        game.run()
        game.display_lives_and_score()
    elif game.state == Game_Over:
        game.display_game_over_screen()
        game.wait_for_player_action()

    
    pygame.display.flip()  # Ensure this is the only place where the screen is updated
    clock.tick(60)

    
pygame.quit()
sys.exit()