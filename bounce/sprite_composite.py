

import pygame
from Box2D import *
import math
import bounce

from . sprite_physics import *

class SpriteComposite(SpritePhysics):
    def __init__(self, clock, body):
        SpritePhysics.__init__(self, clock, body)            
        self.items_dict = {}
        self.sprites = pygame.sprite.Group()
        self.sprites.add(self)
        
    def draw(self, surface):
        self.sprites.draw(surface)
            
    def add_child(self, name, item, relpos):
        "Item is a SpriteAnim element"
        # move the physical body to the desired position
        item.pos = relpos
        self.items_dict[name] = item
        self.sprites.add(item)

    #def add(self, group):
    #    "add all the sprites to the group so they can be drawed"
    #    for i in self.items:
    #        group.add(i)
    #    group.add(self)

    def update(self):
        SpritePhysics.update(self)

        # update the childs
        for item in self.items_dict.values():
            item.update()
            if item._state != "clear":
                angle = self.body.transform.angle
                item.rect.center = (b2Vec2(self.rect.center) + item.pos)
                item.image, item.rect = bounce.rotate_by_point( item.frames[item.index][0], item.rect, math.degrees(angle), self.rect.center)

            