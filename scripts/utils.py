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


def vector_add(v1, v2):
    return (v1[0] + v2[0], v1[1] + v2[1])


def vector_sub(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1])
