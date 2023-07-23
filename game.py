# Images ,Input and Collisions

import pygame
import sys

WIDTH,HEIGHT = 720,480
BLUE = (21,50,201)
RED =  (215,20,70)
BG_COLOR = (21,21,21)
class Game:
    def __init__(self):

        pygame.init()
        pygame.display.set_caption('Platformer Game')

        self.screen = pygame.display.set_mode((WIDTH,HEIGHT)) 
        self.clock = pygame.time.Clock()
        self.img = pygame.image.load("data/images/clouds/cloud_2.png")

        # To make the black background in the image as transparent
        self.img.set_colorkey((0,0,0))

        self.img_pos = [100,100]
        self.movement = [False,False,False,False] # Left ,Right ,Top ,Down

        self.block = pygame.Rect(200,50,50,100)
        
    def run(self):

        running = True

        while running:
            # draw stuff ----------------------------------------------------------|
            self.screen.fill(BG_COLOR)

            # bliting img in surface
            self.img_pos[0] += (self.movement[1] - self.movement[0]) *2
            self.img_pos[1] += (self.movement[3] - self.movement[2]) *2


            img_r = pygame.Rect(*self.img_pos,*self.img.get_size())

            # Alternatively you can do this
            # img_r = pygame.Rect(self.img_pos[0],self.img_pos[1],self.img.get_width(),self.img.get_height())
            
            # Checking collision --------------------------------------------------|
            if img_r.colliderect(self.block):
                
                pygame.draw.rect(self.screen,RED,self.block) # Screen , Color , Rect
            else:
                pygame.draw.rect(self.screen,BLUE,self.block) # Screen , Color , Rect

            self.screen.blit(self.img,self.img_pos)

            # you can also blit something in image as img = surface
            # self.img.blit(self.screen,self.img_pos)

            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
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

            # update stuff --------------------------------------------------------|
            pygame.display.update()
            self.clock.tick(60)


        # Quit --------------------------------------------------------------------|
        pygame.quit()
        sys.exit()


Game().run()

