import pygame
from Box2D import *
import math

def vecMod(v):
    r = math.sqrt( math.pow(v[0],2) + math.pow(v[1],2))
    return r

class StarshipEngine(pygame.sprite.Sprite):
    def __init__(self,app):
        self.app = app
        pygame.sprite.Sprite.__init__(self)    
        
        self.images = []
        self.duration = 0
        self.index = 0
        self.stamp = 0
        self.timer = 0

    def update_local(self):
        time_delta = self.app.clock.get_time()

        if (self.stamp + time_delta)  > self.duration:
        
            if self.timer == 0:
                self.index = 0
                self.stamp = 0
                self.image = self.images[self.index].copy()

            else:
                
                secs = self.timer / 1000
                max_images = 0

                if secs > 0.0 and secs < 1.5:
                    max_images = 2
                if secs >= 1.5 and secs < 2.0:
                    max_images = 4
                if secs >= 2.0:
                    max_images = len(self.images)-1

                #del self.image
                self.image = self.images[self.index].copy()
                self.stamp = 0

                if self.index > max_images or self.index == len(self.images)-1:
                    self.index = 1
                else:
                    self.index += 1


        else:
            self.stamp += time_delta
        
    def update(self):
        pass

class Starship(pygame.sprite.Sprite):
    def __init__(self, app):
        self.app = app
        pygame.sprite.Sprite.__init__(self)
        
        self.loadFromMap()

        #define the Physics body

    def move_from_center( self, pos ):
        " move the element to the pos with center align"
        sc = b2Vec2(pos)
        sc = sc - (self.rect.width/2, (self.rect.height)/2)
        self.rect.center = pos
 

    def update(self):

        myrect = self.orig_image.get_rect()
        enginerect = self.engine.image.get_rect()

        offset = enginerect.height
        
        self.image_tmp = pygame.Surface( ( myrect.width, myrect.height+enginerect.height+offset), pygame.SRCALPHA| pygame.HWSURFACE )
        self.topleft = myrect.topleft

        self.image_tmp.blit( self.orig_image, (0, offset))
        pos = b2Vec2(myrect.midbottom) - b2Vec2(enginerect.width/2,0 ) + b2Vec2(0, offset)
        self.image_tmp.blit( self.engine.image, pos, enginerect )

        #print(self.body.linearVelocity, self.body.angularVelocity, self.body.linearVelocity.length)
        x, y = self.app.physics.ToPixels(self.body.transform.position)
        r = self.body.transform.angle
        self.image, self.rect = self.rot_center(self.image_tmp, math.degrees(r))
   
        self.rect.center = (x,y)
        self.engine.update_local()
        
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

        self.engine = StarshipEngine(self.app)
        
        # load animations


        for gid, props in self.app.wmap.tmx.tile_properties.items():
            if 'parent' in props.keys() and props['parent'].lower() == "starship":
                for animation_frame in props['frames']:
                    image = self.app.wmap.tmx.get_tile_image_by_gid(gid)
                    
                    self.engine.images.append(image.copy())
                    self.engine.duration = animation_frame.duration 
                    self.engine.rect = image.get_rect()
                    print("adding animation frame %d" % gid)

   
        empty = pygame.Surface(self.engine.images[0].get_rect().size, pygame.SRCALPHA| pygame.HWSURFACE )
        empty.fill((0,0,0,0)) # RGBALPHA
        self.engine.images = [ empty ] + self.engine.images
        self.engine.image = self.engine.images[0].copy()
        self.index = 0



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
        wcenter = self.app.physics.ScaleToWorld( ( self.rect.width/2, self.rect.height/2 ))


        self.body = self.app.world.CreateDynamicBody(
                position = self.app.physics.ToWorld(self.rect.center),
                #angle =math.pi/4.2,
                angle = math.radians(-starship.rotation),
                fixtures = b2FixtureDef(
                    shape = b2PolygonShape(box= wcenter),
                    density = starship.properties['density'],
                    friction = starship.properties['friction'],
                    restitution = starship.properties['restitution'])
                )          