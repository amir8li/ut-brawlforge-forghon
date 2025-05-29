import pygame
import os

BASE_IMG_PATH = "./src/assets/images/"

def load_image(path, scale=None, is_heart=False):
    try:
        img = pygame.image.load(BASE_IMG_PATH + path)
        if is_heart:
            cream_color = (210, 180, 140)
            img.set_colorkey(cream_color)
        elif path.startswith("healthbar/"):
            img.set_colorkey((220, 220, 220))
        else:
            img.set_colorkey((0, 0, 0))
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    except FileNotFoundError:
        print(f"Error: Image file not found at {BASE_IMG_PATH + path}")
        return pygame.Surface((16, 16))

def load_images(path, scale=None, is_heart=False):
    images = []
    try:
        for filename in sorted(os.listdir(BASE_IMG_PATH + path)):
            images.append(load_image(path + "/" + filename, scale, is_heart))
        if not images:
            print(f"Error: No images found in {BASE_IMG_PATH + path}")
            return [pygame.Surface((16, 16))]
    except FileNotFoundError:
        print(f"Error: Directory not found at {BASE_IMG_PATH + path}")
        return [pygame.Surface((16, 16))]
    return images