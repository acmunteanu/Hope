import pygame
from laser import Laser

class Player(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.image.load(r'E:\Project_Hope\Source_Code\assets\spaceship_basic.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom = position)
        self.speed = 5
        self.ready = True
        self.laser_time = 0
        self.laser_cooldown = 600
        
        self.lasers = pygame.sprite.Group()
        self.laser_sound = pygame.mixer.Sound(r'E:\Project_Hope\Source_Code\assets\spaceship_1_laser.mp3')
        self.laser_sound.set_volume(0.5)

    def get_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
            
        if keys[pygame.K_SPACE] and self.ready:
            self.shoot_laser()
            self.ready = False
            self.laser_time = pygame.time.get_ticks()
            self.laser_sound.play()
            
    def recharge(self):
        if not self.ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_cooldown:
                self.ready = True
            
    def shoot_laser(self):
        self.lasers.add(Laser(self.rect.center, -8, self.rect.bottom))
        

