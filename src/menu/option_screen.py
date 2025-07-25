import pygame
import os
import json
from config import SCREEN_SIZE, FPS
from src.utils import draw_text, import_image

class OptionsScreen:
    def __init__(self, surface, audio_files, settings):
        self.display = surface
        self.audio_files = audio_files
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font("src/assets/images/ui/runescape_uf.ttf", 80)
        self.font_medium = pygame.font.Font("src/assets/images/ui/runescape_uf.ttf", 48)
        self.font_small = pygame.font.Font("src/assets/images/ui/runescape_uf.ttf", 36)

        self.button_img = import_image("src", "assets", "images", "menu", "button", "button")
        self.button_highlight = import_image("src", "assets", "images", "menu", "button", "highlighted")
        self.button_img = pygame.transform.scale(self.button_img, (320, 80))
        self.button_highlight = pygame.transform.scale(self.button_highlight, (320, 80))

        self.bg = pygame.Surface(SCREEN_SIZE)
        self.bg.fill((169, 153, 139))
        self.frame_rect = pygame.Rect(SCREEN_SIZE[0] // 2 - 360, 120, 720, 480)
        self.frame_color = (102, 81, 60)
        self.frame_thickness = 6

        self.settings_file = "settings.json"
        self.default_settings = {"music_volume": 0.5, "sfx_volume": 0.7}
        self.settings = settings
        self.music_volume = self.settings["music_volume"]
        self.sfx_volume = self.settings["sfx_volume"]

        self.music_slider_rect = pygame.Rect(SCREEN_SIZE[0] // 2 - 200, 200, 400, 30)
        self.sfx_slider_rect = pygame.Rect(SCREEN_SIZE[0] // 2 - 200, 300, 400, 30)
        self.slider_handle_size = 30
        self.music_handle_pos = self.music_slider_rect.left + int(self.music_volume * self.music_slider_rect.width)
        self.sfx_handle_pos = self.sfx_slider_rect.left + int(self.sfx_volume * self.sfx_slider_rect.width)

        self.dragging_music = False
        self.dragging_sfx = False
        self.back_rect = pygame.Rect(SCREEN_SIZE[0] // 2 - 160, 400, 320, 80)

        if 'menu_bg' in self.audio_files:
            self.audio_files['menu_bg'].set_volume(self.music_volume)
            self.audio_files['menu_bg'].play(-1)

        self.apply_volumes()

    def save_settings(self):
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print("خطا هنگام ذخیره تنظیمات:", e)
    def save_volume_settings(self, new_volume):
        self.settings['music_volume'] = new_volume
        with open("settings.json", "w") as f:
            json.dump(self.settings, f)
        self.audio_files['menu_bg'].set_volume(new_volume)

    def apply_volumes(self):
        music_keys = ['bg', 'menu_bg']
        sfx_keys = ['attack', 'coin', 'jump', 'damage', 'bullet', 'click', 'transition', 'loading', 'win', 'gameover', 'type']
        for key in music_keys:
            if key in self.audio_files:
                try:
                    self.audio_files[key].set_volume(self.music_volume)
                except AttributeError:
                    print(f"Warning: Sound file for '{key}' not loaded properly.")
        for key in sfx_keys:
            if key in self.audio_files:
                try:
                    self.audio_files[key].set_volume(self.sfx_volume)
                except AttributeError:
                    print(f"Warning: Sound file for '{key}' not loaded properly.")

    def update_slider(self, mouse_pos, mouse_pressed):
        handle_rect = pygame.Rect(self.music_handle_pos - self.slider_handle_size // 2, self.music_slider_rect.centery - self.slider_handle_size // 2, self.slider_handle_size, self.slider_handle_size)
        if mouse_pressed[0] and handle_rect.collidepoint(mouse_pos):
            self.dragging_music = True
        if not mouse_pressed[0]:
            self.dragging_music = False
        if self.dragging_music:
            self.music_handle_pos = min(max(mouse_pos[0], self.music_slider_rect.left), self.music_slider_rect.right)
            self.music_volume = (self.music_handle_pos - self.music_slider_rect.left) / self.music_slider_rect.width
            self.settings["music_volume"] = self.music_volume
            self.apply_volumes()
            self.save_settings()

        handle_rect = pygame.Rect(self.sfx_handle_pos - self.slider_handle_size // 2, self.sfx_slider_rect.centery - self.slider_handle_size // 2, self.slider_handle_size, self.slider_handle_size)
        if mouse_pressed[0] and handle_rect.collidepoint(mouse_pos):
            self.dragging_sfx = True
        if not mouse_pressed[0]:
            self.dragging_sfx = False
        if self.dragging_sfx:
            self.sfx_handle_pos = min(max(mouse_pos[0], self.sfx_slider_rect.left), self.sfx_slider_rect.right)
            self.sfx_volume = (self.sfx_handle_pos - self.sfx_slider_rect.left) / self.sfx_slider_rect.width
            self.settings["sfx_volume"] = self.sfx_volume
            self.apply_volumes()
            self.save_settings()

    def draw(self):
        self.display.blit(self.bg, (0, 0))
        pygame.draw.rect(self.display, self.frame_color, self.frame_rect, self.frame_thickness, border_radius=20)
        draw_text(self.display, "Music Volume", self.font_medium, "#ffffff", (SCREEN_SIZE[0] // 2, 150), shadow=True)
        pygame.draw.rect(self.display, (80, 80, 80), self.music_slider_rect, border_radius=10)
        fill_width = self.music_volume * self.music_slider_rect.width
        pygame.draw.rect(self.display, (200, 200, 200), (self.music_slider_rect.left, self.music_slider_rect.top, fill_width, self.music_slider_rect.height), border_radius=10)
        pygame.draw.circle(self.display, (255, 255, 255), (self.music_handle_pos, self.music_slider_rect.centery), self.slider_handle_size // 2)
        draw_text(self.display, f"{int(self.music_volume * 100)}%", self.font_small, "#ffffff", (SCREEN_SIZE[0] // 2 + 240, self.music_slider_rect.centery), shadow=True)
        draw_text(self.display, "Sound Effects Volume", self.font_medium, "#ffffff", (SCREEN_SIZE[0] // 2, 250), shadow=True)
        pygame.draw.rect(self.display, (80, 80, 80), self.sfx_slider_rect, border_radius=10)
        fill_width = self.sfx_volume * self.sfx_slider_rect.width
        pygame.draw.rect(self.display, (200, 200, 200), (self.sfx_slider_rect.left, self.sfx_slider_rect.top, fill_width, self.sfx_slider_rect.height), border_radius=10)
        pygame.draw.circle(self.display, (255, 255, 255), (self.sfx_handle_pos, self.sfx_slider_rect.centery), self.slider_handle_size // 2)
        draw_text(self.display, f"{int(self.sfx_volume * 100)}%", self.font_small, "#ffffff", (SCREEN_SIZE[0] // 2 + 240, self.sfx_slider_rect.centery), shadow=True)
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.back_rect.collidepoint(mouse_pos)
        button_img = self.button_highlight if is_hovered else self.button_img
        self.display.blit(button_img, self.back_rect.topleft)
        draw_text(self.display, "Back", self.font_medium, "#ffffff", self.back_rect.center, shadow=True)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if 'menu_bg' in self.audio_files:
                        self.audio_files['menu_bg'].stop()
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.back_rect.collidepoint(event.pos):
                        if 'click' in self.audio_files:
                            self.audio_files['click'].set_volume(self.sfx_volume)
                            self.audio_files['click'].play()
                        if 'menu_bg' in self.audio_files:
                            self.audio_files['menu_bg'].stop()
                        return "menu"
            self.update_slider(mouse_pos, mouse_pressed)
            self.draw()
            pygame.display.update()
        return "menu"