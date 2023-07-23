# Creating basic window

import pygame
import sys

WIDTH,HEIGHT = 720,480
class Game:
    def __init__(self):

        pygame.init()
        pygame.display.set_caption('Platformer Game')

        self.screen = pygame.display.set_mode((WIDTH,HEIGHT)) 
        self.clock = pygame.time.Clock()

        
    def run(self):

        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # main screen ---------------------------------------------------------|
            self.screen.fill((255,255,0))

            # display stuff -------------------------------------------------------|
            pygame.display.update()
            self.clock.tick(60)


        # Quit --------------------------------------------------------------------|
        pygame.quit()
        sys.exit()


Game().run()

