import pygame
from pygame import Vector2 as vector
from src.sprites import Bullet
from config import *
from src.timer import Timer

import openai

def is_line_blocked(start, end, rects):
    for rect in rects:
        if rect.clipline(start, end):
            return True
    return False

class Tooth(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites, sounds, player):
        super().__init__(groups)
        self.frames = frames
        self.sounds = sounds
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox_rect = self.rect.inflate(-10, -10)
        self.z = ZLAYERS["main"]
        self.player = player

        self.direction = 1
        self.speed = ENEMY_SPEED
        self.collision_rects = [sprite.rect for sprite in collision_sprites]

        min_dist = float('inf')
        new_y = self.rect.y
        for platform_rect in self.collision_rects:
            if platform_rect.left <= self.rect.centerx <= platform_rect.right:
                platform_top = platform_rect.top
                if platform_top >= self.rect.bottom and (platform_top - self.rect.bottom) < min_dist:
                    min_dist = platform_top - self.rect.bottom
                    new_y = platform_top - self.rect.height
        if min_dist != float('inf'):
            self.rect.y = new_y
            self.hitbox_rect.center = self.rect.center

        self.hit_timer = Timer(350)

        self.health = 2  
        self.dead = False
        self.hurt = False
        self.hurt_timer = Timer(300)
        self.death_sound_played = False
        self.death_timer = Timer(400)
        
    def take_damage(self):
        if not self.dead:
            self.health -= 1
            self.hurt = True
            self.hurt_timer.activate()
            self.frame_index = 0
            if self.health <= 0:
                self.dead = True
                self.death_timer.activate()
            
            player_x = self.player.rect.centerx
            enemy_x = self.rect.centerx
            if (self.direction > 0 and player_x < enemy_x) or (self.direction < 0 and player_x > enemy_x):
                self.direction *= -1

    def update(self, dt):
        self.hit_timer.update()
        self.hurt_timer.update()
        self.death_timer.update()

        # animation
        self.frame_index += 6 * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

        # flicker logic
        if self.dead:
            if not self.death_sound_played:
                self.sounds["tooth_death"].play()
                self.death_sound_played = True
            if self.hurt_timer.active:
                if int(pygame.time.get_ticks() / 100) % 2 == 0:
                    self.image.set_alpha(100)
                else:
                    self.image.set_alpha(255)
            if not self.death_timer.active:
                self.kill()
            return
        elif self.hurt:
            self.sounds["tooth_damage"].play()
            if self.hurt_timer.active:
                if int(pygame.time.get_ticks() / 100) % 2 == 0:
                    self.image.set_alpha(100)
                else:
                    self.image.set_alpha(255)
            else:
                self.hurt = False
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)

        # movement
        self.rect.x += self.direction * self.speed * dt
        self.hitbox_rect.center = self.rect.center

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

        collision_rects = [sprite.rect for sprite in collision_sprites]
        min_dist = float('inf')
        new_y = self.rect.y
        for platform_rect in collision_rects:
            if platform_rect.left <= self.rect.centerx <= platform_rect.right:
                platform_top = platform_rect.top
                if platform_top >= self.rect.bottom and (platform_top - self.rect.bottom) < min_dist:
                    min_dist = platform_top - self.rect.bottom
                    new_y = platform_top - self.rect.height
        if min_dist != float('inf'):
            OFFSET = 6 #
            self.rect.y = new_y + OFFSET
            self.hitbox_rect.center = self.rect.center
            self.pos.y = self.rect.y

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
                self.sounds["archer_death"].set_volume(1)
                self.sounds["archer_death"].play()
            else:
                self.sounds["archer_wizard_damage"].play()

    def shoot_arrow(self):
        arrow_img = pygame.image.load('src/assets/images/enemies/archer/arrow.png').convert_alpha()
        archer_center = vector(self.rect.center)
        player_center = vector(self.player.rect.center)
        direction = (player_center - archer_center).normalize()
        speed = 500
        spawn_pos = (self.rect.centerx + 30 * (1 if direction.x >= 0 else -1), self.rect.centery)

        angle = direction.angle_to(vector(1, 0))
        rotated_arrow = pygame.transform.rotate(arrow_img, angle)
        Bullet(pos=spawn_pos, surf=rotated_arrow, direction=direction, speed=speed, groups=[self.player.all_sprites], rotating=False, from_who="Enemy")

class IceBullet(Bullet):
    def __init__(self, pos, surf, direction, speed, groups, player, freeze_duration=2000):
        super().__init__(pos, surf, direction, speed, groups, rotating=False, from_who="Enemy")
        self.player = player
        self.freeze_duration = freeze_duration

    def update(self, dt):
        super().update(dt)
        if self.rect.colliderect(self.player.hitbox_rect):
            if hasattr(self.player, 'freeze'):
                self.player.freeze(self.freeze_duration)
            self.kill()

