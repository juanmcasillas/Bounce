
import bounce
import pygame
from Box2D import *

def physics_do_step():
    bounce.Physics.world.Step(bounce.Physics.step, bounce.Physics.velocityIT, bounce.Physics.positionIT)

def init_physics():
    bounce.Physics.step = 1 / bounce.App.fps
    bounce.Physics.world_rect = bounce.FRect(0,0,0,0) # world physics size
    bounce.Physics.pixel_rect = pygame.Rect(0,0,0,0)  # world pixel size.
    bounce.Physics.world = b2World(gravity = bounce.Physics.gravity, doSleep=True)   
    bounce.Physics.do_step = physics_do_step

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


def drawPhysicsSurface(surface, rect):

    if not bounce.App.debug:
        return
    
    bounce.render_text(bounce.Physics.surface,"World: %s " % bounce.Physics.world_rect, (0,0), 12)
    bounce.render_text(bounce.Physics.surface,"Pixel: %s " % bounce.Physics.pixel_rect, (0,12), 12)
    surface.blit(bounce.Physics.surface, (0,0), rect)

def test_physics():
    "convert the corners and the center from the world coords"
    
    for i in [ "topleft", "topright", "bottomleft", "bottomright", "center" ]:
        v = getattr(bounce.Physics.world_rect, i)
        r = bounce.ToPixels(v)
        s = bounce.ToWorld(r)
        print("%s: P%s -> W%s -> P%s" % (i,v,r,s))