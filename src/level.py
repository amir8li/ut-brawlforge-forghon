import pygame
import os
from pygame import Vector2 as vector
from random import uniform
from config import *
from src.sprites import Sprite, MovingSprite, AnimatedSprite, Item, Spike, ParticleEffectSprite
from src.player import Player
from src.groups import AllSprites
from src.enemies import Tooth, Bombastic, Archer, IceWizard
from src.powerup import PowerUp

class Level:
    def __init__(self, tmx_map, level_frames, audio_files, data, powerup_locations=None):
        self.data = data
        self.tmx_map = tmx_map
        self.display = pygame.display.get_surface()
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_bottom = tmx_map.height * TILE_SIZE
        self.multiplayer = len(data) > 1
        self.powerup_locations = powerup_locations or {}
        self.audio_files = audio_files

        tmx_level_properties = tmx_map.get_layer_by_name("Data")[0].properties
        bg_tile = level_frames["bg_tiles"][tmx_level_properties["bg"]] if tmx_level_properties["bg"] else None
        clouds_dict = {"large": level_frames["cloud_large"], "small": level_frames["cloud_small"]}

        self.all_sprites = AllSprites(
            tmx_map.width, tmx_map.height,
            clouds_dict, tmx_level_properties["horizon_line"], bg_tile
        )

        self.collision_sprites = pygame.sprite.Group()
        self.semi_collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.tooth_sprites = pygame.sprite.Group()
        self.bombastic_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        self.ice_wizard_sprites = pygame.sprite.Group()
        self.archer_sprites = pygame.sprite.Group()


        self.initial_item_count = 0
        self.powerup_sprites = pygame.sprite.Group()
        self.level_frames = level_frames
        self.coin_sound = audio_files['coin']
        self.coin_sound.set_volume(0.3)
        self.players = []

        self.setup(tmx_map, level_frames, audio_files)

        if self.multiplayer:
            self.spawn_powerups()

    def setup(self, tmx_map, level_frames, audio_files):
        for layer in ["BG", "Terrain", "FG", "Platforms"]:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == "Terrain": groups.append(self.collision_sprites)
                elif layer == "Platforms": groups.append(self.semi_collision_sprites)
                match layer:
                    case "BG": z = ZLAYERS["bg tiles"]
                    case "FG": z = ZLAYERS["fg"]
                    case _: z = ZLAYERS["main"]
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, groups, z)

        for obj in tmx_map.get_layer_by_name("BG details"):
            if obj.name == "static":
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, z=ZLAYERS["bg tiles"])
            else:
                AnimatedSprite((obj.x, obj.y), level_frames[obj.name], self.all_sprites, ZLAYERS["bg tiles"])
                if obj.name == "candle":
                    AnimatedSprite((obj.x, obj.y) + vector(-20, -20), level_frames["candle_light"], self.all_sprites, ZLAYERS["bg tiles"])

        player_positions = []
        for obj in tmx_map.get_layer_by_name("Objects"):
            if obj.name == "player":
                player_positions.append((obj.x, obj.y))
            elif obj.name in ("barrel", "crate"):
                Sprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
            else:
                frames = level_frames[obj.name] if "palm" not in obj.name else level_frames["palms"][obj.name]
                if obj.name == "floor_spike" and obj.properties.get("inverted", False):
                    frames = [pygame.transform.flip(frame, False, True) for frame in frames]
                groups = [self.all_sprites]
                if obj.name in ("palm_small", "palm_large"):
                    groups.append(self.semi_collision_sprites)
                if obj.name in ("saw", "floor_spike"):
                    groups.append(self.damage_sprites)
                z = ZLAYERS["main"] if "bg" not in obj.name else ZLAYERS["bg details"]
                anim_speed = ANIMATION_SPEED if "palm" not in obj.name else 6 + uniform(-1, 1)
                AnimatedSprite((obj.x, obj.y), frames, groups, z, anim_speed)

        if not player_positions:
            player_positions = [(100, 200), (300, 200)]

        for i, data in enumerate(self.data):
            base_pos = player_positions[i % len(player_positions)]
            spawn_offset = 100 * i
            player_pos = (base_pos[0] + spawn_offset, base_pos[1])
            player = Player(
                pos=player_pos,
                groups=self.all_sprites,
                collision_sprites=self.collision_sprites,
                semi_collision_sprites=self.semi_collision_sprites,
                frames=level_frames["player"][i] if isinstance(level_frames["player"], list) else level_frames["player"],
                sounds=self.audio_files,
                data=data,
                player_id=i
            )
            self.players.append(player)

            anim_speed = ANIMATION_SPEED if not "palm" in obj.name else 6 + uniform(-1, 1)
            AnimatedSprite((obj.x, obj.y), frames, groups, z, anim_speed)

        # enemies
        for obj in tmx_map.get_layer_by_name("Enemies"):
            if obj.name == "tooth":
                Tooth((obj.x, obj.y), level_frames["tooth"], (self.all_sprites, self.damage_sprites, self.tooth_sprites), self.collision_sprites, audio_files, self.players[0])
            elif obj.name == "bombastic":
                Bombastic((obj.x, obj.y), level_frames["bombastic"], level_frames["bombastic_explosion"], level_frames["bombastic_dead"], (self.all_sprites, self.damage_sprites, self.bombastic_sprites), self.players[0], audio_files)
            elif obj.name == "archer":
                Archer((obj.x, obj.y), level_frames["archer"], (self.all_sprites, self.damage_sprites, self.archer_sprites), self.collision_sprites, self.players[0], audio_files)
            elif obj.name == "ice wizard":
                frames = level_frames["ice_wizard"]
                IceWizard((obj.x, obj.y), frames, (self.all_sprites, self.damage_sprites, self.ice_wizard_sprites), self.players[0], audio_files)

        # moving objects
        for obj in tmx_map.get_layer_by_name("Moving Objects"):
            if obj.name == "spike":
                surf = level_frames["spike"]
                if isinstance(surf, list):
                    surf = surf[0]
                Spike(
                    pos=(obj.x + obj.width / 2, obj.y + obj.height / 2),
                    surf=surf,
                    radius=obj.properties.get("radius", 100),
                    speed=obj.properties.get("speed", 50),
                    start_angle=obj.properties.get("start_angle", 0),
                    end_angle=obj.properties.get("end_angle", -1),
                    groups=(self.all_sprites, self.damage_sprites),
                )
                for i in range(0, obj.properties.get("radius", 100), 20):
                    Spike(
                        pos=(obj.x + obj.width / 2, obj.y + obj.height / 2),
                        surf=level_frames["spike_chain"],
                        radius=i,
                        speed=obj.properties.get("speed", 50),
                        start_angle=obj.properties.get("start_angle", 0),
                        end_angle=obj.properties.get("end_angle", -1),
                        groups=self.all_sprites,
                        z=ZLAYERS["bg details"],
                    )
            else:
                frames = level_frames[obj.name]
                if isinstance(frames, pygame.Surface):
                    frames = [frames]
                is_platform = obj.properties.get("platform", False)
                is_harmful = obj.properties.get("harmful", False)
                groups = [self.all_sprites]
                if is_platform:
                    groups.append(self.semi_collision_sprites)
                elif is_harmful:
                    groups.append(self.damage_sprites)
                else:
                    groups.append(self.collision_sprites)

                if obj.width > obj.height:
                    move_dir = 'x'
                    start_pos = (obj.x, obj.y + obj.height // 2)
                    end_pos = (obj.x + obj.width, obj.y + obj.height // 2)
                else:
                    move_dir = 'y'
                    start_pos = (obj.x + obj.width // 2, obj.y)
                    end_pos = (obj.x + obj.width // 2, obj.y + obj.height)

                speed = obj.properties.get("speed", 1)
                flip = obj.properties.get("flip", False)
                MovingSprite(frames, tuple(groups), start_pos, end_pos, speed, move_dir, flip)

                if obj.name == "saw":
                    chain_surf = level_frames["saw_chain"]
                    if move_dir == "x":
                        y = start_pos[1] - chain_surf.get_height() // 2
                        for x in range(int(start_pos[0]), int(end_pos[0]), 20):
                            Sprite((x, y), chain_surf, self.all_sprites, ZLAYERS["bg details"])
                    else:
                        x = start_pos[0] - chain_surf.get_width() // 2
                        for y in range(int(start_pos[1]), int(end_pos[1]), 20):
                            Sprite((x, y), chain_surf, self.all_sprites, ZLAYERS["bg details"])

        # if len(self.data) == 1: 
        #     for obj in tmx_map.get_layer_by_name("Enemies"):
        #         if obj.name == "tooth":
        #             Tooth((obj.x, obj.y), level_frames["tooth"], (self.all_sprites, self.damage_sprites, self.tooth_sprites), self.collision_sprites, audio_files, self.players[0])

            for obj in tmx_map.get_layer_by_name("Items"):
                Item(obj.name, (obj.x + 32, obj.y + 32), level_frames["items"][obj.name], (self.all_sprites, self.item_sprites), self.data)

            self.initial_item_count = len(self.item_sprites)

        for obj in tmx_map.get_layer_by_name("Water"):
            rows = int(obj.height / 64)
            cols = int(obj.width / 64)
            for row in range(rows):
                for col in range(cols):
                    x = obj.x + col * 64
                    y = obj.y + row * 64
                    if row == 0:
                        AnimatedSprite((x, y), self.level_frames["water_top"], self.all_sprites, ZLAYERS["water"])
                    else:
                        Sprite((x, y), self.level_frames["water_body"], self.all_sprites, ZLAYERS["water"])

    def powerup_collision(self):
        for player in self.players:
            collided = pygame.sprite.spritecollide(player, self.powerup_sprites, True)
            for p in collided:
                if p.power_type == "double_jump":
                    player.enable_double_jump()
                elif p.power_type == "magic":
                    player.buff_damage()
                elif p.power_type == "shield":
                    player.activate_shield()
                ParticleEffectSprite(p.rect.center, self.level_frames["particle"], self.all_sprites)
                self.audio_files["coin"].play()

    def item_collision(self):
        for player in self.players:
            item_sprites = pygame.sprite.spritecollide(player, self.item_sprites, True)
            for item in item_sprites:
                item.activate(player.data)
                ParticleEffectSprite(item.rect.center, self.level_frames["particle"], self.all_sprites)
                self.coin_sound.play()

    def hit_collision(self):
        for sprite in self.damage_sprites.sprites():
            if sprite.rect.colliderect(self.players[0].hitbox_rect):
                self.players[0].damage()
        for sprite in self.all_sprites:
            if hasattr(sprite, 'player') and hasattr(sprite, 'direction') and hasattr(sprite, 'facing_right'):
                if sprite.rect.colliderect(self.players[0].rect):
                    player_x = self.players[0].rect.centerx
                    archer_x = sprite.rect.centerx
                    if (sprite.direction > 0 and player_x < archer_x) or (sprite.direction < 0 and player_x > archer_x):
                        sprite.direction *= -1
                        sprite.facing_right = sprite.direction > 0

    def attack_collision(self):
        enemy_sprites = self.tooth_sprites.sprites() + self.bombastic_sprites.sprites() + self.archer_sprites.sprites() + self.ice_wizard_sprites.sprites()
        
        for target in enemy_sprites:
            facing_target = (self.players[0].rect.centerx < target.rect.centerx and self.players[0].face_right) or \
                            (self.players[0].rect.centerx > target.rect.centerx and not self.players[0].face_right)

            if target.hitbox_rect.colliderect(self.players[0].rect) and self.players[0].attacking and facing_target:
                if target not in self.players[0].attacked_enemies:
                    target.take_damage()
                    self.players[0].attacked_enemies.append(target)
        for player in self.players:
            for sprite in self.damage_sprites:
                offset = (sprite.rect.left - player.rect.left, sprite.rect.top - player.rect.top)
                if pygame.sprite.collide_mask(player, sprite):
                    player.damage(knockback=False)

        affected_targets = set()
        for i, attacker in enumerate(self.players):
            for j, target in enumerate(self.players):
                if i == j or target in affected_targets:
                    continue
                if attacker.attacking:
                    facing_target = (
                        attacker.rect.centerx < target.rect.centerx and attacker.face_right
                    ) or (
                        attacker.rect.centerx > target.rect.centerx and not attacker.face_right
                    )
                    if target.rect.colliderect(attacker.rect) and facing_target:
                        target.knockback_from(attacker)
                        affected_targets.add(target)

        if not self.multiplayer:
            for player in self.players:
                for target in self.tooth_sprites:
                    facing_target = (
                        player.rect.centerx < target.rect.centerx and player.face_right
                    ) or (
                        player.rect.centerx > target.rect.centerx and not player.face_right
                    )
                    if target.rect.colliderect(player.rect) and player.attacking and facing_target:
                        target.reverse()

    def bullet_collision(self):
        for i, attacker in enumerate(self.players):
            for bullet in attacker.bullets:
                for j, target in enumerate(self.players):
                    if i != j and bullet.rect.colliderect(target.rect):
                        if not target.timers["hit"].active:
                            target.damage()
                            bullet.kill()
                            if bullet in attacker.bullets:
                                attacker.bullets.remove(bullet)

    def check_constraint(self):
        alive = [p for p in self.players if p.data.health > 0 and p.hitbox_rect.bottom < self.level_bottom + 300]
        if len(alive) == 0:
            return "gameover"
        if len(alive) == 1 and self.multiplayer:
            return f"{alive[0].data.name} won"
        if len(self.item_sprites) == 0 and self.initial_item_count > 0 and not self.multiplayer:
            return "win"

    def spawn_powerups(self):
        map_name = os.path.basename(self.tmx_map.filename)
        powerup_types = self.level_frames["powerups"]

        durations = {
            "double_jump": 10000,
            "magic": 8000,
            "shield": 12000
        }

        positions = self.powerup_locations.get(map_name, {})

        for power_type, image in powerup_types.items():
            coords = positions.get(power_type, [])
            for pos in coords:
                powerup = PowerUp(power_type, pos, image, duration=durations.get(power_type, 8000))
                self.powerup_sprites.add(powerup)
                self.all_sprites.add(powerup)


    def update(self, dt):
        self.all_sprites.update(dt)
        self.powerup_sprites.update(dt)
        self.item_collision()
        self.hit_collision()
        self.attack_collision()
        self.bullet_collision()
        self.powerup_collision()

        # self.all_sprites.draw(self.player.hitbox_rect.center, dt)

    def draw(self, surface):
        self.all_sprites.custom_draw(self.players[0] if len(self.players) == 1 else self.players)
        for player in self.players:
            player.draw_shield(surface)
        
            
