import pygame
import math


def render_text(surface, text, pos, size=24, color=(255,255,255), font_family=None):
    """
    Render text into the given surface.
    """
    font_family = font_family or "consolas"
    font = pygame.font.Font(pygame.font.match_font(font_family), size)
    text_surface = font.render(text, False, color)
    surface.blit(text_surface, dest=(pos))

def rotate_by_center(image, angle):
    """rotate an image while keeping its center"""
    rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)
    return rot_image,rot_rect

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
