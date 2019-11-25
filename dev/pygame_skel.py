import pygame
import sys
import os
from pygame.locals import *
import math
import sys
import numpy
import pygame

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    pygame.mouse.set_visible(False)
    pygame.display.set_caption("Pygame Test")
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((1024, 768), pygame.HWSURFACE|pygame.DOUBLEBUF)
    _running = True

    while _running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                _running = False
                break
                
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()    