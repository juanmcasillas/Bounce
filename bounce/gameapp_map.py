import bounce
import pygame
from Box2D import *
import pyscroll
from pytmx.util_pygame import load_pygame
from . gameapp_base import pyGameApp
from . gameapp_physics import pyGameAppPhysics
import math


class pyGameAppMap(pyGameAppPhysics):
    def __init__(self, mapfile):
        super().__init__()
        self.wmap = bounce.WorldMap(mapfile)
        self.objects = []
        
    def loadMap(self):
        self.wmap.tmx = load_pygame(self.wmap.fname)

        # here, we know the space of our world, so store it in the class
        # used after that to init the Physics engine.
        w = self.wmap.tmx.width * self.wmap.tmx.tilewidth
        h = self.wmap.tmx.height * self.wmap.tmx.tileheight
        bounce.update_world_size((w, h))

        # Make data source for the map
        self.wmap.data = pyscroll.TiledMapData(self.wmap.tmx)

        # Make the scrolling layer
        # with screen_rect_size, creates a buffer for the screen, 
        # but we need a full world buffer (to allow blitting the physics layer when needed)
        #self.wmap.layer = pyscroll.BufferedRenderer(self.wmap.data, bounce.Screen.rect.size, alpha=False, clamp_camera=True)
        self.wmap.layer = pyscroll.BufferedRenderer(self.wmap.data, bounce.Physics.pixel_rect.size, alpha=False, clamp_camera=True)
                

    def Zoom(self, value):
        "for now, I don't know how to implement that on the Physics layer"
        pass
        

    def initMap(self):
        "do nothing here"
        pass
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

    def on_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                self._running = False
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._pause = not self._pause     
                return

        pressed = pygame.key.get_pressed()
      
        if pressed[pygame.K_q]:
            self.update_keypressed_time(pygame.K_q)
            self.starship.engine.play()
    
            max_val = self.starship.body.mass * 50
            # count the time we get the key pressed, in miliseconds.
            impulse = min (max_val,  self.starship.body.mass * 100 * (self.get_keypressed_time(pygame.K_q) / 1000))
            angle =  self.starship.body.angle + math.pi/2
            y = math.sin(angle)*impulse
            x = math.cos(angle)*impulse
            self.starship.body.ApplyForce( (x,y), self.starship.body.worldCenter, wake=True )
        else:
            self.reset_keypressed_time(pygame.K_q)
            self.starship.engine.stop()
            self.starship.engine.clear()

        if pressed[pygame.K_o]:
     
            self.update_keypressed_time(pygame.K_o)
            max_val = self.starship.body.mass * 20
            impulse = min (max_val,  self.starship.body.mass * 100 * (self.get_keypressed_time(pygame.K_o) / 1000))
            self.starship.body.ApplyTorque(impulse, wake=True)
        else:
            self.reset_keypressed_time(pygame.K_o)

        if pressed[pygame.K_p]:
            self.update_keypressed_time(pygame.K_p)
            max_val = self.starship.body.mass * 20
            impulse = min (max_val,  self.starship.body.mass * 100 * (self.get_keypressed_time(pygame.K_p) / 1000))
            self.starship.body.ApplyTorque(-impulse, wake=True)
            ##self.starship.body.ApplyAngularImpulse(impulse=-impulse, wake=True)
        else:
            self.reset_keypressed_time(pygame.K_p)
  

    def init(self):
        pyGameApp.init(self)
        self.loadMap()
       
        self.add_keypressed_time(pygame.K_q)
        self.add_keypressed_time(pygame.K_o)
        self.add_keypressed_time(pygame.K_p)
        
        self.loadBodiesFromMap()
        
        self.initMap()
        #self.starship = None
        #self.sprites.add(self.starship, self.starship.engine)
    
  
    def on_render(self):

        # copy the bg to the physics layer. (the physics surface layer is the same size of the bg)
        self.wmap.layer.draw(bounce.Physics.surface,bounce.Physics.surface.get_rect())

        # draw things in surface        
        for body in self.bodies:
            bounce.Physics.draw_body(body)

        bounce.Physics.draw_body(self.starship.body, wireFrame=True)

        self.sprites.draw(bounce.Physics.surface)
        self.starship.draw(bounce.Physics.surface)
        
        # for debbuging sprite rects
        # pygame.draw.rect(self.physics.surface, (255,255,255),self.starship.rect,1)   
        #pygame.draw.rect(self.physics.surface,(255,255,255),self.starship.engine.rect,1) 
        # hack to use the plain render.
        #surfaces = list()
        
        #self.viewport.surface.fill(bounce.Colors.black_bga) # to preserve the bg
        self.viewport.surface.blit(bounce.Physics.surface, (0,0), self.viewport.rect)

        # annotate in the viewport
        bounce.Physics.annotate(self.viewport.surface, fps=self.clock.get_fps())

        # to the screen! no alpha needed to do the work
        self.screen.blit(self.viewport.surface, (0,0))
        

    def on_loop(self):
        self.sprites.update()
        
        b = pygame.mouse.get_pressed()
        pos = self.starship.rect.center
        if b[0]:
            # scale the window coordinates to all the world, so when pressing the button
            # and panning with the mouse, you can check all the window.
            x,y = pygame.mouse.get_pos()
            wx,wy = bounce.Physics.pixel_rect.size
            pos = ( x * wx / self.viewport.rect.width,
                    y * wy / self.viewport.rect.height)
      
        self.wmap.layer.center(pos)
        self.viewport.rect.center = pos

        # do some clip for intelligent camera here.

        if self.viewport.rect.top < 0:
            self.viewport.rect.top = 0
        if self.viewport.rect.bottom >  bounce.Physics.pixel_rect.height:
            self.viewport.rect.bottom = bounce.Physics.pixel_rect.height

        if self.viewport.rect.left < 0:
            self.viewport.rect.left = 0
        if self.viewport.rect.right >  bounce.Physics.pixel_rect.width:
            self.viewport.rect.right = bounce.Physics.pixel_rect.width




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
            if obj.type and obj.type.lower() == "wallline":
                print("wallline found: %s" % obj.name)
                # all points are defined from the base 
                #  <object id="30" name="object5" type="wallline" x="448" y="320">
                # <polyline points="0,0 -128,64 -256,0 -256,64 -384,64"/>
                # </object>
                orig = (0,0)
     
                # now, translate all the points to the 0,0:
                xlate = []
                for p in obj.points:
                    px,py = bounce.ToWorld(b2Vec2(p) + orig)
                    xlate.append((px,py)) 
   
                for p in xlate:
                    print(p,len(xlate))
      
                body = bounce.Physics.world.CreateStaticBody(shapes=b2ChainShape(vertices_chain=xlate)) ## the vertice order is CCW
                #body.fixtures[0].filterData.categoryBits=4
                #body.fixtures[0].filterData.maskBits=0
                #body.fixtures[0].filterData.groupIndex=0
                
            if obj.type and obj.type.lower() == "wallcircle":
                print("wallcircle found: %s" % obj.name)
                center = (0,0)
                rectsize = (0,0)
                
                # its a circle, calculate center and radious
                #b2CircleShape(pos=(1, 2), radius=0.5)
                center =  ( obj.x + (obj.width/2), obj.y + (obj.height / 2))
                radius = max(obj.width/2, obj.height/2)
                print(center, radius)
                radius, _ = bounce.ScaleToWorld((radius,0))

                body = bounce.Physics.world.CreateStaticBody(
                        position=bounce.ToWorld(center),   
                        shapes=b2CircleShape(radius=radius)
                        )

            # dinamic object test
            if obj.type and obj.type.lower() == "dynpoly":
                print("dynpoly found: %s" % obj.name)
       
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

                    body = bounce.Physics.world.CreateDynamicBody(
                            position = bounce.ToWorld(center),
                            angle = 0,
                            fixtures = b2FixtureDef(
                                shape = b2PolygonShape(box= bounce.ScaleToWorld(rectsize)),
                                density = obj.properties['density'],
                                friction = obj.properties['friction'],
                                restitution = obj.properties['restitution']
                            ))     
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
                        px,py = bounce.ScaleToWorld(b2Vec2(p) - centroid)
                        xlate.append( (px,-py)  )
                    
                    for p in obj.points:
                        print(p, centroid)
                    
                    for p in xlate:
                        print(p)
                    
    
                    body = bounce.Physics.world.CreateDynamicBody(
                            position = bounce.ToWorld(centroid),
                            angle = 0,
                            fixtures = b2FixtureDef(
                                shape = b2PolygonShape(vertices=xlate),
                                density = obj.properties['density'],
                                friction = obj.properties['friction'],
                                restitution = obj.properties['restitution']
                            )) 

                                  
            if obj.type and obj.type.lower() == "dyncircle":
                print("dyncircle found: %s" % obj.name)
                center = (0,0)
                rectsize = (0,0)
                
                # its a circle, calculate center and radious
                #b2CircleShape(pos=(1, 2), radius=0.5)
                center =  ( obj.x + (obj.width/2), obj.y + (obj.height / 2))
                radius = max(obj.width/2, obj.height/2)
                print(center, radius)
                for p in obj.properties.keys():
                    print("%s: %s" % (p, obj.properties[p]))
                radius, _ = bounce.ScaleToWorld((radius,0))

                body = bounce.Physics.world.CreateDynamicBody(
                        position=bounce.ToWorld(center),
                        angle=0,
                        fixtures = b2FixtureDef(
                            shape = b2CircleShape(radius=radius),
                            density = obj.properties['density'],
                            friction = obj.properties['friction'],
                            restitution = obj.properties['restitution']
                        ))                     
                print(body)

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

                    body = bounce.Physics.world.CreateStaticBody(position=bounce.ToWorld(center),   
                        shapes=b2PolygonShape(box=bounce.ScaleToWorld(rectsize)))
                
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
                        px,py = bounce.ScaleToWorld(b2Vec2(p) - centroid)
                        xlate.append( (px,-py)  )
                    
                    for p in obj.points:
                        print(p, centroid)
                    
                    for p in xlate:
                        print(p)

                    body = bounce.Physics.world.CreateStaticBody(position=bounce.ToWorld(centroid),   
                            shapes=b2PolygonShape(vertices=xlate)) ## the vertice order is CCW
                
            if obj.image != None and obj.name.lower() != "starship":
                "allocate the sprite, and update it when the object is updated"
                body_s = bounce.SpritePhysics(self.clock, body)
                body_s.add_frame(obj.image)
                self.sprites.add( body_s )
                print("adding sprite")
                
            self.bodies.append(body)
             

