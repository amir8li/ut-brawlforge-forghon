import pygame
from config import ZLAYERS

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, power_type, pos, image, duration=8000):
        super().__init__()
        self.power_type = power_type
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.spawn_time = pygame.time.get_ticks()
        self.duration = duration
        self.z = ZLAYERS["main"]

    def update(self, dt):
        elapsed = pygame.time.get_ticks() - self.spawn_time
        if self.duration - elapsed < 1000:
            self.image.set_alpha(100 if elapsed // 200 % 2 == 0 else 255)
        else:
            self.image.set_alpha(255)
        if elapsed > self.duration:
            self.kill()

