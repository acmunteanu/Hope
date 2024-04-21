import pygame
from laser import Laser

class Player(pygame.sprite.Sprite):
    def __init__(self, position, image_path, controls):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(midbottom = position)
        self.speed = 5
        self.score = 0
        self.lives = 3
        self.ready = True
        self.laser_time = 0
        self.laser_cooldown = 600        
        self.lasers = pygame.sprite.Group()
        self.laser_sound = pygame.mixer.Sound(r'E:\Project_Hope\Source_Code\assets\spaceship_1_laser.mp3')
        self.laser_sound.set_volume(0.05) 
        self.controls = controls
        
    def increase_score(self, amount):
        self.score += amount
        
    def update_controls(self, controls):
        self.controls = controls

    def get_input(self):
        keys = pygame.key.get_pressed()
        if keys[self.controls['left']]:
            self.rect.x -= self.speed
        if keys[self.controls['right']]:
            self.rect.x += self.speed
        if keys[self.controls['up']]:
            self.rect.y -= self.speed
        if keys[self.controls['down']]:
            self.rect.y += self.speed
        if keys[self.controls['shoot']]:
            self.shoot_laser()
                                   
    def shoot_laser(self):
        if self.ready:
            self.lasers.add(Laser(self.rect.center, -8, self.rect.bottom))
            self.ready = False
            self.laser_time = pygame.time.get_ticks()
            self.laser_sound.play()
        
    def recharge(self):
        if not self.ready:
            if pygame.time.get_ticks() - self.laser_time > self.laser_cooldown:
                self.ready = True
                
    def update(self):
        self.recharge
    
    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.kill()        
