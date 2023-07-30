import pygame
from scripts.utils import vector_sub, vector_add


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
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

    def update(self, tilemap, movement=[0, 0]):
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
        self.apply_gravity()

        self.animaiton.update()

    def render(self, surf, offest):
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
            self.velocity[1] = min(4, self.velocity[1] + 0.5)

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

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)
        self.air_time += 1
        # Setting player states
        if self.collisions["bottom"]:
            self.air_time = 0
        if self.air_time > 4:
            self.set_state("jump")
        elif movement[0] != 0:
            self.set_state("run")
        else:
            self.set_state("idle")
