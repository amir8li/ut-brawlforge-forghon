import pygame
from config import SCREEN_SIZE, FPS
from os.path import join

class LoadingScreen:
    def __init__(self, surface):
        self.display = surface
        self.clock = pygame.time.Clock()

        self.bg_color = (10, 10, 10)

        self.wheelbarrow = pygame.image.load("src/assets/images/menu/wheelbarrow.png").convert_alpha()
        self.wheelbarrow = pygame.transform.scale(self.wheelbarrow, (120, 70))
        self.wheelbarrow_pos = [-self.wheelbarrow.get_width(), SCREEN_SIZE[1]//2 - 75]

        self.font = pygame.font.Font(join("src", "assets", "images", "menu", "fonts", "runescape_uf.ttf"), 32)
        self.percent_font = pygame.font.Font(join("src", "assets", "images", "menu", "fonts", "runescape_uf.ttf"), 24)
        self.bg_image = pygame.image.load("src/assets/images/menu/loading_bg.png").convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (1280, 720))
        self.bg_image = pygame.transform.scale(self.bg_image, SCREEN_SIZE)

        self.progress = 0
        self.alpha = 255
        self.fade_in = True
        self.fade_out = False
        self.fade_surface = pygame.Surface(SCREEN_SIZE)
        self.fade_surface.fill((0, 0, 0))

        self.strip_offset = 0

        self.loading_timer = 0
        self.loading_dots = 0

    def update(self, dt):
        target_x = SCREEN_SIZE[0]//2 - self.wheelbarrow.get_width() // 2
        if self.wheelbarrow_pos[0] < target_x:
            self.wheelbarrow_pos[0] += 200 * dt
            self.progress = min((self.wheelbarrow_pos[0] + self.wheelbarrow.get_width()/2) / (target_x + self.wheelbarrow.get_width()/2) * 100, 100)
        else:
            self.wheelbarrow_pos[0] = target_x
            self.progress = min(self.progress + 60* dt, 100)

        if self.fade_in:
            self.alpha -= 300 * dt
            if self.alpha <= 0:
                self.alpha = 0
                self.fade_in = False

        if self.progress >= 100:
            self.fade_out = True
            self.alpha += 300 * dt

        self.strip_offset += 200 * dt

        self.loading_timer += dt
        if self.loading_timer >= 0.5:
            self.loading_dots = (self.loading_dots + 1) % 4  
            self.loading_timer = 0

    def draw(self):
        self.display.blit(self.bg_image, (0, 0))

        bar_width, bar_height = 400, 20
        bar_x, bar_y = SCREEN_SIZE[0]//2 - bar_width//2, SCREEN_SIZE[1]//2

        pygame.draw.rect(self.display, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height), 2)

        fill_width = bar_width * (self.progress/100)
        bar_fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
        pygame.draw.rect(self.display, (200, 200, 200), bar_fill_rect)

        stripe_color = (160, 160, 160)
        stripe_width = 10
        stripe_spacing = 20
        for i in range(0, int(fill_width), stripe_spacing):
            stripe_rect = pygame.Rect(bar_x + i, bar_y, stripe_width, bar_height)
            pygame.draw.rect(self.display, stripe_color, stripe_rect)

        percent_surf = self.percent_font.render(f"{int(self.progress)}%", True, (200, 200, 200))
        percent_rect = percent_surf.get_rect(midleft=(bar_x + bar_width + 10, bar_y + bar_height//2))
        self.display.blit(percent_surf, percent_rect)

        dots = '.' * self.loading_dots
        text_surf = self.font.render(f"LOADING{dots}", True, (200, 200, 200))
        text_rect = text_surf.get_rect(center=(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2 + 100))
        self.display.blit(text_surf, text_rect)

        self.display.blit(self.wheelbarrow, self.wheelbarrow_pos)

        if self.fade_in or self.fade_out:
            self.fade_surface.set_alpha(self.alpha)
            self.display.blit(self.fade_surface, (0, 0))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            self.update(dt)
            self.draw()
            pygame.display.update()
            if self.fade_out and self.alpha >= 255:
                running = False
