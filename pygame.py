import pygame, sys
#from pygame.locals import *

pygame.init()
displaySurface = pygame.display.set_mode((300, 400), 0, 32)
pygame.display.set_caption("The Weakest Link")

white = pygame.Color(255, 255, 255)

displaySurface.fill(white)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
