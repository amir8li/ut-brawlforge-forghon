import pygame
from pygame import Vector2 as vector
from random import uniform

from config import *
from src.sprites import Sprite, MovingSprite, AnimatedSprite, Item, Spike, ParticleEffectSprite
from src.player import Player
from src.groups import AllSprites
from src.enemies import Tooth

class Level:
    def __init__(self, tmx_map, level_frames, audio_files, data):
        self.data = data
        self.tmx_map = tmx_map
        self.display = pygame.display.get_surface()
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_bottom = tmx_map.height * TILE_SIZE
        tmx_level_properties = tmx_map.get_layer_by_name("Data")[0].properties
        bg_tile = level_frames["bg_tiles"][tmx_level_properties["bg"]] if tmx_level_properties["bg"] else None

        clouds_dict = {"large": level_frames["cloud_large"], "small": level_frames["cloud_small"]}
        self.all_sprites = AllSprites(tmx_map.width, tmx_map.height, clouds_dict, tmx_level_properties["horizon_line"], bg_tile)

        self.collision_sprites = pygame.sprite.Group()
        self.semi_collistion_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.tooth_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        self.level_frames = level_frames
        self.coin_sound = audio_files['coin']
        self.coin_sound.set_volume(0.3)

        self.setup(tmx_map, level_frames, audio_files)

    def setup(self, tmx_map, level_frames, audio_files):
        for layer in ["BG", "Terrain", "FG", "Platforms"]:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == "Terrain": groups.append(self.collision_sprites)
                elif layer == "Platforms": groups.append(self.semi_collistion_sprites)
                match layer:
                    case "BG": z = ZLAYERS["bg tiles"]
                    case "FG": z = ZLAYERS["fg"]
                    case _: z = ZLAYERS["main"]
                Sprite((x*TILE_SIZE, y*TILE_SIZE), surf, groups, z)

        for obj in tmx_map.get_layer_by_name("BG details"):
            if obj.name == "static":
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, z = ZLAYERS["bg tiles"])
            else:
                AnimatedSprite((obj.x, obj.y), level_frames[obj.name], self.all_sprites, ZLAYERS["bg tiles"])
                if obj.name == "candle":
                    AnimatedSprite((obj.x, obj.y) + vector(-20, -20), level_frames["candle_light"], self.all_sprites, ZLAYERS["bg tiles"])

        for obj in tmx_map.get_layer_by_name("Objects"):
            if obj.name == "player":
                player_pos = (obj.x, obj.y)
                if self.data.name == "player3":
                    player_pos = (player_pos[0], player_pos[1] - 40)

                self.player = Player(
                    pos=player_pos,
                    groups=self.all_sprites,
                    collision_sprites= self.collision_sprites,
                    semi_collision_sprites= self.semi_collistion_sprites,
                    frames=level_frames["player"],
                    attack_sound=audio_files['attack'],
                    jump_sound=audio_files['jump'],
                    bullet_sound=audio_files['bullet'],
                    data = self.data)

            else:
                if obj.name in ("barrel", "crate"):
                    Sprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
                else:
                    frames = level_frames[obj.name] if not "palm" in obj.name else level_frames["palms"][obj.name]
                    if obj.name == "floor_spike" and obj.properties["inverted"]:
                        frames = [pygame.transform.flip(frame, False, True) for frame in frames]
                    groups = [self.all_sprites]
                    if obj.name in ("palm_small", "palm_large"): groups.append(self.semi_collistion_sprites)
                    if obj.name in ("saw", "floor_spike"): groups.append(self.damage_sprites)
                    z = ZLAYERS["main"] if not "bg" in obj.name else ZLAYERS["bg details"]
                    anim_speed = ANIMATION_SPEED if not "palm" in obj.name else 6 + uniform(-1, 1)
                    AnimatedSprite((obj.x, obj.y), frames, groups, z, anim_speed)

        for obj in tmx_map.get_layer_by_name("Moving Objects"):
            if obj.name == "spike":
                Spike(
                    pos = (obj.x + obj.width / 2, obj.y + obj.height / 2),
                    surf = level_frames["spike"],
                    radius = obj.properties["radius"],
                    speed = obj.properties["speed"],
                    start_angle = obj.properties["start_angle"],
                    end_angle = obj.properties["end_angle"],
                    groups = (self.all_sprites, self.damage_sprites),
                )
                for i in range(0, obj.properties["radius"], 20):
                    Spike(
                        pos = (obj.x + obj.width / 2, obj.y + obj.height / 2),
                        surf = level_frames["spike_chain"],
                        radius = i,
                        speed = obj.properties["speed"],
                        start_angle = obj.properties["start_angle"],
                        end_angle = obj.properties["end_angle"],
                        groups = self.all_sprites,
                        z = ZLAYERS["bg details"],
                    )
            else:
                frames = level_frames[obj.name]
                groups = (self.all_sprites, self.semi_collistion_sprites) if obj.properties["platform"] else (self.all_sprites, self.damage_sprites)
                if obj.width > obj.height:
                    move_dir = 'x'
                    start_pos = (obj.x, obj.y + obj.height // 2)
                    end_pos = (obj.x + obj.width, obj.y + obj.height // 2)
                else:
                    move_dir = 'y'
                    start_pos = (obj.x + obj.width // 2, obj.y)
                    end_pos = (obj.x + obj.width // 2, obj.y + obj.height)
                speed = obj.properties["speed"]
                MovingSprite(frames, groups, start_pos, end_pos, speed, move_dir, obj.properties["flip"])

                if obj.name == "saw":
                    if move_dir == 'x':
                        y = start_pos[1] - level_frames["saw_chain"].get_height() // 2
                        left, right = int(start_pos[0]), int(end_pos[0])
                        for x in range(left, right, 20):
                            Sprite((x, y), level_frames["saw_chain"], self.all_sprites, ZLAYERS["bg details"])
                    else:
                        x = start_pos[0] - level_frames["saw_chain"].get_width() // 2
                        top, bottom = int(start_pos[1]), int(end_pos[1])
                        for y in range(top, bottom, 20):
                            Sprite((x, y), level_frames["saw_chain"], self.all_sprites, ZLAYERS["bg details"])
    
        for obj in tmx_map.get_layer_by_name("Enemies"):
            if obj.name == "tooth":
                Tooth((obj.x, obj.y), level_frames["tooth"], (self.all_sprites, self.damage_sprites, self.tooth_sprites), self.collision_sprites)        

        for obj in tmx_map.get_layer_by_name("Items"):
            Item(obj.name, (obj.x + 32, obj.y + 32), level_frames["items"][obj.name], (self.all_sprites, self.item_sprites), self.data)

        for obj in tmx_map.get_layer_by_name("Water"):
            rows = int(obj.height / 64)
            cols = int(obj.width / 64)
            for row in range(rows):
                for col in range(cols):
                    x = obj.x + col * 64
                    y = obj.y + row * 64
                    if row == 0:
                        AnimatedSprite((x, y), level_frames["water_top"], self.all_sprites, ZLAYERS["water"])
                    else:
                        Sprite((x, y), level_frames["water_body"], self.all_sprites, ZLAYERS["water"])
    
    def item_collision(self):
        if self.item_sprites:
            item_sprites = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
            if item_sprites:
                item_sprites[0].activate()
                ParticleEffectSprite(item_sprites[0].rect.center, self.level_frames["particle"], self.all_sprites)
                self.coin_sound.play()

    def hit_collision(self):
        for sprite in self.damage_sprites.sprites():
            if sprite.rect.colliderect(self.player.hitbox_rect):
                self.player.damage()

    def attack_collision(self):
        for target in self.tooth_sprites.sprites():
            facing_target = (self.player.rect.centerx < target.rect.centerx and self.player.face_right) or \
                            (self.player.rect.centerx > target.rect.centerx and not self.player.face_right)
            if target.rect.colliderect(self.player.rect) and self.player.attacking and facing_target:
                target.reverse()

    def check_constraint(self):
        if self.player.hitbox_rect.bottom >= self.level_bottom + 300:
            return "gameover"
        if self.player.data.health <= 0:
            return "gameover"
        gold_items = [item for item in self.item_sprites if item.type == "gold"]
        if len(gold_items) == 0:
            return "win"
        return None

    def update(self, dt):
        self.all_sprites.update(dt)
        self.item_collision()
        self.hit_collision()
        self.attack_collision()

    def draw(self, surface):
        self.all_sprites.custom_draw(self.player)