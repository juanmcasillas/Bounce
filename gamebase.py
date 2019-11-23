
import pygame
from Box2D import *
import math
import pyscroll
from pytmx.util_pygame import load_pygame


import sys
import os
import numpy

from frect import FRect
from starship import Starship


def render_text(surface, text, pos, size=24, color=(255,255,255), font=None):
    font = pygame.font.Font(pygame.font.match_font("consolas"), size)
    text_surface = font.render(text, False, color)
    surface.blit(text_surface, dest=(pos))

class WorldMap:
    fname = None
    tmx = None
    data = None
    layer = None

    def __init__(self, fname):
        self.fname = fname


class Config:
    screen_size = None
    caption = ""
    fps = 30
    visibleMouse = False

class Physics:
    debug = True
    gravity = (0, -9.83)
    doSleep = True
    step = 1/60
    velocityIT = 10
    positionIT = 10
    pToM = 32.0 # 32 pixels == 1 meter
    world_rect = FRect(0,0,0,0) # in PIXELS. can be greater than screen
    surface = None


    def __init__(self, config, world_size):
        self.step  = 1/config.fps
        
        wx, wy = b2Vec2(world_size) / self.pToM 
        # FRect(left, top, width, height) -> Rect
        self.world_rect = FRect(0,0,wx,wy)

        # our debug surface
        if self.debug:
            self.surface = pygame.Surface( world_size, pygame.SRCALPHA| pygame.HWSURFACE) 

    def ToWorld(self,v):
        "convert Pixels coords to Physical coords. Physics(0,0)=Lower Left"
        x = v[0] / self.pToM
        y = ((self.world_rect.height*self.pToM)-v[1]) / self.pToM
        #print("ToWorld w(%d,%d) -> P(%d, %d)" % (v[0],v[1],x,y))
        return(x, y)

    def ToPixels(self, v ):
        "convert Physical coords to Pixels coords. Pixel(0,0)=Upper Left"
        x = v[0] * self.pToM
        y = (self.world_rect.height*self.pToM) - (v[1] * self.pToM)
        #print("ToPixels P(%d,%d) -> w(%d, %d)" % (v[0],v[1],x,y))
        return(x, y)

    def ScaleToWorld(self, v):
        return b2Vec2(v) / self.pToM

    def ScaleToPixels (self, v ):
        return b2Vec2(v) * self.pToM

    def worldPixelSize(self):
        return (self.world_rect.width * self.pToM, self.world_rect.height * self.pToM)

    def debug(self):
        if not self.debug:
            return

        self.test()
        print("World Info")
        for k in self.__dict__.keys():
            print("%15s: %15s" % (k, self.__dict__[k]))

    def draw(self, surface, rect):
        if not self.debug:
            return
        
        render_text(self.surface,"World: %s " % self.world_rect, (0,0), 12)
        surface.blit(self.surface, (0,0), rect)
    
    def test(self):
        "convert the corners and the center from the world coords"
        
        for i in [ "topleft", "topright", "bottomleft", "bottomright", "center" ]:
            v = getattr(self.world_rect, i)
            r = self.ToPixels(v)
            s = self.ToWorld(r)
            print("%s: P%s -> W%s -> P%s" % (i,v,r,s))




class pyGameApp:
    def __init__(self, screen_size, caption, fps=60):
        self._running = False
        self._pause = False
        self.screen = None
        self.config = Config()
        self.config.screen_size = screen_size
        self.config.screen_witdh, self.config.screen_height = self.config.screen_size
        self.config.screen_center = (self.config.screen_witdh/2, self.config.screen_height/2)
        self.config.caption = caption
        self.config.fps = fps
        
    def on_init(self):
        pygame.init()
        pygame.font.init()
        pygame.mouse.set_visible(self.config.visibleMouse)
        pygame.display.set_caption(self.config.caption)
        self.clock = pygame.time.Clock()
        # now, were  normal
        self.screen = pygame.display.set_mode(self.config.screen_size, pygame.HWSURFACE|pygame.DOUBLEBUF)
        self._running = True

    def on_event(self):
         for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                self._running = False
                return
            
    def on_loop(self):
        pass

    def on_render(self):
        pass


    def on_cleanup(self):
        pygame.quit()

    def on_step(self):
        self.clock.tick(self.config.fps)

    def on_execute(self):
        self.on_init()
     
        while( self._running ):


            self.on_event()
            if self._pause:
                continue

            self.on_loop()
            self.on_render()
            self.on_step()

            pygame.display.flip()

        self.on_cleanup()

