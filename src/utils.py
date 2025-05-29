import pygame
import os

BASE_IMG_PATH = "./src/assets/images/"

def load_image(path, scale=None, convert=False):
    img = pygame.image.load(BASE_IMG_PATH + path)
    if convert:
        img = img.convert()
    img.set_colorkey((0, 0, 0))
    if scale:
        img = pygame.transform.scale(img, scale)
    return img


def load_images(path, scale=None, convert=False):
    images = []
    for filename in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + "/" + filename, scale, convert))
    return images

class Animation:
    def __init__(self, images, frame_rate=10):
        self.images = images
        self.frame_rate = frame_rate
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

    def copy(self):
        return Animation(self.images, self.frame_rate)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 1000 / self.frame_rate:
            self.current_frame = (self.current_frame + 1) % len(self.images)
            self.last_update = now

    def get_current_image(self):
        return self.images[self.current_frame]