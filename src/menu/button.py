import pygame
import os

class Button:
    def __init__(self, text, pos, font, action, size=(300, 70)):
        self.font = font
        self.text = text
        self.action = action
        self.hovered = False

        img_path = os.path.join("src", "assets", "images", "menu", "button")
        self.normal = pygame.image.load(os.path.join(img_path, "button.png")).convert_alpha()
        self.highlight = pygame.image.load(os.path.join(img_path, "highlighted.png")).convert_alpha()

        self.normal = pygame.transform.scale(self.normal, size)
        self.highlight = pygame.transform.scale(self.highlight, size)

        self.image = self.normal
        self.rect = self.image.get_rect(center=pos)

        self.text_surf = font.render(text, True, (255, 255, 255))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def update(self, mouse_pos, mouse_click):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered:
            self.image = self.highlight
            if mouse_click[0]:
                self.action()
        else:
            self.image = self.normal

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        surface.blit(self.text_surf, self.text_rect)
