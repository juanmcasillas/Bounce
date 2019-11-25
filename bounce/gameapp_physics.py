import bounce
import pygame
from Box2D import *
from . gameapp_base import pyGameApp


class pyGameAppPhysics(pyGameApp):
    def __init__(self):
        super().__init__()

    def on_init(self):
        super().on_init()
        self.create_world_bounds()


    def on_render(self):
        bounce.Physics.surface.fill((0,0,0))
        
        for wall in self.walls:
            self.drawBodies(wall,color=(255,100,100))

        self.viewport.surface.fill((0,0,0,0))
        self.viewport.surface.blit(bounce.Physics.surface, (0,0), self.viewport.rect)

        bounce.drawPhysicsSurface(self.screen,  self.viewport.rect)

    def on_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                self._running = False
                return

    def on_step(self):
        # update the physics engine
        bounce.Physics.do_step()
        super().on_step()

    def create_world_bounds(self):
       "create a static objects fencing all the world. (walls)"
       "deprecated"
       self.walls = []
       ww = 0.1 # meters (wall width)
       w = bounce.Physics.world_rect.width
       h = bounce.Physics.world_rect.height

       self.walls.append( bounce.Physics.world.CreateStaticBody(position=(ww,h/2),   shapes=b2PolygonShape(box=(ww,h/2))))
       self.walls.append( bounce.Physics.world.CreateStaticBody(position=(w-ww,h/2), shapes=b2PolygonShape(box=(ww,h/2))))
       self.walls.append( bounce.Physics.world.CreateStaticBody(position=(w/2,ww),   shapes=b2PolygonShape(box=(w/2,ww))))
       self.walls.append( bounce.Physics.world.CreateStaticBody(position=(w/2,h-ww), shapes=b2PolygonShape(box=(w/2,ww))))

    def zoom(self, v):
        return b2Vec2(v) * self._zoom

    def drawBodies(self, body, color=None, wireFrame=False, surface=None):
        surface = surface or bounce.Physics.surface
            
        if body.type == Box2D.b2_dynamicBody:
            color = color or (100,255,100)
        if body.type == Box2D.b2_staticBody:
            color = color or (100,100,100)

        for fixture in body.fixtures:
            shape = fixture.shape
      
            if isinstance(shape, b2ChainShape):
                vertices = [self.zoom(bounce.ToPixels(body.transform * v)) for v in shape.vertices]
                if not wireFrame:  
                    pygame.draw.lines(surface, color, False, vertices)
                else:
                    pygame.draw.lines(surface, color, False, vertices,1)

            elif isinstance(shape, b2CircleShape):
                ## todo, circle here
                if not wireFrame:
                    center = self.zoom(bounce.ToPixels(body.position))
                    radius, _ = bounce.ScaleToPixels((shape.radius,0))

                    pygame.draw.circle(surface, color, bounce.int_tuple(center), int(radius*self._zoom))
                else:
                    pygame.draw.circle(surface, color, bounce.int_tuple(center), int(radius*self._zoom), 1)

            else:
                #polygon here.
                vertices = [self.zoom(bounce.ToPixels(body.transform * v)) for v in shape.vertices]
                if not wireFrame:
                    pygame.draw.polygon(surface, color, vertices)
                else:
                    pygame.draw.polygon(surface, color, vertices,1)
    











