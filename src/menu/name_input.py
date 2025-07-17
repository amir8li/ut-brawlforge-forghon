import pygame
from config import SCREEN_SIZE, FPS
import os

class NameInputScreen:
    def __init__(self, surface):
        self.display = surface
        self.clock = pygame.time.Clock()

        font_path = os.path.join("src", "assets", "images", "menu", "fonts", "runescape_uf.ttf")
        self.font = pygame.font.Font(font_path, 40)
        self.small_font = pygame.font.Font(font_path, 28)

        # input boxes
        self.input_boxes = [
            pygame.Rect(SCREEN_SIZE[0] // 2 - 150, 250, 300, 60),
            pygame.Rect(SCREEN_SIZE[0] // 2 - 150, 400, 300, 60)
        ]
        self.names = ["", ""]
        self.active = [False, False]

        # button images
        self.button_img = pygame.image.load(
            os.path.join("src", "assets", "images", "menu", "button", "button1.png")
        ).convert_alpha()
        self.highlight_img = pygame.image.load(
            os.path.join("src", "assets", "images", "menu", "button", "highlighted.png")
        ).convert_alpha()

        self.button_img = pygame.transform.scale(self.button_img, (320, 80))
        self.highlight_img = pygame.transform.scale(self.highlight_img, (320, 80))

        # hollow brown frame
        self.frame_rect = pygame.Rect(SCREEN_SIZE[0] // 2 - 320, 160, 640, 360)
        self.frame_color = (102, 81, 60)
        self.frame_thickness = 6

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
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, box in enumerate(self.input_boxes):
                        self.active[i] = box.collidepoint(event.pos)
                if event.type == pygame.KEYDOWN:
                    for i in range(2):
                        if self.active[i]:
                            if event.key == pygame.K_BACKSPACE:
                                self.names[i] = self.names[i][:-1]
                            elif event.key == pygame.K_RETURN:
                                self.active[i] = False
                            else:
                                if len(self.names[i]) < 10:
                                    self.names[i] += event.unicode
                    if event.key == pygame.K_RETURN and all(self.names):
                        done = True

            self.display.fill((169, 153, 139))

            pygame.draw.rect(self.display, self.frame_color, self.frame_rect, self.frame_thickness, border_radius=20)

            for i, box in enumerate(self.input_boxes):
                img = self.highlight_img if self.active[i] else self.button_img
                self.display.blit(img, img.get_rect(center=box.center))

                color = (255, 255, 255) if self.active[i] else (200, 200, 200)
                #pygame.draw.rect(self.display, color, box, border_radius=10)
                #pygame.draw.rect(self.display, (0, 0, 0), box, 2, border_radius=10)

                text = self.font.render(self.names[i], True, (255, 255, 255))
                self.render_text_with_shadow(
                    self.names[i], self.font, (255,255,255),
                    (box.x + 10, box.centery - text.get_height() // 2)
                )

            label1 = "PLAYER 1 NAME:"
            label2 = "PLAYER 2 NAME:"
            self.render_text_with_shadow(label1, self.small_font, (225,225,225),
                (self.input_boxes[0].x, self.input_boxes[0].y - 45))
            self.render_text_with_shadow(label2, self.small_font, (225,225,225),
                (self.input_boxes[1].x, self.input_boxes[1].y - 45))

            cont = "PRESS ENTER TO CONTINUE"
            cont_text = self.small_font.render(cont, True, (255,255,255))
            self.render_text_with_shadow(cont, self.small_font, (255,255,255),
                cont_text.get_rect(center=(SCREEN_SIZE[0] // 2, 600)).topleft)

            pygame.display.update()

        return self.names
