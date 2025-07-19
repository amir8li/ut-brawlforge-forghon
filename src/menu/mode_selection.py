import pygame
import os
from config import SCREEN_SIZE, FPS
from src.menu.button import Button
from src.utils import import_animation

class ModeSelectScreen:
    def __init__(self, surface):
        self.display = surface
        self.clock = pygame.time.Clock()

        font_path = os.path.join("src", "assets", "images", "menu", "fonts", "runescape_uf.ttf")
        self.title_font = pygame.font.Font(font_path, 64)
        self.button_font = pygame.font.Font(font_path, 30)
        self.desc_font = pygame.font.Font(font_path, 22)

        self.left_x = SCREEN_SIZE[0] // 4
        self.right_x = SCREEN_SIZE[0] * 3 // 4
        self.button_y = 300

        self.single_button = Button("Single Player", (self.left_x, self.button_y), self.button_font,
                                    lambda: self.select("single"), size=(420, 90))
        self.multi_button = Button("Multiplayer", (self.right_x, self.button_y), self.button_font,
                                   lambda: self.select("multi"), size=(420, 90))
        self.buttons = [self.single_button, self.multi_button]

        anim_path = os.path.join("src", "assets", "images", "menu", "main_char")
        self.char_single = import_animation(anim_path, "0_Dark_Oracle_Idle_")
        self.char_multi_blue = import_animation(anim_path, "Wraith_01_Idle_")  
        self.char_multi_brown = import_animation(anim_path, "Wraith_02_Idle_")  

        self.index_single = 0
        self.index_multi_blue = 0
        self.index_multi_brown = 0

    def select(self, mode):
        self.choice = mode
        self.running = False

    def run(self):
        self.choice = None
        self.running = True

        pygame.event.clear()

        while self.running:
            dt = self.clock.tick(FPS) / 1000
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.display.fill((169, 153, 139))

            shadow = self.title_font.render("Select Your Mode", True, (60, 50, 40))
            text = self.title_font.render("Select Your Mode", True, (255, 255, 255))
            shadow_rect = shadow.get_rect(center=(SCREEN_SIZE[0] // 2 + 2, 142))
            text_rect = text.get_rect(center=(SCREEN_SIZE[0] // 2, 140))
            self.display.blit(shadow, shadow_rect)
            self.display.blit(text, text_rect)

            for btn in self.buttons:
                btn.update(mouse_pos, mouse_click)
                btn.draw(self.display)

            desc_offset = 40
            single_text = "Play alone through the story"
            multi_text = "Battle with your friends!"

            single_shadow = self.desc_font.render(single_text, True, (60, 50, 40))
            single_main = self.desc_font.render(single_text, True, (220, 210, 190))
            single_rect = single_main.get_rect(center=(self.left_x, self.single_button.rect.bottom + desc_offset))
            self.display.blit(single_shadow, single_rect.move(2, 2))
            self.display.blit(single_main, single_rect)

            multi_shadow = self.desc_font.render(multi_text, True, (60, 50, 40))
            multi_main = self.desc_font.render(multi_text, True, (220, 210, 190))
            multi_rect = multi_main.get_rect(center=(self.right_x, self.multi_button.rect.bottom + desc_offset))
            self.display.blit(multi_shadow, multi_rect.move(2, 2))
            self.display.blit(multi_main, multi_rect)

            if self.char_single:
                self.index_single += 6 * dt
                frame_s = self.char_single[int(self.index_single) % len(self.char_single)]
                scaled_s = pygame.transform.scale(frame_s, (135, 135))
                self.display.blit(scaled_s, scaled_s.get_rect(center=(self.left_x, single_rect.bottom + 80)))

            if self.char_multi_blue and self.char_multi_brown:
                self.index_multi_blue += 6 * dt
                self.index_multi_brown += 6 * dt
                frame_blue = self.char_multi_blue[int(self.index_multi_blue) % len(self.char_multi_blue)]
                frame_brown = self.char_multi_brown[int(self.index_multi_brown) % len(self.char_multi_brown)]

                scaled_blue = pygame.transform.scale(frame_blue, (150, 150))   
                scaled_brown = pygame.transform.scale(frame_brown, (150, 150))

                self.display.blit(scaled_brown, scaled_brown.get_rect(center=(self.right_x - 60, multi_rect.bottom + 80)))
                self.display.blit(scaled_blue, scaled_blue.get_rect(center=(self.right_x + 60, multi_rect.bottom + 80)))

            pygame.display.update()

        return self.choice
