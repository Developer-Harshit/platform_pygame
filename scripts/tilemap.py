import pygame
import json
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
# Tile offset wrt curent tile - left right up down
AUTOTILE_OFFSETS = [(1, 0), (-1, 0), (0, -1), (0, 1)]
# Rules for autotile mapping
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}
# Set is faster to lookup than lists
AUTOTILE_TYPES = {"grass", "stone"}
PHYSICS_TILES = {"grass", "stone"}


class Tilemap:
    def __init__(
        self,
        game,
        tile_size=16,
    ):
        self.tile_size = tile_size
        self.game = game
        # two systems of tiles
        self.tilemap = {}  # convinient for handling physics

        self.offgrid_tiles = []  # tiles ie places all over grid

    # id_pairs is the list of type:variant
    def extract(self, id_pairs, keep=False):
        result = []

        for tile in self.offgrid_tiles.copy():
            if (tile["type"], tile["variant"]) in id_pairs:
                result.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

                    pass

        for location in self.tilemap.copy():
            tile = self.tilemap[location]

            if (tile["type"], tile["variant"]) in id_pairs:
                result.append(tile.copy())

                # To be sure
                result[-1]["pos"] = result[-1]["pos"].copy()

                result[-1]["pos"][0] *= self.tile_size
                result[-1]["pos"][1] *= self.tile_size

                if not keep:
                    del self.tilemap[location]

                    pass
        return result

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

    def save(self, path):
        f = open(path, "w")
        json.dump(
            {
                "tilemap": self.tilemap,
                "tile_size": self.tile_size,
                "offgrid": self.offgrid_tiles,
            },
            f,
        )
        f.close()

    def load(self, path):
        f = open(path, "r")
        tilemap_data = json.load(f)
        f.close()

        self.tilemap = tilemap_data["tilemap"]
        self.tile_size = tilemap_data["tile_size"]
        self.offgrid_tiles = tilemap_data["offgrid"]

    def autotile(self):
        for location in self.tilemap:
            tile = self.tilemap[location]
            neighbours = set()
            for offset in AUTOTILE_OFFSETS:
                check_location = (
                    str(tile["pos"][0] + offset[0])
                    + ";"
                    + str(tile["pos"][1] + offset[1])
                )
                if check_location in self.tilemap:
                    # do stuff
                    if self.tilemap[check_location]["type"] == tile["type"]:
                        neighbours.add(offset)
            neighbours = tuple(sorted(neighbours))
            if (tile["type"] in AUTOTILE_TYPES) and (neighbours in AUTOTILE_MAP):
                tile["variant"] = AUTOTILE_MAP[neighbours]

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
