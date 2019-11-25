import pygame
import sys
import os
from pygame.locals import *
import math
import sys
import numpy
import pygame


def rotate_by_point( image, rect, angle, point=None):
    """rotate the image image in world pixel position rect, from the point point at angle angle(degrees)
    rect is in world pixel coordinates
    point is in world pixel coordinates (can be inside the rect, of course, to rotate from inside the rect)
    angle is expressed in degrees (ccw)
    
    this method create a new surface centered in the desired point, copies the image an issues a perfect 
    rotation.
    """

    point = point or rect.center

    # create a new surface, centered in the point, including our new rectangle.
    ix, iy = rect.center
    px, py = point

    szx = 2* (math.fabs(px - ix) + rect.width/2)
    szy = 2* (math.fabs(py - iy) + rect.height/2)

    # create the new image.
    rot_rect = pygame.Rect( (0,0),(0,0) )
    rot_rect.width = szx
    rot_rect.height = szy
    rot_rect.center = point

    point_vector = ()

    rot_image = pygame.Surface(rot_rect.size,  pygame.SRCALPHA| pygame.HWSURFACE )
    rot_image.fill((0,0,0,0))
    # copy the image to the right place in the new surface.

    in_x = rect.x-rot_rect.x
    in_y = rect.y-rot_rect.y


    rot_image.blit( image,(in_x, in_y))
    
    rot_image_ret = pygame.transform.rotate(rot_image, angle)
    rot_rect_ret = rot_image_ret.get_rect(center=rot_rect.center)
    return rot_image_ret, rot_rect_ret


    
if __name__ == "__main__":

    pygame.init()
    pygame.font.init()
    pygame.mouse.set_visible(False)
    pygame.display.set_caption("Pygame Test")
    clock = pygame.time.Clock()

    image = pygame.image.load("../assets/starship.png")
    image_rect = image.get_rect()

    image_rect.center = (int(1024/2), int(100)) # topleft

    #image_rect.center = (int(200), int(100)) # topleft
    #image_rect.center = (int(700), int(100)) # topright
    #image_rect.center = (int(200), int(600)) # bottomleft
    #image_rect.center = (int(700), int(600)) # bottomright
    #image_rect.center = (int(1024/2), int(768/2)) #same point
    
    

    #point = ( int(1024/2), int(768/2) )
    point = image_rect.midbottom

    screen = pygame.display.set_mode((1024, 768), pygame.HWSURFACE|pygame.DOUBLEBUF)
    _running = True

    angle = 0

    while _running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                _running = False
                break
            
        # original data
        #screen.blit(image,image_rect)
        #pygame.draw.rect(screen,(255,255,255),image_rect,1)  
        screen.set_at(point, (255,0,0))

        rot_image, rot_rect = rotate_by_point(image, image_rect, angle, point)

        # rotated data    
        screen.blit(rot_image,rot_rect)
        pygame.draw.rect(screen,(255,0,0),rot_rect,1)  


        pygame.display.flip()
        screen.fill((0,0,0,0))
        clock.tick(60)
        angle = (angle + 1) % 360

    pygame.quit()     