import pygame

from config import *
from src.timer import Timer

class Tooth(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.z = ZLAYERS["main"]

        self.direction = 1
        self.speed = ENEMY_SPEED
        self.collision_rects = [sprite.rect for sprite in collision_sprites]

        self.hit_timer = Timer(350)

    def reverse(self):
        if not self.hit_timer.active:
            self.direction *= -1
            self.hit_timer.activate()

    def update(self, dt):
        self.hit_timer.update()

        # animation
        self.frame_index += 6 * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

        # movement
        self.rect.x += self.direction * self.speed * dt

        # reverse direction
        floor_rect_right = pygame.Rect(self.rect.bottomright, (1, 1))
        floor_rect_left = pygame.Rect(self.rect.bottomleft, (-1, 1))
        rect_right = pygame.Rect(self.rect.bottomright, (1, -1))
        rect_left = pygame.Rect(self.rect.bottomleft, (-1, -1))

        if floor_rect_right.collidelist(self.collision_rects) < 0 and self.direction > 0:
            self.direction = -1
        elif floor_rect_left.collidelist(self.collision_rects) < 0 and self.direction < 0:
            self.direction = 1
        elif rect_right.collidelist(self.collision_rects) > 0 and self.direction > 0:
            self.direction = -1
        elif rect_left.collidelist(self.collision_rects) > 0 and self.direction < 0:
            self.direction = 1

class Bombastic(pygame.sprite.Sprite):
    def __init__(self, pos, frames, explosion_frames, dead_frames, groups, player, sounds):
        super().__init__(groups)
        self.frames = frames
        self.explosion_frames = explosion_frames
        self.dead_frames = dead_frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox_rect = self.rect.inflate(-10, -10)  
        self.z = ZLAYERS["main"]

        self.speed = ENEMY_SPEED * 0.5  
        self.player = player
        self.sounds = sounds
        
        self.state = "chasing"  # chasing, exploding, dead
        self.explosion_timer = Timer(500) 
        self.dead_timer = Timer(1000) 
        
        self.direction = pygame.math.Vector2(0, 0)

    def update(self, dt):
        if self.state == "chasing":
            self.chase_player(dt)
        elif self.state == "exploding":
            self.explode(dt)
        elif self.state == "dead":
            self.die(dt)

    def chase_player(self, dt):
        player_center = pygame.math.Vector2(self.player.rect.center)
        enemy_center = pygame.math.Vector2(self.rect.center)
        direction = player_center - enemy_center
        
        distance_to_player = direction.length()
        
        if distance_to_player == 0:
            return
            
        self.direction = direction.normalize()
        
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt
        
        self.hitbox_rect.center = self.rect.center
        
        if self.rect.colliderect(self.player.hitbox_rect):
            self.start_explosion()
            return

        self.frame_index += 6 * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        
        if self.direction.x < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def start_explosion(self):
        self.state = "exploding"
        self.frame_index = 0
        self.explosion_timer.activate()
    
        if self.sounds["bombastic_explosion"]:
            self.sounds["bombastic_explosion"].play()

    def explode(self, dt):
        self.explosion_timer.update()
        
        if self.frame_index < len(self.explosion_frames):
            self.image = self.explosion_frames[int(self.frame_index)]
            self.frame_index += 8 * dt  
            
            if self.rect.colliderect(self.player.hitbox_rect):
                self.player.damage()
        
        if self.explosion_timer.active == False:
            self.kill()

    def die(self, dt):
        self.dead_timer.update()
        
        if self.frame_index < len(self.dead_frames):
            self.image = self.dead_frames[int(self.frame_index)]
            self.frame_index += 6 * dt
        
        if self.sounds["bombastic_explosion"]:
            self.sounds["bombastic_explosion"].play()

        if self.dead_timer.active == False:
            self.kill()

    def take_damage(self):
        if self.state == "chasing":
            self.state = "dead"
            self.frame_index = 0
            self.dead_timer.activate()