class IceWizard(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, sounds, shoot_cooldown=3000):
        super().__init__(groups)
        self.frames = frames  
        self.state = "Idle"
        self.frame_index = 0
        self.image = self.frames["Idle"][0]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox_rect = self.rect.inflate(-10, -10)
        self.z = ZLAYERS["main"]
        self.player = player
        self.sounds = sounds
        self.shoot_cooldown = Timer(shoot_cooldown)
        self.attacking = False
        self.attack_timer = Timer(400)
        self.dead = False
        self.hurt = False
        self.health = 3
        self.facing_right = True

    def update(self, dt):
        if self.player.rect.centerx < self.rect.centerx:
            self.facing_right = False
        else:
            self.facing_right = True
        if self.dead:
            finished = self.animate(dt, "Die")
            if finished:
                self.kill()
        elif self.hurt:
            finished = self.animate(dt, "Hurt")
            if finished:
                self.hurt = False
        elif self.attacking:
            self.attack_timer.update()
            finished = self.animate(dt, "Attack")
            if not self.attack_timer.active:
                self.attacking = False
        else:
            self.animate(dt, "Idle")
            if not self.shoot_cooldown.active:
                self.shoot_at_player()
                self.shoot_cooldown.activate()
            else:
                self.shoot_cooldown.update()

    def animate(self, dt, state):
        self.frame_index += 8 * dt
        frames = self.frames[state]
        frame_count = len(frames)
        frame = frames[int(self.frame_index) % frame_count]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame
        self.rect = self.image.get_rect(center=self.rect.center)
        return self.frame_index >= frame_count

    def take_damage(self):
        if not self.dead:
            self.health -= 1
            self.hurt = True
            self.frame_index = 0
            if self.health <= 0:
                self.dead = True
                self.sounds["wizard_death"].play()
            else:
                self.sounds["archer_wizard_damage"].play()

    def shoot_at_player(self):
        wizard_center = vector(self.rect.center)
        player_center = vector(self.player.rect.center)
        direction = (player_center - wizard_center).normalize()
        speed = 400
        spawn_pos = self.rect.center
        snowflake_img = pygame.image.load('src/assets/images/enemies/ice wizard/snowflake.png').convert_alpha()
        snowflake_img = pygame.transform.scale(snowflake_img, (snowflake_img.get_width() // 1.5, snowflake_img.get_height() // 1.5))
        IceBullet(pos=spawn_pos, surf=snowflake_img, direction=direction, speed=speed, groups=[self.player.all_sprites], player=self.player)
        if self.sounds.get("ice_wizard_attack"):
            self.sounds["ice_wizard_attack"].play()
        self.attacking = True
        self.attack_timer = Timer(400)
        self.attack_timer.activate()
        self.frame_index = 0

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


        # OpenAI client for boss dialog
        self.client = openai.OpenAI(api_key="tpsg-RUANDCn04b8K0A7qY78jOTiPps6ldJO", base_url="https://api.metisai.ir/openai/v1")
        self.talk_message = None
        self.talk_thread = None
        self.talk_result_queue = None
        self.talk_display_timer = Timer(6000)

    def say(self, prompt):
        import threading, queue
        if self.talk_thread and self.talk_thread.is_alive():
            return  # Already talking
        self.talk_result_queue = queue.Queue()
        def fetch():
            import traceback
            try:
                model = "gpt-4o-mini"
                messages = [
                    {"role": "system", "content": "You are a video game boss. Be dramatic and taunt the player."},
                    {"role": "user", "content": prompt}
                ]
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=50,
                    timeout=10
                )
                reply = response.choices[0].message.content
                print(f"Boss says: {reply}")
            except Exception as e:
                traceback.print_exc()
                reply = f"Error: {e}"
            self.talk_result_queue.put(reply)
        self.talk_thread = threading.Thread(target=fetch)
        self.talk_thread.start()

    def update(self, dt):
        self.hit_timer.update()
        self.attack_timer.update()

        # Check for new OpenAI message
        if self.talk_result_queue and not self.talk_result_queue.empty():
            self.talk_message = self.talk_result_queue.get()
            self.talk_display_timer.activate()

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

    def draw_talk(self, surface, font):
        if self.talk_message and self.talk_display_timer.active:
            # Smaller font for dialog
            small_font = pygame.font.Font(font.get_name(), 24) if hasattr(font, 'get_name') else pygame.font.SysFont(None, 24)
            rect_width = 340
            rect_height = 70
            rect_x = 20
            rect_y = 20
            # Brighter yellow for text
            bright_yellow = (255, 255, 120)
            shadow_color = (180, 180, 60)

            # Word wrap the message
            def wrap_text(text, font, max_width):
                words = text.split(' ')
                lines = []
                current = ''
                for word in words:
                    test = current + (' ' if current else '') + word
                    if font.size(test)[0] <= max_width:
                        current = test
                    else:
                        if current:
                            lines.append(current)
                        current = word
                if current:
                    lines.append(current)
                return lines

            lines = wrap_text(self.talk_message, small_font, rect_width - 20)

            # Draw each line with shadow and bright text, no border or background
            y = rect_y + 10
            for line in lines:
                shadow = small_font.render(line, True, shadow_color)
                text = small_font.render(line, True, bright_yellow)
                shadow_rect = shadow.get_rect(topleft=(rect_x + 12, y + 2))
                text_rect = text.get_rect(topleft=(rect_x + 10, y))
                surface.blit(shadow, shadow_rect)
                surface.blit(text, text_rect)
                y += small_font.get_height() + 2
            
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

            self.say("You hit the boss! Respond as a taunting boss.")
            if self.health <= 0:
                self.kill()
                print("Boss defeated!")