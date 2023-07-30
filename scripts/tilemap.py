import pygame
from scripts.utils import vector_sub
from random import randint
from perlin_noise import PerlinNoise

# Neighbours offset wrt player
NEIGHBOUR_OFFSETS = [
    (-1, 0),
    (-1, -1),
    (0, -1),
    (1, -1),
    (1, 0),
    (0, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
]
PHYSICS_TILES = {"grass", "stone"}  # Set is faster to lookup than lists


class Tilemap:
    def __init__(self, game, tile_size=16):
        self.tile_size = tile_size
        self.game = game
        # two systems of tiles
        self.tilemap = {}  # convinient for handling physics

        self.offgrid_tiles = []  # tiles ie places all over grid

        xOff = 0.002
        p = PerlinNoise(randint(10, 40))
        for i in range(100):
            yOff = 0.0005
            for j in range(5):
                noise_s = int(abs((p([xOff, yOff]) * 2) // 1))
                noise_g = int(abs((p([yOff, xOff]) * 2) // 1))

                self.tilemap[str(3 + i) + ";" + str(j + 1)] = {
                    "type": "grass",
                    "variant": noise_g,
                    "pos": (3 + i, j + 1),
                }

                self.tilemap[str(3 + i) + ";" + str(j - 7)] = {
                    "type": "stone",
                    "variant": noise_s,
                    "pos": (3 + i, j - 7),
                }
                yOff += 0.005
            xOff += 0.03

    def find_neighbours(self, pos):
        neighbour_tiles = []
        tile_location = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOUR_OFFSETS:
            myTile_location = (
                str(tile_location[0] + offset[0])
                + ";"
                + str(tile_location[1] + offset[1])
            )
            if myTile_location in self.tilemap:
                neighbour_tiles.append(self.tilemap[myTile_location])
        return neighbour_tiles

    def find_physics_neighbours(self, pos):
        physics_rects = []
        for tile in self.find_neighbours(pos):
            if tile["type"] in PHYSICS_TILES:
                physics_rects.append(
                    pygame.Rect(
                        tile["pos"][0] * self.tile_size,
                        tile["pos"][1] * self.tile_size,
                        self.tile_size,
                        self.tile_size,
                    )
                )
        return physics_rects

    def render(self, surf, offset=[0, 0]):
        # For rendering offset tiles
        for tile in self.offgrid_tiles:
            tile_type = self.game.assets[tile["type"]]
            tile_img = tile_type[tile["variant"]]

            """Subtracted with offest as camera is moving,tiles will be moving in opposite direction"""
            surf.blit(tile_img, vector_sub(tile["pos"], offset))
        # For rendering tiles visible on screen
        for x in range(
            offset[0] // self.tile_size,
            (offset[0] + surf.get_width()) // self.tile_size + 1,
        ):
            for y in range(
                offset[1] // self.tile_size,
                (offset[1] + surf.get_height()) // self.tile_size + 1,
            ):
                loc = str(x) + ";" + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    tile_type = self.game.assets[tile["type"]]
                    tile_img = tile_type[tile["variant"]]
                    """Subtracted with offest as camera is moving,tiles will be moving in opposite direction"""
                    scaled_pos = (
                        tile["pos"][0] * self.tile_size,
                        tile["pos"][1] * self.tile_size,
                    )
                    surf.blit(tile_img, vector_sub(scaled_pos, offset))
        # For rendering all tiles
        # for location in self.tilemap:
        #     tile = self.tilemap[location]
        #     tile_type = self.game.assets[tile["type"]]
        #     tile_img = tile_type[tile["variant"]]
        #     scaled_pos = (
        #         tile["pos"][0] * self.tile_size,
        #         tile["pos"][1] * self.tile_size,
        #     )
        #     surf.blit(tile_img, vector_sub(scaled_pos, offset))
