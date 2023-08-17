import pygame
import math
from random import random, randint
from scripts.utils import vector_sub, vector_add
from scripts.particle import Particle, Spark


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


class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, "enemy", pos, size)

        self.walking = 0

    def shoot(self):
        dist_vect = (
            self.game.player.pos[0] - self.pos[0],
            self.game.player.pos[1] - self.pos[1],
        )
        if abs(dist_vect[1] < 16):
            # Shooting to left
            if self.flip and dist_vect[0] < 0:
                # Adding projectile
                self.game.projectiles.append(
                    [
                        [self.get_rect().centerx - 7, self.get_rect().centery],
                        -1.5,
                        0,
                    ]
                )
                # Adding sparks effect
                for i in range(7):
                    self.game.sparks.append(
                        Spark(
                            self.game.projectiles[-1][0],
                            random() - 0.5 + math.pi,
                            2 * random(),
                        )
                    )
                pass
            # Shooting to right
            if not self.flip and dist_vect[0] > 0:
                # Adding projectile

                self.game.projectiles.append(
                    [
                        [self.get_rect().centerx + 7, self.get_rect().centery],
                        1.5,
                        0,
                    ]
                )
                # Adding sparks effect
                for i in range(7):
                    self.game.sparks.append(
                        Spark(
                            self.game.projectiles[-1][0],
                            random() - 0.5,
                            2 * random(),
                        )
                    )

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset)

        # Bliting Gun
        inc = (-4 - self.game.assets["gun"].get_width()) if self.flip else 4
        surf.blit(
            pygame.transform.flip(self.game.assets["gun"], self.flip, False),
            (
                self.get_rect().centerx + inc - offset[0],
                self.get_rect().centery - offset[1],
            ),
        )

    def update(self, tilemap, movement=(0, 0)):
        # self.walking ~ False when = 0
        # Do not Touch ------------------------------------------------------------|
        if self.walking:
            # Checking for ahead of current position and below the current height
            if tilemap.check_solid(
                (self.get_rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)
            ):
                # Checking for colliison with a wall
                if self.collisions["left"] or self.collisions["right"]:
                    self.flip = not self.flip
                else:
                    movement = (
                        movement[0] + (-1 if self.flip else +1),
                        movement[1],
                    )
            else:
                self.flip = not self.flip
            self.walking = max(self.walking - 1, 0)

        # For Flipping and randomly start walking
        elif random() < 0.007:
            if random() < 0.05:
                self.flip = not self.flip
            self.walking = randint(20, 100)
        # For shooting projectiles
        elif random() < 0.04:
            self.shoot()

        # -------------------------------------------------------------------------|
        super().update(tilemap, movement)
        # Setting State -----------------------------------------------------------|
        if movement[0] != 0:
            self.set_state("run")
        else:
            self.set_state("idle")
        # if player in dash state
        if abs(self.game.player.is_dashing) >= 50:
            if self.get_rect().colliderect(self.game.player.get_rect()):
                self.game.sparks.append(
                    Spark(
                        self.get_rect().center,
                        0,
                        2.5 + random(),
                        (11, 11, 11),
                        (220, 30, 70),
                    )
                )

                self.game.sparks.append(
                    Spark(
                        self.get_rect().center,
                        math.pi,
                        2.5 + random(),
                        (11, 11, 11),
                        (220, 30, 70),
                    )
                )
                for i in range(10):
                    angle = random() * math.pi * 2
                    speed = random() * 5
                    self.game.sparks.append(
                        Spark(
                            self.get_rect().center,
                            angle,
                            speed,
                        )
                    )
                kill = True
                return kill


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

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)
        self.air_time += 1
        # Death -------------------------------------------------------------------|
        if self.air_time > 150:
            self.game.shake_value = max(20, self.game.shake_value)
            self.game.death += 1
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
                self.velocity[0] = 2
                self.velocity[1] = -5.5
                self.air_time = 5
                self.jump_data["current"] = max(0, self.jump_data["current"] - 1)
                return True
            # if facing right and moving right
            elif not self.flip and self.last_movement[0] > 0:
                # Move left and up
                self.velocity[0] = -2

                self.velocity[1] = -5.5
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
