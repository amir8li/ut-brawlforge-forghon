import pygame
from pygame.math import Vector2 as vector
from math import sin, cos, radians
from random import randint

from config import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups = None, z=ZLAYERS["main"]):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.old_rect = self.rect.copy()
        self.z = z

class AnimatedSprite(Sprite):
    def __init__(self, pos, frames, groups=None, z=ZLAYERS["main"], animation_speed=ANIMATION_SPEED):
        self.frames = frames
        self.frame_index = 0
        super().__init__(pos, self.frames[self.frame_index], groups, z)
        self.animation_speed = animation_speed

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]
    
    def update(self, dt):
        self.animate(dt)

class Item(AnimatedSprite):
    def __init__(self, type, pos, frames, groups, data):
        super().__init__(pos, frames, groups)
        self.rect.center = pos
        self.type = type
        self.data = data
    
    def activate(self):
        if self.type == "gold":
            self.data.coins += 5
        if self.type == "silver":
            self.data.coins += 1
        if self.type == "diamond":
            self.data.coins += 20
        if self.type == "skull":
            self.data.coins += 50
        if self.type == "potion":
            self.data.health += 1

class ParticleEffectSprite(AnimatedSprite):
    def __init__(self, pos, frames, groups=None):
        super().__init__(pos, frames, groups)
        self.rect.center = pos
        self.z = ZLAYERS["fg"]
    
    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

class MovingSprite(AnimatedSprite):
    def __init__(self, frames, groups, start_pos, end_pos, speed, move_dir, flip=False):
        super().__init__(start_pos, frames, groups)
        if move_dir == 'x':
            self.rect.midleft = start_pos
        else:
            self.rect.midtop = start_pos

        self.start_pos = start_pos
        self.end_pos = end_pos

        self.moving = True
        self.speed = speed
        self.direction = vector(1, 0) if move_dir == 'x' else vector(0, 1)
        self.move_dir = move_dir
        self.flip = flip
        self.reverse = {'x': False, 'y': False}

    def check_bounds(self):
        if self.move_dir == 'x':
            if self.rect.right >= self.end_pos[0] and self.direction.x == 1:
                self.direction.x = -1
                self.rect.right = self.end_pos[0]
            elif self.rect.left <= self.start_pos[0] and self.direction.x == -1:
                self.direction.x = 1
                self.rect.left = self.start_pos[0]
            self.reverse['x'] = True if self.direction.x < 0 else False

        elif self.move_dir == 'y':
            if self.rect.bottom >= self.end_pos[1] and self.direction.y == 1:
                self.direction.y = -1
                self.rect.bottom = self.end_pos[1]
            elif self.rect.top <= self.start_pos[1] and self.direction.y == -1:
                self.direction.y = 1
                self.rect.top = self.start_pos[1]
            self.reverse['y'] = True if self.direction.y > 0 else False

    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.rect.topleft += self.direction * self.speed * dt
        self.check_bounds()
        self.animate(dt)
        if self.flip:
            self.image = pygame.transform.flip(self.image, self.reverse['x'], self.reverse['y'])

class Spike(Sprite):
    def __init__(self, pos, surf, radius, speed, start_angle, end_angle, groups, z=ZLAYERS["main"]):
        self.center = pos
        self.radius = radius
        self.speed = speed
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.angle = start_angle
        self.direction = 1
        self.full_circle = True if self.end_angle == -1 else False

        x = self.center[0] + cos(radians(self.angle)) * self.radius
        y = self.center[1] + sin(radians(self.angle)) * self.radius

        super().__init__((x, y), surf, groups, z)

    def update(self, dt):
        self.angle += self.direction * self.speed * dt

        if not self.full_circle:
            if self.angle >= self.end_angle:
                self.direction = -1
            elif self.angle < self.start_angle:
                self.direction = 1

        x = self.center[0] + cos(radians(self.angle)) * self.radius
        y = self.center[1] + sin(radians(self.angle)) * self.radius
        self.rect.center = (x, y)

class Cloud(Sprite):
    def __init__(self, pos, surf, groups=None, z=ZLAYERS["clouds"]):
        super().__init__(pos, surf, groups, z)
        self.speed = randint(50, 120)
        self.direction = -1
        self.rect.midbottom = pos
    
    def update(self, dt):
        self.rect.x += self.direction * self.speed * dt
        if self.rect.right <= 0:
            self.kill()

class Bullet(Sprite):
    def __init__(self, pos, surf, direction, speed, groups):
        scaled_surf = pygame.transform.scale(surf, (surf.get_width() * 1.5, surf.get_height() * 1.5))
        super().__init__(pos, scaled_surf, groups)
        self.original_image = scaled_surf 
        self.direction = direction
        self.speed = speed
        self.pos = vector(pos)  
        self.rect.center = pos
        self.angle = 0  
        
    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos
        
        self.angle = (self.angle + 500 * dt) % 360  
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center) 
        
        for sprite in self.groups()[0].sprites():
            if sprite != self and hasattr(sprite, 'collision_sprites') and sprite.collision_sprites:
                if pygame.sprite.spritecollide(self, sprite.collision_sprites, False):
                    self.kill()
                    return
            
         
            if sprite != self and hasattr(sprite, 'take_damage') and sprite.state == "chasing":
                if self.rect.colliderect(sprite.hitbox_rect):
                    sprite.take_damage()
                    self.kill()
                    return
        
        world_pos = self.pos + vector(640 - self.rect.center[0], 360 - self.rect.center[1])
        if world_pos.x < -100 or world_pos.x > 2000 or world_pos.y < -100 or world_pos.y > 2000:
            self.kill()