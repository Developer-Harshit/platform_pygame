import os
import pygame

BASE_IMG_PATH = "data/images/"


def load_img(rpath):
    path = BASE_IMG_PATH + rpath

    img = pygame.image.load(path).convert()  # convert method makes it easier to render

    img.set_colorkey((0, 0, 0))
    return img


def load_images(path):
    images = []
    for img_path in os.listdir(BASE_IMG_PATH + path):
        img = load_img(path + "/" + img_path)

        images.append(img)
    return images
