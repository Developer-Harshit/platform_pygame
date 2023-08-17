import pygame
import pygame.gfxdraw as gfx
import math


class Particle:
    def __init__(self, game, p_type, pos, velocity=[0, 0], frame=0):
        self.game = game
        self.type = p_type
        self.velocity = list(velocity)
        self.pos = list(pos)
        self.animation = self.game.assets["particle/" + self.type].copy()
        self.animation.frame = frame

    def update(self):
        kill = False
        if self.animation.done:
            kill = True
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        self.animation.update()

        return kill

    def render(self, surf, offset=(0, 0)):
        img = self.animation.get_img()
        surf.blit(
            img,
            (
                self.pos[0] - offset[0] - img.get_width() // 2,
                self.pos[1] - offset[1] - img.get_height() // 2,
            ),
        )


class Spark:
    # Aditionally you can also assign size and how fast it disappears
    def __init__(
        self, pos, angle, speed, color=(255, 255, 255), border_color=(170, 40, 80)
    ):
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed
        self.color = color
        self.border_color = border_color

    def update(self):
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed
        self.speed = max(self.speed - 0.1, 0)

        kill = not self.speed
        return kill

    def render(self, surf, offset=[0, 0]):
        # Polygon/diamand - like shape

        render_points = [
            # Forward Point
            (
                self.pos[0] + math.cos(self.angle) * self.speed * 2.5 - offset[0],
                self.pos[1] + math.sin(self.angle) * self.speed * 2.5 - offset[1],
            ),
            # Right Point
            (
                self.pos[0]
                + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.3
                - offset[0],
                self.pos[1]
                + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.3
                - offset[1],
            ),
            # Backward Point
            (
                self.pos[0]
                + math.cos(self.angle + math.pi) * self.speed * 2.5
                - offset[0],
                self.pos[1]
                + math.sin(self.angle + math.pi) * self.speed * 2.5
                - offset[1],
            ),
            # Left Point
            (
                self.pos[0]
                + math.cos(self.angle - math.pi * 0.5) * self.speed * 0.3
                - offset[0],
                self.pos[1]
                + math.sin(self.angle - math.pi * 0.5) * self.speed * 0.3
                - offset[1],
            ),
        ]

        pygame.draw.polygon(surf, self.color, render_points)
        gfx.aapolygon(surf, render_points, self.border_color)
