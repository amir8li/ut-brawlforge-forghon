import pygame
from src.timer import Timer
import math
from config import ZLAYERS

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, pos, power_type, surf, groups, duration=10000):
        super().__init__(groups)
        self.power_type = power_type
        self.original_image = surf
        self.image = surf.copy()
        self.rect = self.image.get_rect(center=pos)
        self.z = ZLAYERS["main"]

        self.pos = pygame.math.Vector2(pos)
        self.initial_y = pos[1]
        self.bob_speed = 2
        self.bob_amplitude = 10
        self.angle = 0

        self.lifetime_timer = Timer(duration, self.kill)
        self.lifetime_timer.activate()
        
        self.creation_time = pygame.time.get_ticks()
        self.flicker_start_time = 3000 

    def update(self, dt):
        self.lifetime_timer.update()

        self.angle += self.bob_speed * dt
        self.rect.y = self.initial_y + self.bob_amplitude * math.sin(self.angle)

        self.flicker()

    def flicker(self):
        elapsed_time = pygame.time.get_ticks() - self.creation_time
        remaining_time = self.lifetime_timer.duration - elapsed_time

        if remaining_time < self.flicker_start_time:
            if int(pygame.time.get_ticks() / 150) % 2 == 0:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)
