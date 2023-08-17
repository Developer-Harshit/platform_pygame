# Enemies,Guns,Death & Sparks

import pygame
import sys
import math
from random import random, randint
from scripts.entites import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle, Spark
from scripts.utils import load_img, load_images, Animation

print("Starting Game")

WIDTH, HEIGHT = 320 * 3, 240 * 3
BLUE = (21, 50, 201)
RED = (215, 20, 70)
BG_COLOR = (21, 21, 21)
LEVELS = ["0", "1", "2", "3"]


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
            # Basic assets --------------------------------------------------------|
            "player": load_img("entities/player.png"),
            "stone": load_images("tiles/stone"),
            "grass": load_images("tiles/grass"),
            "decor": load_images("tiles/decor"),
            "large_decor": load_images("tiles/large_decor"),
            "spawners": load_images("tiles/spawners"),
            "clouds": load_images("clouds"),
            "background": load_img("background.png"),  # 320 x 240
            # Player Animation ----------------------------------------------------|
            "player/idle": Animation(
                load_images("entities/player/idle"),
                duration=7,
            ),
            "player/run": Animation(
                load_images("entities/player/run"),
                duration=5,
            ),
            "player/jump": Animation(
                load_images("entities/player/jump"),
                duration=5,
            ),
            "player/slide": Animation(
                load_images("entities/player/slide"),
            ),
            "player/wall_slide": Animation(
                load_images("entities/player/wall_slide"),
            ),
            # Enemy Animation -----------------------------------------------------|
            "enemy/idle": Animation(
                load_images("entities/enemy/idle"),
                duration=7,
            ),
            "enemy/run": Animation(
                load_images("entities/enemy/run"),
                duration=5,
            ),
            # Particle Animation --------------------------------------------------|
            "particle/leaf": Animation(
                load_images(
                    "particles/leaf",
                ),
                duration=20,
                loop=False,
            ),
            "particle/particle": Animation(
                load_images("particles/particle"), duration=7, loop=False
            ),
            "gun": load_img("gun.png"),
            "projectile": load_img("projectile.png"),
        }

        self.tilemap = Tilemap(self)
        self.map_id = 0
        self.load_level(self.map_id)

        self.clouds = Clouds(self.assets["clouds"], 20)

    def load_level(self, map_id):
        self.tilemap.load(f"data/maps/{map_id}.json")

        self.player = Player(self, (50, 50), (8, 15))  # *

        self.scroll = [0, 0]  # for camera #*

        self.leaf_init()  # *

        self.spawn_init()  # *

        self.sparks = []  # *

        self.particles = []  # *

        self.projectiles = []  # *

        self.death = 0  # *
        pass

    def leaf_init(self):
        self.leaf_rect = []
        for tree in self.tilemap.extract([("large_decor", 2)], keep=True):  # *
            self.leaf_rect.append(
                pygame.Rect(4 + tree["pos"][0], 4 + tree["pos"][1], 23, 13)
            )

    def spawn_init(self):
        self.enemies = []
        # Extracting spawners/entity tile
        for spawner in self.tilemap.extract((("spawners", 0), ("spawners", 1))):  # *
            if spawner["variant"] == 0:
                self.player.pos = spawner["pos"]
            else:
                self.enemies.append(Enemy(self, spawner["pos"], (8, 15)))

                # its enemy entity
                pass

    def run(self):
        running = True

        while running:
            if self.death:
                self.death += 1
                if self.death > 40:
                    self.load_level(self.map_id)

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
            # Spawning Leaf -------------------------------------------------------|
            for rect in self.leaf_rect:
                # to spawn leaves based on tree size

                if random() * 39999 < rect.width * rect.height:
                    pos = (
                        rect.x + random() * rect.width,
                        rect.y + random() * rect.height,
                    )
                    self.particles.append(
                        Particle(
                            self,
                            "leaf",
                            pos,
                            velocity=[-0.1, 0.3],
                            frame=randint(0, 20),
                        )
                    )
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

            # For Enemies ----------------------------------------------------------|
            for enemy in self.enemies:
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, render_scroll)  # assigned offset = scroll
                if kill:
                    self.enemies.remove(enemy)

            # For Player ----------------------------------------------------------|
            if not self.death:
                self.player.update(
                    self.tilemap, ((self.movement[1] - self.movement[0]) * 2, 0)
                )
                self.player.render(
                    self.display, render_scroll
                )  # assigned offset = scroll

            # For Projectiles -----------------------------------------------------|
            # Format of each projectile[ [x,y],direction,timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets["projectile"]
                projectile_pos = (
                    projectile[0][0] - img.get_width() / 2,
                    projectile[0][1] - img.get_height() / 2,
                )
                self.display.blit(
                    img,
                    (
                        projectile_pos[0] - render_scroll[0],
                        projectile_pos[1] - render_scroll[1],
                    ),
                )
                # Collided with wall
                if self.tilemap.check_solid(projectile[0]):
                    # Adding sparks effect
                    for i in range(7):
                        self.sparks.append(
                            Spark(
                                self.projectiles[0][0],
                                random() - 0.5 + (math.pi if projectile[1] > 0 else 0),
                                2 * random(),
                            )
                        )
                    self.projectiles.remove(projectile)

                # Projectile tieout
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                # Hit the player
                elif abs(self.player.is_dashing) < 50:
                    if self.player.get_rect().collidepoint(projectile[0]):
                        # Player recieves damage
                        # Spark Explosion
                        for i in range(10):
                            angle = random() * math.pi * 2
                            speed = random() * 5
                            self.sparks.append(
                                Spark(
                                    self.player.get_rect().center,
                                    angle,
                                    speed,
                                )
                            )

                        self.projectiles.remove(projectile)
                        self.death = 1
            # For Sparks ----------------------------------------------------------|
            for spark in self.sparks.copy():
                kill = spark.update()

                spark.render(self.display, render_scroll)

                if kill:
                    self.sparks.remove(spark)

            # For Particle --------------------------------------------------------|
            for particle in self.particles.copy():
                kill = particle.update()
                if particle.type == "leaf":
                    particle.pos[0] += math.sin(particle.animation.frame * 0.03) * 0.4

                particle.render(self.display, offset=render_scroll)

                if kill:
                    self.particles.remove(particle)

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
                        # self.player.velocity[1] = -5
                        self.player.jump()
                    if event.key == pygame.K_l:
                        self.player.dash()

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
