import pygame


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {"left": False, "right": False, "top": False, "bottom": False}

    def get_rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self, tilemap, movement=[0, 0]):
        frame_movement = (
            movement[0] + self.velocity[0],
            movement[1] + self.velocity[1],
        )
        print(self.collisions["bottom"])
        if not self.collisions["bottom"]:
            # Applying gravity

            self.velocity[1] = min(
                4, self.velocity[1] + 0.5
            )  # for impleting terminal velocity while implementing it

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
        if self.collisions["bottom"] or self.collisions["top"]:
            print("hi")
            self.velocity[1] = 0

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

    def render(self, surf):
        surf.blit(self.game.assets["player"], self.pos)
