
import pygame
from Box2D import *
import math
import bounce

from . sprite_base import *

class SpritePhysics(SpriteAnim):
    def __init__(self, clock, body):
        SpriteAnim.__init__(self, clock)            
        self.body = body
        
    def update(self):
        # move the selected frame
        # maintain rect at this position, becouse it's stopped

        super().update(update_pos=self.body.awake)
 
        if self._state == "clear":
           return

        img = self.frames[self.index][0]
        self.rect = img.get_rect()
        
        #if not angle and not relative:
        x, y = bounce.ToPixels(self.body.transform.position)
        angle = self.body.transform.angle

        # watch for the copy here

        self.rect.center = (x,y)
        self.image, self.rect = bounce.rotate_by_point(img, self.rect, math.degrees(angle), (x,y))
        
        #else:
        #    self.rect.center = b2Vec2(relative.center) + self.pos 
        #    self.image, self.rect = bounce.rotate_by_point( img, self.rect, math.degrees(angle), relative.center)