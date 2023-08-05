import pygame
import math
from random import random, randint
from scripts.utils import vector_sub, vector_add
from scripts.particle import Particle


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.last_movement = [0, 0]
        self.collisions = {"left": False, "right": False, "top": False, "bottom": False}

        # For animation
        self.state = ""
        self.set_state("idle")
        # To add padding to the images,its value can vary based on images
        self.anim_off = (-3, -3)
        self.flip = False

    def get_rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_state(self, state):
        if self.state != state:
            self.state = state
            # Getting entity animation
            self.animaiton = self.game.assets[self.type + "/" + self.state].copy()

    def update(self, tilemap, movement=(0, 0)):
        frame_movement = (
            movement[0] + self.velocity[0],
            movement[1] + self.velocity[1],
        )

        self.collisions = {
            "left": False,
            "right": False,
            "top": False,
            "bottom": False,
        }  # resseting the collision
        self.pos[0] += frame_movement[0]
        self.check_collision_x(tilemap, frame_movement)
        self.pos[1] += frame_movement[1]
        self.check_collision_y(tilemap, frame_movement)

        if movement[0] > 0:  # if moving right
            self.flip = False
        if movement[0] < 0:  # if moving left
            self.flip = True

        self.last_movement = movement
        self.apply_gravity()

        self.animaiton.update()

    def render(self, surf, offest=(0, 0)):
        # Subtracting the pos with offset and adding with animation offset
        render_pos = vector_add(vector_sub(self.pos, offest), self.anim_off)
        # Rendering the entity based on current animation frame
        surf.blit(
            pygame.transform.flip(self.animaiton.get_img(), self.flip, False),
            render_pos,
        )

    def apply_gravity(self):
        if self.collisions["bottom"] or self.collisions["top"]:
            self.velocity[1] = 0

        else:
            # Applying gravity
            self.velocity[1] = min(3, self.velocity[1] + 0.5)

    def check_collision_x(self, tilemap, frame_movement):
        # checking X -collision ---------------------------------------------------|
        entity_rect = self.get_rect()

        for rect in tilemap.find_physics_neighbours(self.pos):
            if entity_rect.colliderect(rect):  # if collided with tile
                if frame_movement[0] > 0:  # if moving right
                    self.collisions["right"] = True
                    entity_rect.right = rect.left  # push it to the left
                if frame_movement[0] < 0:  # if moving left
                    self.collisions["left"] = True
                    entity_rect.left = rect.right  # push it to the right
            self.pos[0] = entity_rect.x

    def check_collision_y(self, tilemap, frame_movement):
        # checking Y -collision ---------------------------------------------------|
        entity_rect = self.get_rect()

        for rect in tilemap.find_physics_neighbours(self.pos):
            if entity_rect.colliderect(rect):  # if collided with tile
                if frame_movement[1] >= 0:  # if moving bottom
                    self.collisions["bottom"] = True
                    entity_rect.bottom = rect.top  # push it to the top
                if frame_movement[1] < 0:  # if moving top
                    self.collisions["top"] = True

                    entity_rect.top = rect.bottom  # push it to the bottom
            self.pos[1] = entity_rect.y


# inheriting PhysicEntity Class
class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, "player", pos, size)
        self.air_time = 0
        # Consider Animation,Movement,Jump state while doint wall slide
        self.is_wall_sliding = False

        self.is_dashing = 0  # Represent direction and time

        self.jump_data = {"current": 2, "total": 2, "speed": -6}

    def render(self, surf, offest=(0, 0)):
        if abs(self.is_dashing) <= 50:
            super().render(surf, offest)
        else:
            # show dash particles
            pass

    """
    Player can jump 1 time,if you run out of jump you cant jump again
    But if your are on wall ,your jump resets
    But if you fall from wall without jumping you can jump again
    """

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)
        self.air_time += 1
        # Jump --------------------------------------------------------------------|
        if self.collisions["bottom"]:
            self.air_time = 0
            self.jump_data["current"] = self.jump_data["total"]

        # Wall Slide --------------------------------------------------------------|
        self.wall_slide()

        # For changing state ------------------------------------------------------|
        if not self.is_wall_sliding:
            if self.air_time > 4:
                self.set_state("jump")
                # self.jumps = 0 # to not able to jump after falling
            elif movement[0] != 0:
                self.set_state("run")
            else:
                self.set_state("idle")

        # Dash --------------------------------------------------------------------|
        # Moving plaer in direction of dash
        if abs(self.is_dashing) > 50:
            self.velocity[0] = abs(self.is_dashing) / self.is_dashing * 7
            par_velocity = (
                abs(self.is_dashing) / self.is_dashing * 4 * random(),
                0,
            )
            self.game.particles.append(
                Particle(
                    self.game,
                    "particle",
                    self.get_rect().center,
                    par_velocity,
                    randint(3, 12),
                )
            )
            if abs(self.is_dashing) <= 52:
                self.velocity[0] *= 0.3
        # brust of dash particles
        if abs(self.is_dashing) == 60:
            for i in range(15):
                # in radians
                par_angle = random() * math.pi * 2
                par_speed = random() * 0.7 + 0.5

                # generating velocity based on angle
                par_velocity = (
                    math.cos(par_angle) * par_speed,
                    math.sin(par_angle) * par_speed,
                )
                self.game.particles.append(
                    Particle(
                        self.game,
                        "particle",
                        self.get_rect().center,
                        par_velocity,
                        randint(3, 12),
                    )
                )
        # For handling dashing time -----------------------------------------------|

        if self.is_dashing > 0:
            self.is_dashing = max(self.is_dashing - 1, 0)
        if self.is_dashing < 0:
            self.is_dashing = min(self.is_dashing + 1, 0)

        # For handling floating velocitiy -----------------------------------------|

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def dash(self):
        if not self.is_dashing:
            # Moving left
            if self.flip:
                self.is_dashing = -60
            # Moving right
            else:
                self.is_dashing = 60

        else:
            pass

    def wall_slide(self):
        self.is_wall_sliding = False
        if (self.collisions["left"] or self.collisions["right"]) and self.air_time > 4:
            self.is_wall_sliding = True
            self.velocity[1] = min(self.velocity[1], 1)
            if self.collisions["left"]:
                self.flip = True
            else:
                self.flip = False
            self.set_state("wall_slide")

    def jump(self):
        if self.is_wall_sliding:
            # if facing left and moving left
            if self.flip and self.last_movement[0] < 0:
                # Move right and up
                self.velocity[0] = 3
                self.velocity[1] = -3.5
                self.air_time = 5
                self.jump_data["current"] = max(0, self.jump_data["current"] - 1)
                return True
            # if facing right and moving right
            elif not self.flip and self.last_movement[0] > 0:
                # Move left and up
                self.velocity[0] = -3
                self.velocity[1] = -3.5
                self.air_time = 5
                self.jump_data["current"] = max(0, self.jump_data["current"] - 1)
                return True
        # Returns False when 0 and True when 1

        elif self.jump_data["current"]:
            self.jump_data["current"] -= 1
            self.velocity[1] = self.jump_data["speed"]
            # sets jump state when air_time > 4
            self.air_time = 5
            return True
