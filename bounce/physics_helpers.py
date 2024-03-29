
import bounce
import pygame
from Box2D import *

#
# the userData has to be filled with some meaninful, in order to allow
# the system check what kind of collision happens. Fixture has a method
# to get the body, also.
#
# store contacts as an integer
# -> contact++
# -> contact --
# do things when overall contacts == 0.
#

class ContactListener(b2ContactListener):
    def __init__(self):
        b2ContactListener.__init__(self)
    def BeginContact(self, contact):
        
        if contact.fixtureA.userData:
            # when the Starship is hit by something, this is
            # the handler called
            print("HIT->Starship by something")
        
        if contact.fixtureB.userData:
            # when the  Starship HITS something, this is the
            # handler called
            print("Starship->HITS something")

    def EndContact(self, contact):
        pass
        #print("endContact")
    def PreSolve(self, contact, oldManifold):
        pass
    def PostSolve(self, contact, impulse):
        pass

class ContactFilter(b2ContactFilter):
    def __init__(self):
        b2ContactFilter.__init__(self)

    def ShouldCollide(self, shape1, shape2):
        # Implements the default behavior of b2ContactFilter in Python
        filter1 = shape1.filterData
        filter2 = shape2.filterData
        if filter1.groupIndex == filter2.groupIndex and filter1.groupIndex != 0:
            return filter1.groupIndex > 0
 
        collides = (filter1.maskBits & filter2.categoryBits) != 0 and (filter1.categoryBits & filter2.maskBits) != 0
        return collides


def do_step():
    bounce.Physics.world.Step(bounce.Physics.step, bounce.Physics.velocityIT, bounce.Physics.positionIT)


def clear_surface(color = None):
    color = color or bounce.Colors.Physics.surface_bg
    bounce.Physics.surface.fill(color)


def draw_body(body, color=None, wireFrame=False, surface=None, zoom=1.0):

    surface = surface or bounce.Physics.surface
        
    if body.type == Box2D.b2_dynamicBody:
        color = color or bounce.Colors.Physics.dbody_bg
    if body.type == Box2D.b2_staticBody:
        color = color or bounce.Colors.Physics.sbody_bg

    for fixture in body.fixtures:
        shape = fixture.shape
    
        if isinstance(shape, b2ChainShape):
            vertices = [(bounce.ToPixels(body.transform * v)) for v in shape.vertices]
            if not wireFrame:  
                pygame.draw.lines(surface, color, False, vertices)
            else:
                pygame.draw.lines(surface, color, False, vertices,1)

        elif isinstance(shape, b2CircleShape):
            ## todo, circle here
            if not wireFrame:
                center = bounce.scale_tuple(bounce.ToPixels(body.position), zoom)
                radius, _ = bounce.ScaleToPixels((shape.radius,0))

                pygame.draw.circle(surface, color, bounce.int_tuple(center), int(radius*zoom))
            else:
                pygame.draw.circle(surface, color, bounce.int_tuple(center), int(radius*zoom), 1)

        else:
            #polygon here.
            vertices = [bounce.scale_tuple(bounce.ToPixels(body.transform * v),zoom) for v in shape.vertices]
            if not wireFrame:
                pygame.draw.polygon(surface, color, vertices)
            else:
                pygame.draw.polygon(surface, color, vertices,1)
    


def annotate(viewport, fps):
    if not bounce.App.debug:
        return
    

    bounce.render_text(viewport,"World: %s " % bounce.Physics.world_rect, (12,12), 12)
    bounce.render_text(viewport,"Pixel: %s " % bounce.Physics.pixel_rect, (12,24), 12)
    bounce.render_text(viewport,"fps: %3.3f " % fps, (12,36), 12)




def init_physics():
    bounce.Physics.step = 1 / bounce.App.fps
    bounce.Physics.world_rect = bounce.FRect(0,0,0,0) # world physics size
    bounce.Physics.pixel_rect = pygame.Rect(0,0,0,0)  # world pixel size.
    bounce.Physics.world = b2World(gravity = bounce.Physics.gravity, 
                                  doSleep=True,
                                  contactListener=ContactListener(),
                                  ContactFilter = ContactFilter())
    


    bounce.Physics.do_step = do_step
    bounce.Physics.clear_surface = clear_surface
    bounce.Physics.draw_body = draw_body
    bounce.Physics.annotate = annotate

    # by default, world_size is the same as Screen size.
    update_world_size( bounce.Screen.rect.size )


def update_world_size(world_size):
    bounce.Physics.pixel_rect.size = world_size
    wx, wy = b2Vec2(bounce.Physics.pixel_rect.size) / bounce.Physics.pToM 
    bounce.Physics.world_rect = bounce.FRect(0,0,wx,wy)

    if bounce.App.debug:
        if hasattr(bounce.Physics,"surface") and bounce.Physics.surface:
            del bounce.Physics.surface
        bounce.Physics.surface = pygame.Surface( bounce.Physics.pixel_rect.size, bounce.Screen.surface_flags )
    else:
        bounce.Physics.surface = None    

def ToWorld( v ):
    "convert Pixels coords to Physical coords. Physics(0,0)=Lower Left"
    x = v[0] / bounce.Physics.pToM
    y = ((bounce.Physics.world_rect.height*bounce.Physics.pToM)-v[1]) / bounce.Physics.pToM
    #print("ToWorld w(%d,%d) -> P(%d, %d)" % (v[0],v[1],x,y))
    return(x, y)

def ToPixels( v ):
    "convert Physical coords to Pixels coords. Pixel(0,0)=Upper Left"
    x = v[0] * bounce.Physics.pToM
    y = (bounce.Physics.world_rect.height*bounce.Physics.pToM) - (v[1] * bounce.Physics.pToM)
    #print("ToPixels P(%d,%d) -> w(%d, %d)" % (v[0],v[1],x,y))
    return(x, y)

def ScaleToWorld( v):
    return b2Vec2(v) / bounce.Physics.pToM

def ScaleToPixels ( v ):
    return b2Vec2(v) * bounce.Physics.pToM

def worldPixelSize():
    "TODO: return a RECT"
    return (bounce.Physics.world_rect.width * bounce.Physics.pToM, 
            bounce.Physics.world_rect.height * bounce.Physics.pToM)

def debug():
    if not bounce.App.debug:
        return

    self.test()
    print("World Info")
    for k in bounce.Physics.__dict__.keys():
        print("%15s: %15s" % (k, self.__dict__[k]))



def test_physics():
    "convert the corners and the center from the world coords"
    
    for i in [ "topleft", "topright", "bottomleft", "bottomright", "center" ]:
        v = getattr(bounce.Physics.world_rect, i)
        r = bounce.ToPixels(v)
        s = bounce.ToWorld(r)
        print("%s: P%s -> W%s -> P%s" % (i,v,r,s))