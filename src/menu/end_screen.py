import pygame
import random
from config import SCREEN_SIZE, FPS
from src.utils import import_image, draw_text

class EndScreen:
    def __init__(self, surface, result, background_surface, audio_files, settings):
        self.display = surface
        self.audio_files = audio_files
        self.result = result
        self.settings = settings
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font("src/assets/images/ui/runescape_uf.ttf", 72)
        self.font_medium = pygame.font.Font("src/assets/images/ui/runescape_uf.ttf", 40)
        self.background = background_surface
        self.overlay = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))
        self.panel_width, self.panel_height = 600, 400
        self.panel_rect = pygame.Rect(
            (SCREEN_SIZE[0] - self.panel_width) // 2,
            (SCREEN_SIZE[1] - self.panel_height) // 2,
            self.panel_width,
            self.panel_height
        )
        self.restart_rect = pygame.Rect(self.panel_rect.centerx - 130, self.panel_rect.y + 180, 260, 60)
        self.menu_rect = pygame.Rect(self.panel_rect.centerx - 130, self.panel_rect.y + 250, 260, 60)
        self.next_rect = pygame.Rect(self.panel_rect.centerx - 130, self.panel_rect.y + 320, 260, 60) if result == "win" else None
        self.button_img = import_image("src", "assets", "images", "menu", "button", "button")
        self.button_highlight = import_image("src", "assets", "images", "menu", "button", "highlighted")
        self.skeleton_img = pygame.image.load("src/assets/images/menu/skeleton.png").convert_alpha()
        self.skeleton_img = pygame.transform.scale(self.skeleton_img, (
            self.skeleton_img.get_width() // 2,
            self.skeleton_img.get_height() // 2
        ))
        self.skeletons = []
        self.skeleton_spawn_timer = 0
        self.next_skeleton_delay = random.uniform(0.1, 0.3)
        self.particles_up = []
        self.particles_down = []
        self.particle_spawn_timer_up = 0
        self.particle_spawn_timer_down = 0
        self.particle_img = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.particle_img, (255, 223, 99), (6, 6), 6)
        self.flash_timer = 0
        self.flash_visible = True

        # ✅ پخش صدا فقط یک‌بار
        if result == "win" or result.endswith("won"):
            if 'win' in self.audio_files:
                self.audio_files['win'].set_volume(0.7)
                self.audio_files['win'].play()
        elif result == "gameover":
            if 'gameover' in self.audio_files:
                self.audio_files['gameover'].set_volume(0.7)
                self.audio_files['gameover'].play()

    def run(self):
        choice = None
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000
            self.flash_timer += dt
            if self.flash_timer >= 0.5:
                self.flash_visible = not self.flash_visible
                self.flash_timer = 0

            self.skeleton_spawn_timer += dt
            if (
                self.result == "gameover" and
                self.skeleton_spawn_timer >= self.next_skeleton_delay and
                len(self.skeletons) < 30
            ):
                self.skeletons.append({
                    "x": random.randint(0, SCREEN_SIZE[0] - self.skeleton_img.get_width()),
                    "y": -self.skeleton_img.get_height(),
                    "speed": random.randint(200, 350)
                })
                self.skeleton_spawn_timer = 0
                self.next_skeleton_delay = random.uniform(0.1, 0.3)

            for skeleton in self.skeletons:
                skeleton["y"] += skeleton["speed"] * dt
            self.skeletons = [s for s in self.skeletons if s["y"] < SCREEN_SIZE[1]]

            self.particle_spawn_timer_up += dt
            self.particle_spawn_timer_down += dt
            if self.result.endswith("won"):
                if self.particle_spawn_timer_up >= 0.05:
                    self.particles_up.append({
                        "x": random.randint(0, SCREEN_SIZE[0]),
                        "y": SCREEN_SIZE[1],
                        "speed": random.uniform(30, 60),
                        "alpha": 255
                    })
                    self.particle_spawn_timer_up = 0
                if self.particle_spawn_timer_down >= 0.05:
                    self.particles_down.append({
                        "x": random.randint(0, SCREEN_SIZE[0]),
                        "y": -20,
                        "speed": random.uniform(30, 60),
                        "alpha": 255
                    })
                    self.particle_spawn_timer_down = 0

            for p in self.particles_up:
                p["y"] -= p["speed"] * dt
                p["alpha"] = max(0, p["alpha"] - 60 * dt)
            for p in self.particles_down:
                p["y"] += p["speed"] * dt
                p["alpha"] = max(0, p["alpha"] - 60 * dt)

            self.particles_up = [p for p in self.particles_up if p["alpha"] > 0 and p["y"] > 0]
            self.particles_down = [p for p in self.particles_down if p["alpha"] > 0 and p["y"] < SCREEN_SIZE[1]]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.restart_rect.collidepoint(event.pos):
                        if 'click' in self.audio_files:
                            self.audio_files['click'].set_volume(0.7)
                            self.audio_files['click'].play()
                        self.stop_end_audio()
                        choice = "restart"
                        running = False
                    elif self.menu_rect.collidepoint(event.pos):
                        if 'click' in self.audio_files:
                            self.audio_files['click'].set_volume(0.7)
                            self.audio_files['click'].play()
                        self.stop_end_audio()
                        choice = "menu"
                        running = False
                    elif self.next_rect and self.next_rect.collidepoint(event.pos):
                        if 'click' in self.audio_files:
                            self.audio_files['click'].set_volume(0.7)
                            self.audio_files['click'].play()
                        self.stop_end_audio()
                        choice = "next"
                        running = False

            self.draw()
            pygame.display.update()

        return choice

    def stop_end_audio(self):
        # ✅ توقف صدا فقط هنگام خروج از صفحه
        if self.result == "win" or self.result.endswith("won"):
            if 'win' in self.audio_files:
                self.audio_files['win'].stop()
        elif self.result == "gameover":
            if 'gameover' in self.audio_files:
                self.audio_files['gameover'].stop()

    def draw(self):
        self.display.blit(self.background, (0, 0))
        if self.result == "gameover":
            for skeleton in self.skeletons:
                self.display.blit(self.skeleton_img, (skeleton["x"], skeleton["y"]))
        if self.result.endswith("won") or self.result == "win":
            for p in self.particles_up + self.particles_down:
                img = self.particle_img.copy()
                img.set_alpha(int(p["alpha"]))
                self.display.blit(img, (p["x"], p["y"]))

        self.display.blit(self.overlay, (0, 0))
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (169, 153, 139), panel_surface.get_rect(), border_radius=16)
        self.display.blit(panel_surface, self.panel_rect.topleft)
        pygame.draw.rect(self.display, (68, 68, 68), self.panel_rect, width=6, border_radius=16)

        if self.flash_visible:
            text = "YOU WIN!" if self.result == "win" else "GAME OVER!" if self.result == "gameover" else f"{self.result.upper()}!"
            draw_text(
                self.display,
                text,
                self.font_large,
                "#ffffff",
                (self.panel_rect.centerx, self.panel_rect.y + 80),
                shadow=True
            )

        self.draw_button(self.restart_rect, "Restart")
        self.draw_button(self.menu_rect, "Menu")
        if self.next_rect:
            self.draw_button(self.next_rect, "Next Level")

    def draw_button(self, rect, text):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = rect.collidepoint(mouse_pos)
        button_img = self.button_highlight if is_hovered else self.button_img
        button_img = pygame.transform.scale(button_img, (rect.width, rect.height))
        self.display.blit(button_img, rect.topleft)
        draw_text(self.display, text, self.font_medium, "#ffffff", rect.center, shadow=True)
