import pygame
import os

BASE_IMG_PATH = "./src/assets/images/"

def load_image(path, scale=None):
    img = pygame.image.load(BASE_IMG_PATH + path)
    img.set_colorkey((0, 0, 0))
    if scale:
        img = pygame.transform.scale(img, scale)
    return img


def load_images(path, scale=None):
    images = []
    for filename in os.listdir(BASE_IMG_PATH + path):
        images.append(load_image(path + "/" + filename, scale))
    return images