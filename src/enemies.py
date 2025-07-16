import pygame
from pygame import Vector2 as vector
from src.sprites import Bullet
from config import *
from src.timer import Timer


def is_line_blocked(start, end, rects):
    for rect in rects:
        if rect.clipline(start, end):
            return True
    return False

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

class Archer(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites, player, sounds, r=400, theta=60):
        super().__init__(groups)
        
        # Animation setup
        self.frames = frames
        self.state = "Walk"
        self.frame_index = 0
        self.image = self.frames["Walk"][0] if "Walk" in self.frames else list(self.frames.values())[0][0]
        self.rect = self.image.get_rect(topleft=pos)
        self.z = ZLAYERS["main"]

        # Movement and collision
        self.direction = 1
        self.facing_right = True
        self.speed = ENEMY_SPEED * 0.4
        self.collision_sprites = collision_sprites
        self.hitbox_rect = self.rect.inflate(-10, -10)
        self.pos = vector(self.rect.topleft)

        # Sight and combat
        self.player = player
        self.sounds = sounds
        self.sight_radius = r
        self.sight_angle = theta
        self.attack_cooldown = Timer(1200)
        self.attack_duration = Timer(600)
        # State flags
        self.attacking = False
        self.dead = False
        self.hurt = False
        self.health = 3  

    def update(self, dt):
        self.facing_right = self.direction > 0
        if self.dead:
            finished = self.animate(dt, "Die")
            if finished:
                self.kill()
        elif self.hurt:
            finished = self.animate(dt, "Hurt")
            if finished:
                self.hurt = False
        elif self.attacking:
            self.attack_duration.update()
            self.animate(dt, "Attack")
            if not self.attack_duration.active:
                self.attacking = False
                self.attack_cooldown.activate()
                self.shoot_arrow()
        elif self.can_see_player():
            if not self.attack_cooldown.active:
                self.start_attack()
            else:
                self.attack_cooldown.update()
        else:
            self.patrol(dt)

        self.hitbox_rect.center = self.rect.center

    def patrol(self, dt):
        self.animate(dt, "Walk")
        self.pos.x += self.direction * self.speed * dt
        self.rect.x = round(self.pos.x)

        next_feet = self.rect.bottomright if self.direction > 0 else self.rect.bottomleft
        ground_check = pygame.Rect(next_feet, (1, 2))
        wall_check_right = pygame.Rect(self.rect.midright, (2, -2))
        wall_check_left = pygame.Rect(self.rect.midleft, (-2, -2))

        collision_rects = [sprite.rect for sprite in self.collision_sprites]

        if ground_check.collidelist(collision_rects) < 0:
            self.direction *= -1

        if wall_check_right.collidelist(collision_rects) > 0 and self.direction > 0:
            self.direction = -1
        elif wall_check_left.collidelist(collision_rects) > 0 and self.direction < 0:
            self.direction = 1

    def can_see_player(self):
        archer_center = vector(self.rect.center)
        player_center = vector(self.player.rect.center)
        to_player = player_center - archer_center

        if to_player.length() > self.sight_radius or to_player.length() == 0:
            return False

        facing = vector(self.direction, 0)
        up = vector(0, -1)
        angle_facing = abs(facing.angle_to(to_player))
        angle_up = abs(up.angle_to(to_player))

        collision_rects = [sprite.rect for sprite in self.collision_sprites]
        if is_line_blocked(archer_center, player_center, collision_rects):
            return False
        
        return (angle_facing < self.sight_angle / 2) or (angle_up < self.sight_angle / 2)

    def start_attack(self):
        self.attacking = True
        self.attack_duration.activate()
        self.frame_index = 0

    def animate(self, dt, state):
        self.frame_index += 10 * dt
        old_midbottom = self.rect.midbottom

        frames = self.frames[state]
        frame_count = len(frames)
        frame = frames[int(self.frame_index) % frame_count]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        self.image = frame
        self.rect = self.image.get_rect()
        self.rect.midbottom = old_midbottom

        return self.frame_index >= frame_count

    def take_damage(self):
        if not self.dead:
            player_x = self.player.rect.centerx
            archer_x = self.rect.centerx
            if (self.direction > 0 and player_x < archer_x) or (self.direction < 0 and player_x > archer_x):
                self.direction *= -1
                self.facing_right = self.direction > 0

            self.health -= 1
            self.hurt = True 
            self.frame_index = 0  
            if self.health <= 0:
                self.dead = True
                self.sounds["archer_death"].play()
            else:
                self.sounds["archer_damage"].play()

    def shoot_arrow(self):
        arrow_img = pygame.image.load('src/assets/images/enemies/archer/arrow.png').convert_alpha()
        archer_center = vector(self.rect.center)
        player_center = vector(self.player.rect.center)
        direction = (player_center - archer_center).normalize()
        speed = 500
        spawn_pos = (self.rect.centerx + 30 * (1 if direction.x >= 0 else -1), self.rect.centery)

        angle = direction.angle_to(vector(1, 0))
        rotated_arrow = pygame.transform.rotate(arrow_img, angle)
        Bullet(pos=spawn_pos, surf=rotated_arrow, direction=direction, speed=speed, groups=[self.groups()[0]], rotating=False, from_who="Enemy")