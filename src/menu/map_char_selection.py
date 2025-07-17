import pygame
import sys
import os
from config import *
from src.utils import draw_text

character_list = ["player1", "player6", "player3", "player4"]
character_names = ["Blade Knight", "Shadow Rogue", "Fire Mage", "Thunder Viking"]
single_maps = ["0.tmx", "2.tmx", "5.tmx", "6.tmx"]
multi_maps = ["1.tmx", "3.tmx", "4.tmx", "7.tmx"]

SCREEN_WIDTH, SCREEN_HEIGHT = SCREEN_SIZE

class MapCharacterSelect:
    def __init__(self, screen, mode, player_names):
        self.screen = screen
        self.mode = mode
        self.player_names = player_names
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font("src/assets/images/ui/runescape_uf.ttf", 48)
        self.name_font = pygame.font.Font("src/assets/images/ui/runescape_uf.ttf", 28)
        self.character_thumbnails = self.load_character_thumbnails()
        self.map_thumbnails = self.load_map_thumbnails()
        self.button_img = pygame.image.load("src/assets/images/menu/button/square.png").convert_alpha()
        self.highlighted_img = pygame.image.load("src/assets/images/menu/button/highlighted.png").convert_alpha()
        self.selected_map = 0

        if self.mode == "multi":
            self.selected_indices = [None, None]
        else:
            self.selected_character = 0

    def load_character_thumbnails(self):
        thumbnails = []
        for name in character_list:
            path = os.path.join("src", "assets", "images", "players", name, "wall", "0.png")
            image = pygame.image.load(path).convert_alpha()
            surface = pygame.Surface((140, 140), pygame.SRCALPHA)

            if name == "player2":
                image = pygame.transform.smoothscale(image, (130, 130))
                rect = image.get_rect(center=(70, 70))
            elif name == "player3":
                image = pygame.transform.smoothscale(image, (110, 140))
                rect = image.get_rect(midbottom=(70, 135))
            elif name == "player4":
                image = pygame.transform.smoothscale(image, (120, 120))
                rect = image.get_rect(center=(70, 70))
                rect.x -= 10
                rect.y += 10
            else:
                image = pygame.transform.smoothscale(image, (100, 100))
                rect = image.get_rect(center=(70, 70))

            surface.blit(image, rect)
            thumbnails.append((name, surface))
        return thumbnails

    def load_map_thumbnails(self):
        thumbnails = []
        maps = single_maps if self.mode == "single" else multi_maps
        for name in maps:
            square = pygame.Surface((100, 100)).convert_alpha()
            square.fill("#d5d5d5")
            framed = pygame.Surface((140, 140), pygame.SRCALPHA)
            rect = square.get_rect(center=(70, 70))
            framed.blit(square, rect)
            thumbnails.append((name, framed))
        return thumbnails

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    start_x = SCREEN_WIDTH // 2 - ((len(self.character_thumbnails) - 1) * 200) // 2
                    for i, (_, img) in enumerate(self.character_thumbnails):
                        x = start_x + i * 200
                        y = 200
                        rect = img.get_rect(center=(x, y))
                        if rect.collidepoint(mx, my):
                            if self.mode == "multi":
                                if i not in self.selected_indices:
                                    self.selected_indices[0 if self.selected_indices[0] is None else 1] = i
                                else:
                                    # اگر قبلاً انتخاب شده بود، جابجا بشه
                                    for p_idx in range(2):
                                        if self.selected_indices[p_idx] == i:
                                            self.selected_indices[p_idx] = None
                            else:
                                self.selected_character = i

                    start_x_map = SCREEN_WIDTH // 2 - ((len(self.map_thumbnails) - 1) * 200) // 2
                    for i, (_, img) in enumerate(self.map_thumbnails):
                        x = start_x_map + i * 200
                        y = 550
                        rect = img.get_rect(center=(x, y))
                        if rect.collidepoint(mx, my):
                            self.selected_map = i

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.mode == "single":
                            selected_map = single_maps[self.selected_map]
                            selected_name = character_list[self.selected_character]
                            return selected_map, selected_name
                        else:
                            if None not in self.selected_indices:
                                selected_map = multi_maps[self.selected_map]
                                selected_characters = [character_list[i] for i in self.selected_indices]
                                return selected_map, selected_characters

            self.screen.fill((169, 153, 139))
            self.draw_ui()
            pygame.display.flip()

    def draw_ui(self):
        draw_text(self.screen, "Choose your hero", self.title_font, "#ffffff", (SCREEN_WIDTH // 2, 80), shadow=True)
        start_x = SCREEN_WIDTH // 2 - ((len(self.character_thumbnails) - 1) * 200) // 2

        for i, (_, image) in enumerate(self.character_thumbnails):
            name = character_names[i]
            x = start_x + i * 200
            y = 200
            is_selected = (i == self.selected_character) if self.mode == "single" else i in self.selected_indices
            frame = self.highlighted_img if is_selected else self.button_img
            frame = pygame.transform.scale(frame, (140, 140))
            rect = frame.get_rect(center=(x, y))
            self.screen.blit(frame, rect)
            self.screen.blit(image, image.get_rect(center=rect.center))
            draw_text(self.screen, name, self.name_font, "#ffffff", (x, y + 105), shadow=True)

            if self.mode == "multi":
                for p_idx in range(2):
                    if self.selected_indices[p_idx] == i:
                        draw_text(self.screen, self.player_names[p_idx], self.name_font, "#ffffff", (x, y - 60), shadow=True)

        draw_text(self.screen, "Choose your map", self.title_font, "#ffffff", (SCREEN_WIDTH // 2, 420), shadow=True)
        start_x_map = SCREEN_WIDTH // 2 - ((len(self.map_thumbnails) - 1) * 200) // 2
        for i, (map_name, image) in enumerate(self.map_thumbnails):
            x = start_x_map + i * 200
            y = 550
            frame = self.highlighted_img if i == self.selected_map else self.button_img
            frame = pygame.transform.scale(frame, (140, 140))
            rect = frame.get_rect(center=(x, y))
            self.screen.blit(frame, rect)
            self.screen.blit(image, image.get_rect(center=rect.center))
            draw_text(self.screen, map_name.replace(".tmx", ""), self.name_font, "#ffffff", (x, y + 105), shadow=True)
