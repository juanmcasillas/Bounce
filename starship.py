import pygame
from Box2D import *
import math

class Starship(pygame.sprite.Sprite):
    def __init__(self, app):
        self.app = app
        pygame.sprite.Sprite.__init__(self)
 
        self.loadFromMap()

        #define the Physics body

  


    def move_from_center( self, pos ):
        " move the element to the pos with center align"
        sc = b2Vec2(pos)
        sc = sc - (self.rect.width/2, self.rect.height/2)
        self.rect.center = pos
 

    def update(self):
        x, y = self.app.physics.ToPixels(self.body.transform.position)
        r = self.body.transform.angle
        self.image, self.rect = self.rot_center(self.orig_image, math.degrees(r))
        # if x>Config.screen_size[0]-50:
        #     print(x)
        #     x = Config.screen_size[0]-50
        # if y>Config.screen_size[1]-50:
        #     print(y)
        #     y = Config.screen_size[1]-50

        self.move_from_center((x,y))

    def rot_center(self,image, angle):
        """rotate an image while keeping its center"""
        rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = rot_image.get_rect(center=rect.center)
        return rot_image,rot_rect

    def loadFromMap(self):
        try:
            group = self.app.wmap.tmx.get_layer_by_name("objects")
        except ValueError as e:
            print("Can't find objects layer in the map. Ignoring them")
            return

        group = self.app.wmap.tmx.get_layer_by_name("objects")
        starship = self.app.wmap.tmx.get_object_by_name("starship")
        if starship == None:
            print("Can't find starship layer in the map. Fatal. Bailing out")
            sys.exit(0)

        # load startship info from here.
        self.fname = starship.properties['source']
        self.image = starship.image.copy()
        self.orig_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.move_from_center((starship.x, starship.y))

        #define the Physics body    
        wcenter = self.app.physics.ScaleToWorld( ( self.rect.width/2, self.rect.height /2))

        self.body = self.app.world.CreateDynamicBody(
                position = self.app.physics.ToWorld(self.rect.center),
                #angle =math.pi/4.2,
                angle = 0,
                fixtures = b2FixtureDef(
                    shape = b2PolygonShape(box= wcenter),
                    density = starship.properties['density'],
                    friction = starship.properties['friction'],
                    restitution = starship.properties['restitution'])
                )          