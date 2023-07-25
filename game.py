# Images ,Input and Physics

import pygame
import sys
from scripts.entites import PhysicsEntity
from scripts.tilemap import Tilemap
from scripts.utils import load_img, load_images

print("Starting Game")

WIDTH, HEIGHT = 720, 480
BLUE = (21, 50, 201)
RED = (215, 20, 70)
BG_COLOR = (21, 21, 21)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Platformer Game")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.display = pygame.Surface((WIDTH / 2, HEIGHT / 2))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]  # Left ,Right

        self.assets = {
            "player": load_img("entities/player.png"),
            "stone": load_images("tiles/stone"),
            "grass": load_images("tiles/grass"),
        }
        self.tilemap = Tilemap(self)
        self.player = PhysicsEntity(self, "player", (50, 50), (8, 15))

    def run(self):
        running = True

        while running:
            # compute stuff -------------------------------------------------------|
            self.player.update(
                self.tilemap, ((self.movement[1] - self.movement[0]) * 2, 0)
            )

            # print(self.tilemap.find_neighbours(self.player.pos))

            # draw stuff ----------------------------------------------------------|
            self.display.fill(BG_COLOR)
            self.tilemap.render(self.display)

            self.player.render(self.display)

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

            # update stuff --------------------------------------------------------|
            self.screen.blit(
                pygame.transform.scale(self.display, self.screen.get_size()), (0, 0)
            )
            pygame.display.update()
            self.clock.tick(60)

        # Quit --------------------------------------------------------------------|
        pygame.quit()
        sys.exit()


Game().run()
print("Game Over")
