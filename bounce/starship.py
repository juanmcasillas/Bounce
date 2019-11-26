import pygame
from Box2D import *
import math

import  bounce





class SpriteAnim(pygame.sprite.Sprite):
    def __init__(self,parent):
        self.parent = parent
        pygame.sprite.Sprite.__init__(self)   
        # frames have (image, ms_duration)
        self.frames = []
        self.index = 0
        self.timestamp = 0
        self.index = 0
        self._state = "play"
        self.image = None
        self.pos = None

    def init(self, pos=None):

        if len(self.frames) == 0:
            raise ValueError("Sprite has no frames. Bailing out")
        
        self.pos = pos

        self.rect = self.frames[0][0].get_rect()
        self.empty = pygame.Surface((1,1),  pygame.SRCALPHA| pygame.HWSURFACE )
        self.empty.fill((0,0,0,0))
        self.image = self.frames[0][0]

        self.stop()  # animation stopped
        self.clear() # image empty


    def play(self):
        self._state = "play"
    
    def stop(self):
        self._state = "stop"

    def clear(self):
        self.image = self.empty
        self.rect = self.empty.get_rect()
        self.index = 0 # reset cycle animation
        self.timestamp = 0

    def addFrame(self, image, duration):
        self.frames.append( (image, duration) )
        self.rect = image.get_rect()

    def update(self):
        
        if self._state == "stop":
            return
        
        if len(self.frames) == 0:
            raise ValueError("Sprite has no frames. Bailing out")

        time_delta = self.parent.app.clock.get_time()
        frame, duration = self.frames[self.index]

        if (self.timestamp + time_delta)  > duration:
            # move to other frame.
            self.timestamp = 0
            self.index += 1
            if self.index > len(self.frames)-1:
                self.index = 0
        else:
            self.timestamp += time_delta    


        self.rect = frame.get_rect()




class SpritePhysics(pygame.sprite.Sprite):
    def __init__(self, app, image, body):
        pygame.sprite.Sprite.__init__(self)            
        self.app = app
        self.image_orig = image.copy()
        self.image = self.image_orig
        self.body = body
        self.rect = self.image.get_rect()

    def update(self):
  
        
        if not self.body.awake:
            return
        x, y = bounce.ToPixels(self.body.transform.position)
        angle = self.body.transform.angle

        self.rect = self.image_orig.get_rect()
        self.rect.center = (x,y)
        self.image, self.rect = bounce.rotate_by_point( self.image_orig, self.rect, math.degrees(angle), (x,y))

class EngineAnim(SpriteAnim):
    def __init__(self,parent):
        super().__init__(parent)

    def update(self):
        
        if self._state == "stop":
            return
        
        if len(self.frames) == 0:
            raise ValueError("Sprite has no frames. Bailing out")

        time_delta = self.parent.app.clock.get_time()
        frame, duration = self.frames[self.index]

        if (self.timestamp + time_delta)  > duration:
            # move to other frame.
            self.timestamp = 0
        
            elapsed = self.parent.app.get_keypressed_time(pygame.K_q) / 1000 
      
            if elapsed >= 0 and elapsed <= 1.0:
                max_frames = 2
            if elapsed > 1.0 and elapsed <= 2.0:
                max_frames = 4
            if elapsed > 2.0:
                max_frames = len(self.frames)-1

            self.index += 1
            if self.index > max_frames:
                self.index = 0




        else:
            self.timestamp += time_delta    


        self.rect = frame.get_rect()
        #
        # do the required transformations    
        #
        # 1 get physics info
        # 2 position the sprite in world pixels coords relative to its parent (if any)
        # 3 rotate
        #

        angle = self.parent.angle

        if self.pos:
            # harcoded, must be configured outside.
            # set the relative position from parent, from the CENTER.
            self.rect.midtop = b2Vec2(self.parent.rect.center) + self.pos

        self.image, self.rect = bounce.rotate_by_point( frame, self.rect, math.degrees(angle), self.parent.rect.center)


class Starship(pygame.sprite.Sprite):
    def __init__(self, app):
        self.app = app
        self.engine = EngineAnim(self)
        self.angle = 0 # radians

        pygame.sprite.Sprite.__init__(self)
        
        self.loadFromMap()
        self.engine.init((0,40)) ## TODO, relative position to the CENTER of the image

        #define the Physics body

    def move_from_center( self, pos ):
        " move the element to the pos with center align"
        sc = b2Vec2(pos)
        sc = sc - (self.rect.width/2, (self.rect.height)/2)
        self.rect.center = pos
 

    def update(self):

        x, y = bounce.ToPixels(self.body.transform.position)
        r = self.body.transform.angle
        
        # this will be used from the childs
        self.image, self.rect = bounce.rotate_by_center(self.orig_image, math.degrees(r))
        self.rect.center = (x,y)
        self.angle = r




    def loadFromMap(self):
        try:
            group = self.app.wmap.tmx.get_layer_by_name("objects")
        except ValueError as e:
            print("Can't find objects layer in the map. Ignoring them")
            return

        # load animations

        for gid, props in self.app.wmap.tmx.tile_properties.items():
            if 'parent' in props.keys() and props['parent'].lower() == "starship":
                for animation_frame in props['frames']:
                    image = self.app.wmap.tmx.get_tile_image_by_gid(gid)
                    
                    self.engine.addFrame(image.copy(), animation_frame.duration)                    
                    print("adding animation frame %d" % gid)


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
        wcenter = bounce.ScaleToWorld( ( self.rect.width/2, self.rect.height/2 ))

        self.body = bounce.Physics.world.CreateDynamicBody(
                position = bounce.ToWorld(self.rect.center),
                #angle =math.pi/4.2,
                angle = math.radians(-starship.rotation),
                fixtures = b2FixtureDef(
                    shape = b2PolygonShape(box= wcenter),
                    density = starship.properties['density'],
                    friction = starship.properties['friction'],
                    restitution = starship.properties['restitution'])
                )          