class pyGameAppPhysics(pyGameApp):
    def __init__(self, screen_size, caption, fps=60, world_size=None):
        super().__init__(screen_size, caption, fps)

        if world_size:
            self.physics = Physics(self.config, world_size)
        # else, deferred the initialization (mapLoad)
        self.viewport = pygame.Rect((0,0),screen_size) # used to "PAN from the world surface"
        self.viewport_surface = pygame.Surface(screen_size, pygame.SRCALPHA| pygame.HWSURFACE) 

        self.zoom = 1


    def on_init(self):
        super().on_init()
        # init physics engine
        self.world = b2World(gravity = self.physics.gravity, doSleep=self.physics.doSleep)       
        self.physics.debug()
        self.create_world_bounds()

    def on_render(self):
        self.physics.surface.fill((0,0,0))

        for wall in self.walls:
            self.drawBodies(wall,color=(255,100,100))

        self.physics.draw(self.screen,  self.viewport)

    def on_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                self._running = False
                return
        pressed = pygame.key.get_pressed()
        amount = (0,0)
        amountDelta = 5
        wp_width, wp_height = self.physics.worldPixelSize()

        if pressed[pygame.K_LEFT] and self.viewport.left - amountDelta >= 0:
            amount = (-amountDelta,0)
        
        if pressed[pygame.K_RIGHT] and self.viewport.right + amountDelta <= wp_width:
            amount = (+amountDelta,0)

        if pressed[pygame.K_UP] and self.viewport.top - amountDelta >= 0:
            amount = (0,-amountDelta)
        
        if pressed[pygame.K_DOWN] and self.viewport.bottom + amountDelta <= wp_height:
            amount = (0,+amountDelta)         
        
        if pressed[pygame.K_PLUS]:            
            self.zoom += 0.1
            # debug the objects

        if pressed[pygame.K_MINUS]:            
            self.zoom -= 0.1
            # debug the objects

        self.viewport.move_ip(amount)

    def on_step(self):
        # update the physics engine
        self.world.Step(self.physics.step, self.physics.velocityIT, self.physics.positionIT)
        super().on_step()

    def create_world_bounds(self):
       "create a static objects fencing all the world. (walls)"
       "deprecated"
       pass
    #    self.walls = []
    #    ww = 0.1 # meters (wall width)
    #    w = self.physics.world_rect.width
    #    h = self.physics.world_rect.height

    #    self.walls.append( self.world.CreateStaticBody(position=(ww,h/2),   shapes=b2PolygonShape(box=(ww,h/2))))
    #    self.walls.append( self.world.CreateStaticBody(position=(w-ww,h/2), shapes=b2PolygonShape(box=(ww,h/2))))
    #    self.walls.append( self.world.CreateStaticBody(position=(w/2,ww),   shapes=b2PolygonShape(box=(w/2,ww))))
    #    self.walls.append( self.world.CreateStaticBody(position=(w/2,h-ww), shapes=b2PolygonShape(box=(w/2,ww))))

    def drawBodies(self, body, color=None, wireFrame=False, surface=None):
        surface = surface or self.physics.surface
        
        def zoom(v):
            return b2Vec2(v) * self.zoom
        def int_tuple(v):
            return (int(v[0]), int(v[1]) )

            
        if body.type == Box2D.b2_dynamicBody:
            color = color or (100,255,100)
        if body.type == Box2D.b2_staticBody:
            color = color or (100,100,100)


        for fixture in body.fixtures:
            shape = fixture.shape
      
            if isinstance(shape, b2CircleShape):
                
                ## todo, circle here
                if not wireFrame:
                    center = zoom(self.physics.ToPixels(shape.pos))
                    radius, _ = self.physics.ScaleToPixels((shape.radius,0))

                    pygame.draw.circle(surface, color, int_tuple(center), int(radius*self.zoom))
                else:
                    pygame.draw.circle(surface, color, int_tuple(center), int(radius*self.zoom), 1)

            else:
                vertices = [zoom(self.physics.ToPixels(body.transform * v)) for v in shape.vertices]
                if not wireFrame:
                    pygame.draw.polygon(surface, color, vertices)
                else:
                    pygame.draw.polygon(surface, color, vertices,1)
    

#
# This implementation LOADS a map and scrolls fine.
# 











