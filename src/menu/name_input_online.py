import pygame
from config import SCREEN_SIZE, FPS
import os

class NameInputOnlineScreen:
    def __init__(self, surface, audio_files, settings):
        self.display = surface
        self.audio_files = audio_files
        self.settings = settings
        self.clock = pygame.time.Clock()
        font_path = os.path.join("src", "assets", "images", "menu", "fonts", "runescape_uf.ttf")
        self.font = pygame.font.Font(font_path, 40)
        self.small_font = pygame.font.Font(font_path, 28)
        self.title_font = pygame.font.Font(font_path, 48)

        self.input_box = pygame.Rect(SCREEN_SIZE[0] // 2 - 150, 325, 300, 60)
        self.name = ""
        self.active = False

        self.button_img = pygame.image.load(os.path.join("src", "assets", "images", "menu", "button", "button1.png")).convert_alpha()
        self.highlight_img = pygame.image.load(os.path.join("src", "assets", "images", "menu", "button", "highlighted.png")).convert_alpha()
        self.button_img = pygame.transform.scale(self.button_img, (320, 80))
        self.highlight_img = pygame.transform.scale(self.highlight_img, (320, 80))
        self.frame_rect = pygame.Rect(SCREEN_SIZE[0] // 2 - 320, 160, 640, 360)
        self.frame_color = (102, 81, 60)
        self.frame_thickness = 6
        if 'menu_bg' in self.audio_files and not pygame.mixer.get_busy():
            self.audio_files['menu_bg'].set_volume(0.5)
            self.audio_files['menu_bg'].play(-1)

    def render_text_with_shadow(self, text, font, color, pos, shadow_offset=(2,2), shadow_color=(0,0,0)):
        shadow = font.render(text, True, shadow_color)
        self.display.blit(shadow, (pos[0] + shadow_offset[0], pos[1] + shadow_offset[1]))
        rendered = font.render(text, True, color)
        self.display.blit(rendered, pos)

    def run(self):
        done = False
        while not done:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if 'menu_bg' in self.audio_files:
                        self.audio_files['menu_bg'].stop()
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.input_box.collidepoint(event.pos):
                        self.active = True
                        if 'click' in self.audio_files:
                            self.audio_files['click'].play()
                    else:
                        self.active = False
                if event.type == pygame.KEYDOWN:
                    if self.active:
                        if event.key == pygame.K_BACKSPACE:
                            self.name = self.name[:-1]
                            if 'type' in self.audio_files:
                                self.audio_files['type'].play()
                        elif event.key == pygame.K_RETURN:
                             if not self.name.strip():
                                self.name = "Player"
                             done = True
                        else:
                            if len(self.name) < 10:
                                self.name += event.unicode
                                if 'type' in self.audio_files:
                                    self.audio_files['type'].play()
            
            self.display.fill((169, 153, 139))
            pygame.draw.rect(self.display, self.frame_color, self.frame_rect, self.frame_thickness, border_radius=20)
            
            title = "Enter Your Username"
            self.render_text_with_shadow(title, self.title_font, (255,255,255), 
                                         (self.frame_rect.centerx - self.title_font.size(title)[0] // 2, 180))

            img = self.highlight_img if self.active else self.button_img
            self.display.blit(img, img.get_rect(center=self.input_box.center))
            self.render_text_with_shadow(self.name, self.font, (255,255,255),
                (self.input_box.x + 10, self.input_box.centery - self.font.render(self.name, True, (255,255,255)).get_height() // 2))
            
            label = "USERNAME:"
            self.render_text_with_shadow(label, self.small_font, (225,225,225),
                (self.input_box.x, self.input_box.y - 45))
            
            cont = "PRESS ENTER TO CONTINUE"
            cont_text_size = self.small_font.size(cont)
            self.render_text_with_shadow(cont, self.small_font, (255,255,255),
                ((SCREEN_SIZE[0] - cont_text_size[0]) // 2, 600))

            pygame.display.update()
        
        if 'menu_bg' in self.audio_files:
            self.audio_files['menu_bg'].stop()
        return [self.name]