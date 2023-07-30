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


class Animation:
    def __init__(self, images, duration=5, loop=True):
        self.images = images
        self.duration = duration
        self.loop = loop
        self.done = False
        self.frame = 0

    # Could be used for sprites like grasses,decor animaiton
    def copy(self):
        return Animation(self.images, self.duration, self.loop)

    def update(self):
        """
        Whenever there is a loop and we have to repeat values ,we use modulo operator
        """
        v_Value = self.duration * len(self.images)
        if self.loop:
            self.frame = (self.frame + 1) % v_Value
        else:
            self.frame = min(self.frame + 1, v_Value - 1)
            if self.frame >= v_Value - 1:
                self.done = True

    def get_img(self):
        return self.images[int(self.frame / self.duration)]
