# Level Editor

import pygame
import sys

from scripts.tilemap import Tilemap
from scripts.utils import load_img, load_images

print("Starting Game")

RENDER_SCALE = 2
WIDTH, HEIGHT = 320 * RENDER_SCALE, 240 * RENDER_SCALE

BLUE = (21, 50, 201)

RED = (215, 20, 70)

BG_COLOR = (21, 21, 21)


class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Level Editor")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        # display is half of screen size

        self.display = pygame.Surface((WIDTH / 2, HEIGHT / 2))

        self.clock = pygame.time.Clock()

        self.movement = [False, False, False, False]  # Left , Right , Top , Bottom

        self.assets = {
            "grass": load_images("tiles/grass"),
            "stone": load_images("tiles/stone"),
            "decor": load_images("tiles/decor"),
            "large_decor": load_images("tiles/large_decor"),
            "spawners": load_images("tiles/spawners"),
            "leaf": load_images("particles/leaf"),
        }

        self.tilemap = Tilemap(self)
        try:
            self.tilemap.load("data/maps/test.json")
        except FileNotFoundError:
            print("file does not exist")
        self.scroll = [0, 0]  # for camera

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_var = 0

        self.right_click = False
        self.left_click = False
        self.shift_click = False
        self.on_grid = True

    def run(self):
        running = True

        while running:
            self.display.fill((BG_COLOR))

            # Scroll Behavior -----------------------------------------------------|
            if self.shift_click:
                self.scroll[0] += (self.movement[1] - self.movement[0]) * 4
                self.scroll[1] += (self.movement[3] - self.movement[2]) * 4
            else:
                self.scroll[0] += (self.movement[1] - self.movement[0]) * 1.5
                self.scroll[1] += (self.movement[3] - self.movement[2]) * 1.5
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # Getting current tile ------------------------------------------------|
            current_tile_img = self.assets[self.tile_list[self.tile_group]][
                self.tile_var
            ]

            # Getting mouse pos
            mouse_pos = pygame.mouse.get_pos()

            # Diving by render scale cuz why not
            mouse_pos = (
                mouse_pos[0] / RENDER_SCALE,
                mouse_pos[1] / RENDER_SCALE,
            )
            # coordinates of mouse in terms of tilemap
            tile_pos = (
                int((mouse_pos[0] + self.scroll[0]) // self.tilemap.tile_size),
                int((mouse_pos[1] + self.scroll[1]) // self.tilemap.tile_size),
            )
            tile_location = str(tile_pos[0]) + ";" + str(tile_pos[1])

            # Adding TIles --------------------------------------------------------|
            if self.left_click and self.on_grid:
                self.tilemap.tilemap[tile_location] = {
                    "type": self.tile_list[self.tile_group],
                    "variant": self.tile_var,
                    "pos": tile_pos,
                }
            if self.right_click:
                if tile_location in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_location]
                # Un optimized way to do it
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile["type"]][tile["variant"]]
                    tile_rect = pygame.Rect(
                        tile["pos"][0] - self.scroll[0],
                        tile["pos"][1] - self.scroll[1],
                        tile_img.get_width(),
                        tile_img.get_height(),
                    )
                    if tile_rect.collidepoint(mouse_pos):
                        self.tilemap.offgrid_tiles.remove(tile)

            # Bliting the preview -------------------------------------------------|
            current_tile_img.set_alpha(80)
            # Do not touch --------------------------------------------------------|
            if self.shift_click:
                # if self.on_grid:
                if tile_location in self.tilemap.tilemap:
                    self.display.fill(
                        (160, 110, 200),
                        (
                            tile_pos[0] * self.tilemap.tile_size - self.scroll[0],
                            tile_pos[1] * self.tilemap.tile_size - self.scroll[1],
                            self.tilemap.tile_size,
                            self.tilemap.tile_size,
                        ),
                    )
                else:
                    self.display.fill(
                        (160, 110, 200), (mouse_pos[0], mouse_pos[1], 5, 5)
                    )
                # else:
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile["type"]][tile["variant"]]
                    tile_rect = pygame.Rect(
                        tile["pos"][0] - self.scroll[0],
                        tile["pos"][1] - self.scroll[1],
                        tile_img.get_width(),
                        tile_img.get_height(),
                    )
                    if tile_rect.collidepoint(mouse_pos):
                        self.display.fill((160, 110, 200), tile_rect)
                        break
                else:
                    self.display.fill(
                        (160, 110, 200), (mouse_pos[0], mouse_pos[1], 5, 5)
                    )
            else:
                if self.on_grid:
                    self.display.blit(
                        current_tile_img,
                        (
                            tile_pos[0] * self.tilemap.tile_size - self.scroll[0],
                            tile_pos[1] * self.tilemap.tile_size - self.scroll[1],
                        ),
                    )
                else:
                    self.display.blit(
                        current_tile_img,
                        mouse_pos,
                    )
            # ---------------------------------------------------------------------|
            # Bliting current tile
            current_tile_img.set_alpha(200)
            # Blitting all tiles
            self.tilemap.render(self.display, offset=render_scroll)

            self.display.fill(
                (10, 10, 10),
                (
                    3,
                    3,
                    current_tile_img.get_width() + 4,
                    current_tile_img.get_height() + 4,
                ),
            )
            if not self.on_grid:
                pygame.draw.circle(
                    self.display,
                    (255, 255, 255),
                    (WIDTH / RENDER_SCALE - 10, HEIGHT / RENDER_SCALE - 10),
                    5,
                )

            self.display.blit(current_tile_img, (5, 5))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Mouse Down Event ------------------------------------------------|
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left Click
                        self.left_click = True
                        # Adding this logic here to avoid having unnessary tiles
                        if not self.on_grid:
                            self.tilemap.offgrid_tiles.append(
                                {
                                    "type": self.tile_list[self.tile_group],
                                    "variant": self.tile_var,
                                    "pos": (
                                        mouse_pos[0] + self.scroll[0],
                                        mouse_pos[1] + self.scroll[1],
                                    ),
                                }
                            )
                    if event.button == 3:  # Right Click
                        self.right_click = True
                    if self.shift_click:
                        if event.button == 4:  # Up Mouse Scroll
                            # Whenever you got to loop values use modulo
                            self.tile_var = (self.tile_var - 1) % len(
                                self.assets[self.tile_list[self.tile_group]]
                            )
                        if event.button == 5:  # Dwon Mouse Scroll
                            self.tile_var = (self.tile_var + 1) % len(
                                self.assets[self.tile_list[self.tile_group]]
                            )
                    # Changing tile Group -----------------------------------------|
                    else:
                        if event.button == 4:  # Up Mouse Scroll
                            # Whenever you got to loop values use modulo
                            self.tile_group = (self.tile_group - 1) % len(
                                self.tile_list
                            )
                            self.tile_var = 0
                        if event.button == 5:  # Dwon Mouse Scroll
                            self.tile_group = (self.tile_group + 1) % len(
                                self.tile_list
                            )
                            self.tile_var = 0

                if event.type == pygame.KEYDOWN:
                    # X-Axis ------------------------------------------------------|
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    # Y-Axis ------------------------------------------------------|
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = True
                    # Others ------------------------------------------------------|
                    if event.key == pygame.K_LSHIFT:
                        self.shift_click = True
                    if event.key == pygame.K_o:
                        self.tilemap.save("data/maps/test.json")
                    if event.key == pygame.K_u:
                        self.tilemap.autotile()

                # Mouse Up Event --------------------------------------------------|
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left Click
                        self.left_click = False
                    if event.button == 3:  # Right Click
                        self.right_click = False

                if event.type == pygame.KEYUP:
                    # X-Axis ------------------------------------------------------|
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False
                    # Y-Axis ------------------------------------------------------|
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = False
                    # Others ------------------------------------------------------|
                    if event.key == pygame.K_LSHIFT:
                        self.shift_click = False
                    if event.key == pygame.K_g:
                        self.on_grid = not self.on_grid

            # Rendering Screen ----------------------------------------------------|

            self.screen.blit(
                pygame.transform.scale(self.display, self.screen.get_size()), (0, 0)
            )

            pygame.display.update()

            self.clock.tick(60)

        # Quit --------------------------------------------------------------------|

        pygame.quit()

        sys.exit()


if __name__ == "__main__":
    Editor().run()

print("Game Over")
