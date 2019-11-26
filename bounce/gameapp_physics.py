import bounce
import pygame
from Box2D import *
from . gameapp_base import pyGameApp


class pyGameAppPhysics(pyGameApp):
    def __init__(self):
        super().__init__()
        # maybe that's removed.
        self.bodies = [] 

    def init(self):
        super().init()
        # create a simple walls to get something to see.
        self.create_world_bounds() 

    def on_render(self):
        # to get a funny color in the background
        bounce.Physics.clear_surface(bounce.Colors.viewport_bg)
        
        for wall in self.walls:
            bounce.Physics.draw_body(wall)

        for body in self.bodies:
            bounce.Physics.draw_body(body)

        ##self.viewport.surface.fill(bounce.Colors.viewport_bg)
        #self.viewport.surface.blit(bounce.Physics.surface, (0,0), self.viewport.rect)
        #self.screen.blit(self.viewport.surface, (0,0))
        
        self.sprites.draw(bounce.Physics.surface)
        self.sprite_dict["composite"].draw(bounce.Physics.surface)
        
        # copying to viewport is not needed.
        ##self.viewport.surface.blit(bounce.Physics.surface, (0,0), self.viewport.rect)
        self.screen.blit(bounce.Physics.surface, (0,0), self.viewport.rect)
        bounce.Physics.annotate(self.screen, fps=self.clock.get_fps())
       
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



 











