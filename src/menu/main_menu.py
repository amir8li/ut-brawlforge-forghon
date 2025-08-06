import pygame
import os
import random
from config import SCREEN_SIZE, FPS
from src.menu.button import Button
from src.utils import import_folder, import_animation

class MainMenu:
    def __init__(self, surface, audio_files, settings):
        self.surface = surface
        self.audio_files = audio_files
        self.settings = settings
        self.clock = pygame.time.Clock()

        self.bg = pygame.Surface(SCREEN_SIZE)
        self.bg.fill((169, 153, 139))

        self.top_border = pygame.image.load(os.path.join("src", "assets", "images", "menu", "top_border.png")).convert_alpha()
        self.top_border = pygame.transform.scale(self.top_border, (SCREEN_SIZE[0], self.top_border.get_height()))

        self.bottom_border = pygame.image.load(os.path.join("src", "assets", "images", "menu", "bottom_border.png")).convert_alpha()
        self.bottom_border = pygame.transform.scale(self.bottom_border, (SCREEN_SIZE[0], self.bottom_border.get_height()))

        self.pattern = pygame.image.load(os.path.join("src", "assets", "images", "menu", "box.png")).convert_alpha()
        self.pattern = pygame.transform.scale(self.pattern, (600, 450))

        font_path = os.path.join("src", "assets", "images", "menu", "fonts", "runescape_uf.ttf")
        self.font = pygame.font.Font(font_path, 36)
        self.title_font = pygame.font.Font(font_path, 64)

        self.candle_frames = import_folder("src", "assets", "images", "level", "candle")
        self.candle_light_frames = import_folder("src", "assets", "images", "level", "candle light")
        self.smoke_frames = import_folder("src", "assets", "images", "effects", "particle")
        main_char_path = os.path.join("src", "assets", "images", "menu", "main_char")
        self.character_frames = import_animation(main_char_path, "0_Valkyrie_Falling Down_")
        self.character_index = 0
        self.character_y = -100
        self.character_target_y = 65
        self.character_speed = 250
        self.character_landed = False

        self.candle_anim_index = 0
        self.candle_light_index = 0
        self.smoke_index = 0

        self.candle_positions = [
            (50, 40), (SCREEN_SIZE[0] - 100, 40),
            (50, SCREEN_SIZE[1] - 100), (SCREEN_SIZE[0] - 100, SCREEN_SIZE[1] - 100)
        ]
        self.particle_pos = [random.randint(0, SCREEN_SIZE[0]) for _ in range(20)]
        self.buttons = []
        self.create_buttons()

        if 'menu_bg' in self.audio_files:
            self.audio_files['menu_bg'].set_volume(self.settings.get('music_volume', 0.5))
            self.audio_files['menu_bg'].play(-1)

    def create_buttons(self):
        self.buttons.append(Button("START", (SCREEN_SIZE[0] // 2, 280), self.font, lambda: self.select("start")))
        self.buttons.append(Button("ONLINE GAME", (SCREEN_SIZE[0] // 2, 360), self.font, lambda: self.select("online")))
        self.buttons.append(Button("OPTIONS", (SCREEN_SIZE[0] // 2, 440), self.font, lambda: self.select("options")))
        self.buttons.append(Button("QUIT", (SCREEN_SIZE[0] // 2, 520), self.font, lambda: self.select("quit")))


    def select(self, choice):
        if 'click' in self.audio_files:
            self.audio_files['click'].set_volume(self.settings.get('sfx_volume', 0.7))
            self.audio_files['click'].play()
        if 'menu_bg' in self.audio_files:
            self.audio_files['menu_bg'].stop()
        self.choice = choice
        self.running = False

    def run(self):
        self.choice = None
        self.running = True

        while self.running:
            dt = self.clock.tick(FPS) / 1000
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if 'menu_bg' in self.audio_files:
                        self.audio_files['menu_bg'].stop()
                    pygame.quit()
                    exit()

            self.candle_anim_index += 8 * dt
            self.candle_light_index += random.choice([1, 0]) * 10 * dt
            self.smoke_index += 3 * dt

            if not self.character_landed:
                self.character_y += self.character_speed * dt
                if self.character_y >= self.character_target_y:
                    self.character_y = self.character_target_y
                    self.character_landed = True

            candle_frame = self.candle_frames[int(self.candle_anim_index) % len(self.candle_frames)]
            candle_light_frame = self.candle_light_frames[int(self.candle_light_index) % len(self.candle_light_frames)]
            smoke_frame = self.smoke_frames[int(self.smoke_index) % len(self.smoke_frames)]
            character_frame = self.character_frames[int(self.character_index) % len(self.character_frames)]
            scaled_character = pygame.transform.scale(character_frame, (
                character_frame.get_width() // 5,
                character_frame.get_height() // 5
            ))
            char_rect = scaled_character.get_rect(center=(SCREEN_SIZE[0] // 2, self.character_y))

            self.surface.blit(self.bg, (0, 0))
            self.surface.blit(self.top_border, (0, 0))
            bottom_y = SCREEN_SIZE[1] - self.bottom_border.get_height()
            self.surface.blit(self.bottom_border, (0, bottom_y))
            self.surface.blit(scaled_character, char_rect)

            for pos in self.candle_positions:
                x, y = pos
                self.surface.blit(candle_frame, (x, y))
                glow = candle_light_frame.copy()
                glow.set_alpha(120)
                self.surface.blit(glow, (x - 10, y - 20))
                smoke = smoke_frame.copy()
                smoke.set_alpha(80)
                smoke_pos = (x + random.randint(-5, 5), y - 30 + random.randint(-5, 5))
                self.surface.blit(smoke, smoke_pos)

            for i in range(len(self.particle_pos)):
                y = (i * 30 + pygame.time.get_ticks() * 0.05) % SCREEN_SIZE[1]
                self.surface.fill((255, 255, 150, 30), pygame.Rect(self.particle_pos[i], y, 2, 2), special_flags=pygame.BLEND_RGBA_ADD)

            pattern_rect = self.pattern.get_rect(center=(SCREEN_SIZE[0] // 2, 400))
            self.surface.blit(self.pattern, pattern_rect)

            title_text = self.title_font.render("Welcome!", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(SCREEN_SIZE[0] // 2, 120))
            self.surface.blit(title_text, title_rect)

            for btn in self.buttons:
                btn.update(mouse_pos, mouse_pressed)
                btn.draw(self.surface)

            pygame.display.update()

        return self.choice
