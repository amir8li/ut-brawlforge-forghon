import pygame
from config import SCREEN_SIZE, FPS

class NameInputScreen:
    def __init__(self, surface):
        self.display = surface
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 36, bold=True)
        self.input_boxes = [pygame.Rect(SCREEN_SIZE[0]//2-150, 250, 300, 60),
                            pygame.Rect(SCREEN_SIZE[0]//2-150, 400, 300, 60)]
        self.names = ["", ""]
        self.active = [False, False]

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
            self.display.fill((220, 200, 160))
            for i, box in enumerate(self.input_boxes):
                color = (0,0,0) if self.active[i] else (80,80,80)
                pygame.draw.rect(self.display, color, box, 3)
                text = self.font.render(self.names[i], True, (0,0,0))
                self.display.blit(text, text.get_rect(midleft=(box.x+10, box.centery)))
            label1 = self.font.render("Player 1 Name:", True, (0,0,0))
            label2 = self.font.render("Player 2 Name:", True, (0,0,0))
            self.display.blit(label1, (self.input_boxes[0].x, self.input_boxes[0].y-50))
            self.display.blit(label2, (self.input_boxes[1].x, self.input_boxes[1].y-50))
            cont = self.font.render("Press ENTER to continue", True, (0,0,0))
            self.display.blit(cont, cont.get_rect(center=(SCREEN_SIZE[0]//2, 600)))
            pygame.display.update()
        return self.names
