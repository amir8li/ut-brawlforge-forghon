import pygame
from pygame import Vector2 as vector
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

class Archer(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites, player, sounds, r=400, theta=60):
        super().__init__(groups)
        self.frames = frames  
        self.state = "Walk"  # Walk, attack, hurt, die
        self.frame_index = 0
        self.image = self.frames["Walk"][self.frame_index] if "Walk" in self.frames else list(self.frames.values())[0][0]
        self.rect = self.image.get_rect(topleft=pos)
        self.z = ZLAYERS["main"]

        self.direction = 1
        self.speed = ENEMY_SPEED * 0.7
        self.collision_rects = [sprite.rect for sprite in collision_sprites]
        self.player = player
        self.sounds = sounds
        self.hitbox_rect = self.rect.inflate(-10, -10)

        self.sight_radius = r
        self.sight_angle = theta 
        self.attack_cooldown = Timer(1200)
        self.attack_duration = Timer(600)
        self.attacking = False
        self.dead = False
        self.hurt = False
        self.idle_timer = Timer(500)

    def update(self, dt):
        if self.dead:
            self.animate(dt, "Die")
            return
        if self.hurt:
            self.animate(dt, "Hurt")
            return
        if self.attacking:
            self.attack_duration.update()
            self.animate(dt, "Attack")
            if not self.attack_duration.active:
                self.attacking = False
                self.attack_cooldown.activate()
        elif self.can_see_player():
            if not self.attack_cooldown.active:
                self.start_attack()
            else:
                self.attack_cooldown.update()
                self.animate(dt, "Idle")
        else:
            self.patrol(dt)

        self.hitbox_rect.center = self.rect.center

    def patrol(self, dt):
        self.idle_timer.update()
        self.frame_index += 6 * dt
        self.image = self.frames["Walk"][int(self.frame_index) % len(self.frames["Walk"])]
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect.x += self.direction * self.speed * dt
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

    def can_see_player(self):
        archer_center = vector(self.rect.center)
        player_center = vector(self.player.rect.center)
        to_player = player_center - archer_center
        distance = to_player.length()
        if distance > self.sight_radius:
            return False
        facing = vector(self.direction, 0)
        if distance == 0:
            return False
        angle = facing.angle_to(to_player)
        return abs(angle) < self.sight_angle / 2 and (self.direction > 0) == (to_player.x > 0)

    def start_attack(self):
        self.attacking = True
        self.attack_duration.activate()
        self.frame_index = 0
        # if self.sounds.get("archer_attack"):
        #     self.sounds["archer_attack"].play()

    def animate(self, dt, state):
        if state not in self.frames:
            state = list(self.frames.keys())[0]
        self.frame_index += 6 * dt
        self.image = self.frames[state][int(self.frame_index) % len(self.frames[state])]
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def take_damage(self):
        if not self.dead:
            self.hurt = True
            self.frame_index = 0
            self.dead = True  
            # if self.sounds.get("archer_die"):
            #     self.sounds["archer_die"].play()

class Boss(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player):
        super().__init__(groups)
        self.player = player
        
        # Create a simple rectangle boss
        self.image = pygame.Surface((128, 128))
        self.image.fill((150, 0, 0))  # Dark red color
        self.rect = self.image.get_rect(center=pos)
        self.hitbox_rect = self.rect.inflate(-20, -20)
        self.z = ZLAYERS["main"]
        
        # Boss stats
        self.health = 100
        self.max_health = 100
        self.speed = 100
        self.damage = 2
        
        # Movement
        self.direction = vector(1, 0)
        self.move_timer = 0
        self.attack_timer = Timer(3000)  # Attack every 3 seconds
        
        # Visual feedback
        self.hit_timer = Timer(200)
        
    def update(self, dt):
        self.hit_timer.update()
        self.attack_timer.update()

        self.move_timer += dt
        if self.move_timer > 2.0:
            self.direction.x *= -1
            self.move_timer = 0

        self.rect.x += self.direction.x * self.speed * dt
        
        # Keep boss within bounds
        if self.rect.left < 100:
            self.rect.left = 100
            self.direction.x = 1
        elif self.rect.right > 2400:
            self.rect.right = 2400
            self.direction.x = -1
            
        self.hitbox_rect.center = self.rect.center
        
        # Simple attack pattern
        if not self.attack_timer.active:
            self.attack()
            self.attack_timer.activate()
            
        # Visual feedback when hit
        if self.hit_timer.active:
            self.image.fill((255, 100, 100))  # Light red when hit
        else:
            self.image.fill((150, 0, 0))  # Normal dark red
            
    def attack(self):
        distance = vector(self.rect.center) - vector(self.player.rect.center)
        if distance.length() < 300:  # Attack range
            self.player.damage()
            print("Boss attacks!")
            
    def take_damage(self, damage=10):
        if not self.hit_timer.active:
            self.health -= damage
            self.hit_timer.activate()
            print(f"Boss health: {self.health}/{self.max_health}")
            
            if self.health <= 0:
                self.kill()
                print("Boss defeated!")