class pyGameAppPhysicsMap(pyGameAppPhysics):
    def __init__(self, screen_size, caption, mapfile, fps=60, world_size=None):
        super().__init__(screen_size, caption, fps)

        self.wmap = WorldMap(mapfile)

    def loadMap(self, screen_size):
        self.wmap.tmx = load_pygame(self.wmap.fname)
    
        # Make data source for the map
        self.wmap.data = pyscroll.TiledMapData(self.wmap.tmx)

        # Make the scrolling layer
        self.wmap.layer = pyscroll.BufferedRenderer(self.wmap.data, screen_size, alpha=False, clamp_camera=True)
    
        # here, we know the space of our world, so store it in the class
        # used after that to init the Physics engine.
        w = self.wmap.tmx.width * self.wmap.tmx.tilewidth
        h = self.wmap.tmx.height * self.wmap.tmx.tileheight
        self.wmap.world_size = (w, h)
        

    def Zoom(self, value):
        "for now, I don't know how to implement that on the Physics layer"
        pass
        #self.zoom += value
        #w,h = self.wmap.world_size
        #self.wmap.layer.zoom = self.zoom
        #self.physics.surface = pygame.transform.scale(self.physics.surface, ( int(w*self.zoom), int(h*self.zoom)))
        #self.wmap.world_size = (w*self.zoom, h*self.zoom)
        

    def initMap(self):
        # make the pygame SpriteGroup with a scrolling map
        #self.group.add(self.starship)
        #self.px, self.py = (self.map_layer.map_rect.width / 2, self.map_layer.map_rect.height / 2)
        #self.group.center( (self.px, self.py))
        #self.group.center( self.starship.rect.center )
        #self.map_layer.center(self.starship.rect.center) # world coords or screeen coords ? :D
        #self.zoom_orig = min (Config.screen_size[0]/ self.map_layer.map_rect.width, 
        #                    Config.screen_size[1]/ self.map_layer.map_rect.height)

        #self.wmap.group = pyscroll.PyscrollGroup(map_layer=self.wmap.layer)       

        # for use with map.
        # self.wmap.layer.center( self.starship.rect.center)
        # self.zoom = 1        
        pass

    def on_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                self._running = False
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._pause = not self._pause                
        
        pressed = pygame.key.get_pressed()
        amount = (0,0)
        amountDelta = 5
        wp_width, wp_height = self.physics.worldPixelSize()

        if pressed[pygame.K_LEFT] and self.viewport.left - amountDelta >= 0:
            amount = (-amountDelta,0)
        
        if pressed[pygame.K_RIGHT] and self.viewport.right + amountDelta <= wp_width:
            amount = (+amountDelta,0)

        if pressed[pygame.K_UP] and self.viewport.top - amountDelta >= 0:
            amount = (0,-amountDelta)
        
        if pressed[pygame.K_DOWN] and self.viewport.bottom + amountDelta <= wp_height:
            amount = (0,+amountDelta)         
        
        if pressed[pygame.K_PLUS]:            
            self.Zoom(0.01)
            # debug the objects

        if pressed[pygame.K_MINUS]:            
            self.Zoom(-0.01)
            # debug the objects

        if pressed[pygame.K_q]:
            impulse = self.starship.body.mass * 1.2
            angle =  self.starship.body.angle + math.pi/2
            y = math.sin(angle)*impulse
            x = math.cos(angle)*impulse
            self.starship.body.ApplyLinearImpulse( (x,y), self.starship.body.worldCenter, wake=True )
        
        if pressed[pygame.K_o]:
            self.starship.body.ApplyAngularImpulse(impulse=1, wake=True)

        if pressed[pygame.K_p]:
            self.starship.body.ApplyAngularImpulse(impulse=-1, wake=True)

  
  

        self.wmap.layer.scroll(amount)
        self.viewport.move_ip(amount)
 

    def on_init(self):
        pyGameApp.on_init(self)
        self.loadMap(self.config.screen_size)
        self.physics = Physics(self.config, self.wmap.world_size)
        self.world = b2World(gravity = self.physics.gravity, doSleep=self.physics.doSleep)       
        self.physics.debug()

        self.loadBodiesFromMap()
        #self.create_world_bounds()
        
        
        self.starship = Starship(self,init=False) # delay init...
        self.starship.loadFromMap()
        self.initMap()
        self.sprites = pygame.sprite.RenderPlain((self.starship))

    def on_render(self):
        
        self.physics.surface.fill((0,0,0,0)) # alpha blending, boy!
        for body in self.bodies:
            self.drawBodies(body)

        self.drawBodies(self.starship.body, wireFrame=True)

        self.sprites.draw(self.physics.surface)

        # hack to use the plain render.
        surfaces = list()

        self.viewport_surface.fill((0,0,0,0))
        self.viewport_surface.blit(self.physics.surface, (0,0), self.viewport)
        surfaces.append( (self.viewport_surface, self.viewport_surface.get_rect(), 5)) # 0 works fine over the bg, behind the planets
        self.wmap.layer.draw(self.screen, self.screen.get_rect(), surfaces)

        #by my sidl
        #self.wmap.layer.draw(self.screen, self.screen.get_rect())
        #self.physics.draw(self.screen,  self.viewport)  
        
    def on_loop(self):
        self.sprites.update()
        # dont zoom, for now
        
        b = pygame.mouse.get_pressed()
        
        # TODO, fix the visualizer.
        pos = self.starship.rect.center
        if b[0]:
            i,j = (0,0)
            x,y = pygame.mouse.get_pos()
            pos = ( i+x, j+y)
       
        self.wmap.layer.center(pos)
        self.viewport.center = pos

        # do some clip for intelligent camera here.
        if self.viewport.top < 0:
            self.viewport.top = 0
        if self.viewport.bottom >  self.physics.worldPixelSize()[1]:
            self.viewport.bottom = self.physics.worldPixelSize()[1]

        if self.viewport.left < 0:
            self.viewport.left = 0
        if self.viewport.right >  self.physics.worldPixelSize()[0]:
            self.viewport.right = self.physics.worldPixelSize()[0]

    def loadBodiesFromMap(self):
        self.bodies = [] 
        try:
            group = self.wmap.tmx.get_layer_by_name("objects")
        except ValueError as e:
            print("Can't find objects layer in the map. Ignoring them")
            return

        group = self.wmap.tmx.get_layer_by_name("objects")
        for obj in group:
            #
            # process the defined elements for objects.
            #
            if obj.type and obj.type.lower() == "wallcircle":
                print("wallcircle found: %s" % obj.name)
                center = (0,0)
                rectsize = (0,0)
                
                # its a circle, calculate center and radious
                #b2CircleShape(pos=(1, 2), radius=0.5)
                center =  ( obj.x + (obj.width/2), obj.y + (obj.height / 2))
                radius = max(obj.width/2, obj.height/2)
                print(center, radius)
                radius, _ = self.physics.ScaleToWorld((radius,0))

                body = self.world.CreateStaticBody(
                        #position=self.physics.ToWorld(center),   
                        shapes=b2CircleShape(pos=self.physics.ToWorld(center), radius=radius)
                        )

            if obj.type and obj.type.lower() == "test":
                print("test found: %s" % obj.name)
                center = (0,0)
                rectsize = (0,0)
                if not hasattr(obj,"points"):
                    # its a rectangle, easy
                    # x, y, height, width
                    ## self.world.CreateStaticBody(position=(ww,h/2),   shapes=b2PolygonShape(box=(ww,h/2))))
                    center =  ( obj.x + (obj.width/2), obj.y + (obj.height / 2))
                    rectsize = (obj.width/2, obj.height/2)
                    print(obj.x, obj.y, obj.width, obj.height)
                    print(center, rectsize)

                    body = self.world.CreateDynamicBody(
                            position = self.physics.ToWorld(center),
                            angle = 0,
                            fixtures = b2FixtureDef(
                                shape = b2PolygonShape(box= self.physics.ScaleToWorld(rectsize)),
                                density = obj.properties['density'],
                                friction = obj.properties['friction'],
                                restitution = obj.properties['restitution']
                            ))            
                
            if obj.type and obj.type.lower() == "wall":
                print("wall found: %s" % obj.name)
                center = (0,0)
                rectsize = (0,0)
                if not hasattr(obj,"points"):
                    # its a rectangle, easy
                    # x, y, height, width
                    ## self.world.CreateStaticBody(position=(ww,h/2),   shapes=b2PolygonShape(box=(ww,h/2))))
                    center =  ( obj.x + (obj.width/2), obj.y + (obj.height / 2))
                    rectsize = (obj.width/2, obj.height/2)
                    print(obj.x, obj.y, obj.width, obj.height)
                    print(center, rectsize)

                    body = self.world.CreateStaticBody(position=self.physics.ToWorld(center),   
                        shapes=b2PolygonShape(box=self.physics.ScaleToWorld(rectsize)))
                
                else:
                    # vertice chain so calculate the centroid.
                    # create a static body here
                    # first, get the points and calculate the center of the polygon.
                    # calculate the centroid.
                    x = [p[0] for p in obj.points]
                    y = [p[1] for p in obj.points]
                    centroid = (sum(x) / len(obj.points), sum(y) / len(obj.points))
                    
                    # now, translate all the points to the 0,0:
                    xlate = []
                    centroid = b2Vec2(centroid)
                    for p in obj.points:
                        # centroid is measure from (0.0) was is upper left,
                        # in the world coords, start in bottom left, so just
                        # swap the points y coord (flipping around axis 0)
                        px,py = self.physics.ScaleToWorld(b2Vec2(p) - centroid)
                        xlate.append( (px,-py)  )
                    
                    for p in obj.points:
                        print(p, centroid)
                    
                    for p in xlate:
                        print(p)

                    body = self.world.CreateStaticBody(position=self.physics.ToWorld(centroid),   
                            shapes=b2PolygonShape(vertices=xlate)) ## the vertice order is CCW
                

            self.bodies.append(body)
             




    
