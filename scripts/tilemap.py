import pygame
from scripts.utils import vector_sub

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

        for i in range(10):
            self.tilemap[str(3 + i) + ";10"] = {
                "type": "grass",
                "variant": 1,
                "pos": (3 + i, 10),
            }
            self.tilemap["20;" + str(9 + i)] = {
                "type": "stone",
                "variant": 1,
                "pos": (20, 9 + i),
            }

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

    def render(self, surf, offset):
        for tile in self.offgrid_tiles:
            tile_img = self.game.assets[tile["type"][tile["variant"]]]

            """Subtracted with offest as camera is moving,tiles will be moving in opposite direction"""
            surf.blit(tile_img, vector_sub(tile["pos"], offset))
        for location in self.tilemap:
            tile = self.tilemap[location]

            tile_type = self.game.assets[tile["type"]]

            tile_img = tile_type[tile["variant"]]
            scaled_pos = (
                tile["pos"][0] * self.tile_size,
                tile["pos"][1] * self.tile_size,
            )
            surf.blit(tile_img, vector_sub(scaled_pos, offset))
