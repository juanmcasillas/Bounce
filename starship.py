import pygame
from Box2D import *
import math

def vecMod(v):
    r = math.sqrt( math.pow(v[0],2) + math.pow(v[1],2))
    return r


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
        self.empty = pygame.Surface(self.rect.size,  pygame.SRCALPHA| pygame.HWSURFACE )
        self.empty.fill((0,0,0,0))
        self.image = self.frames[0][0]

    def play(self):
        self._state = "play"
    
    def stop(self):
        self._state = "stop"

    def empty(self):
        self.image = self.empty
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

        self.image, self.rect = rotate_by_point( frame, self.rect, math.degrees(angle), self.parent.rect.center)

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
        self.engine = SpriteAnim(self)
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

        x, y = self.app.physics.ToPixels(self.body.transform.position)
        r = self.body.transform.angle
        
        # this will be used from the childs
        self.image, self.rect = self.rot_center(self.orig_image, math.degrees(r))
        self.rect.center = (x,y)
        self.angle = r


    def rot_center(self, image, angle):
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