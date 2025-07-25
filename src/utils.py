import pygame
import os
from os import walk
from os.path import join
from random import randint
from src.sprites import AnimatedSprite
from src.timer import Timer
from config import SCREEN_SIZE

pygame.init()

class Data:
    def __init__(self, ui, player_id=0):
        self.ui = ui
        self.player_id = player_id
        self._coins = 0
        self._health = 5
        self.ui.create_hearts(self._health, self.player_id)

    @property
    def coins(self):
        return self._coins

    @coins.setter
    def coins(self, value):
        self._coins = value
        self.ui.show_coins(value, self.player_id)

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = value
        self.ui.create_hearts(value, self.player_id)

class UI:
    def __init__(self, font, frames, mode, player_names=None, audio_files=None):
        self.display = pygame.display.get_surface()
        self.mode = mode
        self.audio_files = audio_files
        self.heart_sprites = {0: pygame.sprite.Group(), 1: pygame.sprite.Group()}
        self.font = font
        self.name_font = pygame.font.Font(
            os.path.join("src", "assets", "images", "menu", "fonts", "runescape_uf.ttf"), 14
        )
        self.player_names = player_names if player_names else {0: "PLAYER 1", 1: "PLAYER 2"}
        self.heart_frames = frames["heart"]
        self.heart_width = self.heart_frames[0].get_width()
        self.heart_padding = 6
        self.coin_amount = {0: 0, 1: 0}
        self.coin_timer = Timer(1000)
        self.coin_frame = frames["coin"]

    def create_hearts(self, amount, player_id):
        for sprite in self.heart_sprites[player_id]:
            sprite.kill()
        for heart in range(amount):
            if player_id == 0:
                x = 10 + heart * (self.heart_width + self.heart_padding)
                y = 10
            else:
                x = SCREEN_SIZE[0] - 10 - self.heart_width - (heart * (self.heart_width + self.heart_padding))
                y = 10
            Heart((x, y), self.heart_frames, self.heart_sprites[player_id])
        if self.audio_files and 'type' in self.audio_files:
            self.audio_files['type'].set_volume(0.5)
            self.audio_files['type'].play()

    def display_text(self, player_id):
        if self.coin_timer.active:
            if player_id == 0:
                coin_rect = self.coin_frame.get_rect(topleft=(10, 34))
                self.display.blit(self.coin_frame, coin_rect)
                text_surf = self.font.render(f'{self.coin_amount[player_id]}', False, "#33323d")
                text_rect = text_surf.get_rect(midleft=(coin_rect.right + 5, coin_rect.centery))
                self.display.blit(text_surf, text_rect)
            elif self.mode == "multi":
                coin_rect = self.coin_frame.get_rect(topright=(SCREEN_SIZE[0] - 10, 34))
                self.display.blit(self.coin_frame, coin_rect)
                text_surf = self.font.render(f'{self.coin_amount[player_id]}', False, "#33323d")
                text_rect = text_surf.get_rect(midright=(coin_rect.left - 5, coin_rect.centery))
                self.display.blit(text_surf, text_rect)

    def show_player_name(self, player_id):
        name = self.player_names.get(player_id, f"PLAYER {player_id + 1}")
        shadow_color = (0, 0, 0)
        text_color = (255, 255, 255)
        name_surf = self.name_font.render(name, True, text_color)
        shadow_surf = self.name_font.render(name, True, shadow_color)
        if player_id == 0:
            x = 10
        else:
            x = SCREEN_SIZE[0] - 10 - name_surf.get_width()
        y = 10 + self.heart_frames[0].get_height() + 4
        self.display.blit(shadow_surf, (x + 2, y + 2))
        self.display.blit(name_surf, (x, y))

    def show_coins(self, amount, player_id):
        self.coin_amount[player_id] = amount
        self.coin_timer.activate()
        if self.audio_files and 'type' in self.audio_files:
            self.audio_files['type'].set_volume(0.5)
            self.audio_files['type'].play()

    def update(self, dt):
        self.coin_timer.update()
        player_ids = [0] if self.mode != "multi" else [0, 1]
        for player_id in player_ids:
            self.heart_sprites[player_id].update(dt)
            self.heart_sprites[player_id].draw(self.display)
            self.display_text(player_id)
            if self.mode == "multi":
                self.show_player_name(player_id)

class Heart(AnimatedSprite):
    def __init__(self, pos, frame, groups):
        super().__init__(pos, frame, groups)
        self.active = False

    def animate(self, dt):
        self.frame_index += 6 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.active = False
            self.frame_index = 0

    def update(self, dt):
        if self.active:
            self.animate(dt)
        else:
            if randint(0, 1000) == 1:
                self.active = True

def import_image(*path, alpha=True, format='png'):
    full_path = join(*path) + f'.{format}'
    return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()

def import_folder(*path):
    frames = []
    for folder_path, _, image_names in walk(join(*path)):
        def extract_index(name):
            name = name.split('.')[0]
            num = ''.join(filter(str.isdigit, name))
            return int(num) if num else 0
        sorted_images = sorted(image_names, key=extract_index)
        for image_name in sorted_images:
            full_path = join(folder_path, image_name)
            frames.append(pygame.image.load(full_path).convert_alpha())
    return frames

def import_folder_dict(*path):
    frame_dict = {}
    for folder_path, _, image_names in walk(join(*path)):
        for image_name in image_names:
            full_path = join(folder_path, image_name)
            surface = pygame.image.load(full_path).convert_alpha()
            frame_dict[image_name.split('.')[0]] = surface
    return frame_dict

def import_sub_folders(*path):
    frame_dict = {}
    for _, sub_folders, __ in walk(join(*path)):
        if sub_folders:
            for sub_folder in sub_folders:
                frame_dict[sub_folder] = import_folder(*path, sub_folder)
    return frame_dict

def load_image(*path, alpha=True, format="png"):
    full_path = join(*path) + f".{format}"
    image = pygame.image.load(full_path)
    return image.convert_alpha() if alpha else image.convert()

def draw_text(surface, text, font, color, center_pos, shadow=False):
    if shadow:
        shadow_surf = font.render(text, True, "#000000")
        shadow_rect = shadow_surf.get_rect(center=(center_pos[0]+2, center_pos[1]+2))
        surface.blit(shadow_surf, shadow_rect)
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=center_pos)
    surface.blit(text_surf, text_rect)

def import_animation(path, prefix):
    files = sorted([
        f for f in os.listdir(path)
        if f.startswith(prefix) and f.endswith(".png")
    ])
    frames = [pygame.image.load(join(path, f)).convert_alpha() for f in files]
    return frames

def import_character_frames(*path_parts):
    base_path = os.path.join(*path_parts)
    animations = {}
    folders = [folder for folder in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, folder))]
    for folder in folders:
        full_path = os.path.join(base_path, folder)
        images = [
            pygame.image.load(os.path.join(full_path, file)).convert_alpha()
            for file in sorted(os.listdir(full_path)) if file.endswith(".png")
        ]
        animations[folder] = images
    if "fall" not in animations:
        if "jump" in animations:
            animations["fall"] = animations["jump"][-1:]
        elif "idle" in animations:
            animations["fall"] = animations["idle"][:1]
    if "bullet" not in animations:
        fallback = None
        if "stop" in animations:
            fallback = animations["stop"][0]
        elif "attack" in animations:
            fallback = animations["attack"][0]
        elif "idle" in animations:
            fallback = animations["idle"][0]
        if fallback:
            animations["bullet"] = [pygame.transform.scale(fallback, (24, 24))]
    return animations