from random import random, choice


class Cloud:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)  # copy the passed list
        self.img = img
        self.speed = speed
        self.depth = depth

    def update(self):
        # The cloud moves in x axis every frame
        self.pos[0] += self.speed

    def render(self, surf, offset=[0, 0]):
        # multiplying with depth To give you parallex effect
        render_pos = (
            self.pos[0] - offset[0] * self.depth,
            self.pos[1] - offset[1] * self.depth,
        )
        # In computer graphices to loop stuff ,its best to use modulo operator
        # position % (size + buffer) - buffer
        surf.blit(
            self.img,
            (
                render_pos[0] % (surf.get_width() + self.img.get_width())
                - self.img.get_width(),
                render_pos[1] % (surf.get_height() + self.img.get_height())
                - self.img.get_height(),
            ),
        )


class Clouds:
    def __init__(self, cloud_images, count=16):
        self.clouds = []
        for i in range(count):
            my_cloud = Cloud(
                (random() * 9999, random() * 9999),
                choice(cloud_images),
                random() * 1 + 0.05,
                random() * 0.6 + 0.2,
            )
            self.clouds.append(my_cloud)
        # Some advanced syntax of python ,using it to sort based on depth
        self.clouds.sort(key=lambda x: x.depth)

    def update(self):
        for cloud in self.clouds:
            cloud.update()

    def render(self, surf, offest=[0, 0]):
        for cloud in self.clouds:
            cloud.render(surf, offset=offest)
