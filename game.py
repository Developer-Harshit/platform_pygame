# Level Editor

import pygame
import sys
from scripts.entites import PhysicsEntity, Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.utils import load_img, load_images, Animation

print("Starting Game")

WIDTH, HEIGHT = 320 * 3, 240 * 3
BLUE = (21, 50, 201)
RED = (215, 20, 70)
BG_COLOR = (21, 21, 21)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Platformer Game")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        # display is half of screen size
        self.display = pygame.Surface((WIDTH / 2, HEIGHT / 2))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]  # Left ,Right

        self.assets = {
            "player": load_img("entities/player.png"),
            "stone": load_images("tiles/stone"),
            "grass": load_images("tiles/grass"),
            "decor": load_images("tiles/decor"),
            "large_decor": load_images("tiles/large_decor"),
            "spawners": load_images("tiles/spawners"),
            "clouds": load_images("clouds"),
            "background": load_img("background.png"),  # 320 x 240
            "player/idle": Animation(
                load_images("entities/player/idle"), duration=7, loop=True
            ),
            "player/run": Animation(
                load_images("entities/player/run"), duration=5, loop=True
            ),
            "player/jump": Animation(
                load_images("entities/player/jump"), duration=5, loop=True
            ),
        }
        self.tilemap = Tilemap(self)
        self.tilemap.load("data/maps/0.json")

        self.player = Player(self, (50, 50), (8, 15))
        self.clouds = Clouds(self.assets["clouds"], 20)
        self.scroll = [0, 0]  # for camera

    def run(self):
        running = True
        while running:
            # For Camera ----------------------------------------------------------|

            self.scroll[0] += (
                self.player.get_rect().centerx
                - self.display.get_width() / 2
                - self.scroll[0]
            ) / 30
            self.scroll[1] += (
                self.player.get_rect().centery
                - self.display.get_height() / 2
                - self.scroll[1]
            ) / 30
            # THats why we are converting it into int
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # For Background ------------------------------------------------------|
            self.display.blit(
                pygame.transform.scale(
                    self.assets["background"], self.display.get_size()
                ),
                (0, 0),
            )
            # For clouds ----------------------------------------------------------|
            self.clouds.update()
            self.clouds.render(self.display, render_scroll)
            # For TileMap ---------------------------------------------------------|
            self.tilemap.render(self.display, render_scroll)  # assigned offset = scroll

            # For Player ----------------------------------------------------------|
            self.player.update(
                self.tilemap, ((self.movement[1] - self.movement[0]) * 2, 0)
            )
            self.player.render(self.display, render_scroll)  # assigned offset = scroll

            # Checking Events -----------------------------------------------------|
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    # X-Axis ------------------------------------------------------|
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                        self.player.velocity[1] = -5
                if event.type == pygame.KEYUP:
                    # X-Axis ------------------------------------------------------|
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False

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
    Game().run()
print("Game Over")
