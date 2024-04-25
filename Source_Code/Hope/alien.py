import pygame
import config

class Alien(pygame.sprite.Sprite):
    def __init__(self, color,x ,y, scale_size= (50, 50)):
        super().__init__()
        original_image = pygame.image.load(config.alien_image_path).convert_alpha()
        self.image = pygame.transform.scale(original_image, scale_size)
        self.rect = self.image.get_rect(topleft = (x,y))
        
        if color == 'red': self.value = 100
        elif color == 'green': self.value = 200
        else: self.value = 300
        
    def update(self, direction):
        self.rect.x += direction
        
        
class Miniboss(pygame.sprite.Sprite):
    def __init__(self, side, screen_width, scale_size=(20, 20)):
        super().__init__()
        original_image = pygame.image.load(config.miniboss_image_path).convert_alpha()
        self.image = pygame.transform.scale(original_image, scale_size)
        self.screen_width = screen_width
        
        if side == 'right':
            x = screen_width + 50  # Starts off the right edge
            self.speed = -3  # Moves left
        else:
            x = -50  # Starts off the left edge
            self.speed = 3  # Moves right
        
        self.rect = self.image.get_rect(topleft=(x, 80))
        self.health = 40

        
    def lose_health(self, amount=20):
        self.health -= amount
        if self.health <= 0:
            self.kill()
    
    def update(self):
        self.rect.x += self.speed

