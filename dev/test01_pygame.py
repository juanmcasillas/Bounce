import pygame
import sys
import os
from pygame.locals import *
from Box2D import *
import math
import pyscroll
from pytmx.util_pygame import load_pygame
import sys
import numpy


class Config:
    screen_size = (1024,768)
    screen_center = (screen_size[0]/2, screen_size[1]/2)
    pixel_scale = 10 # 10 pixels equal 1 meter.
    caption = "Sample1 demo"
    rocket_file = "svgs/rocket2.svg"
    world_size = None # wait for setup

    def W2P( v ):
        "world (pixel) 2 Physics coords"
        "Upper left is 0,0, pixel resolution. Bigger than the viewport"
        x = v[0] / Config.pixel_scale
        y = (Config.world_size[1]-v[1]) / Config.pixel_scale
        #print("W2P (%d,%d) -> (%d, %d)" % (v[0],v[1],x,y))
        return(x, y)

    def P2W( v ):
        "Physics world 2 world (pixel) coords"
        "Lower left is 0,0. up Y increases, left X increases"
        x = int(v[0] * Config.pixel_scale)
        y = Config.world_size[1] - int(v[1] * Config.pixel_scale)
        #print("P2W (%d,%d) -> (%d, %d)" % (v[0],v[1],x,y))
        return(x, y)

    def W2P_S( v ):
        return v / Config.pixel_scale

    def P2W_S ( v ):
        return v * Config.pixel_scale



class Starship(pygame.sprite.Sprite):
    def __init__(self, world):
        pygame.sprite.Sprite.__init__(self)
        self.fname = "assets/starship.png"
        self.image = pygame.image.load(self.fname)
        self.orig_image = self.image.copy()
        self.rect = self.image.get_rect()
        # center the starship in the CENTER of the screen.
        self.move_from_center(Config.screen_center)

        #define the Physics body

        p_center_x = Config.W2P_S( self.rect.width/2 )
        p_center_y = Config.W2P_S( self.rect.height /2 )
        self.body = world.CreateDynamicBody(
                position = Config.W2P(self.rect.center),
                #angle =math.pi/4.2,
                angle = 0,
                fixtures = b2FixtureDef(
                    shape = b2PolygonShape(box= (p_center_x,p_center_y)),
                    density = 1,
                    friction = 5,
                    restitution = 0.1)
                )        

    def move_from_center( self, pos ):
        " move the element to the pos with center align"
        sc = b2Vec2(pos)
        sc = sc - (self.rect.width/2, self.rect.height/2)
        self.rect.center = pos
 

    def update(self):
        x, y = Config.P2W(self.body.transform.position)
        r = self.body.transform.angle
        self.image, self.rect = self.rot_center(self.orig_image, math.degrees(r))
        if x>Config.screen_size[0]-50:
            print(x)
            x = Config.screen_size[0]-50
        if y>Config.screen_size[1]-50:
            print(y)
            y = Config.screen_size[1]-50

        self.move_from_center((x,y))

    def rot_center(self,image, angle):
        """rotate an image while keeping its center"""
        rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = rot_image.get_rect(center=rect.center)
        return rot_image,rot_rect


class App:


    def __init__(self):
        self._running = True
        self.screen = None

    def initPhysics(self):
        # init physics
        self.world = b2World(gravity = (0, -9.83), doSleep=True)
        self.starship = Starship(self.world)
        self.force = False

    def loadMap(self, fname):
        self.tmx_data = load_pygame(fname)
    
        # Make data source for the map
        self.map_data = pyscroll.TiledMapData(self.tmx_data)

        # Make the scrolling layer
        self.map_layer = pyscroll.BufferedRenderer(self.map_data, Config.screen_size, alpha=False, clamp_camera=True)
    
        # here, we know the space of our world, so store it in the class
        h = self.tmx_data.height * self.tmx_data.tileheight
        w = self.tmx_data.width * self.tmx_data.tilewidth
        Config.world_size = (w, h)
        

    def initMap(self):
        # make the pygame SpriteGroup with a scrolling map
        
        #self.group.add(self.starship)
        #self.px, self.py = (self.map_layer.map_rect.width / 2, self.map_layer.map_rect.height / 2)
        #self.group.center( (self.px, self.py))
        #self.group.center( self.starship.rect.center )
        self.map_layer.center( self.starship.rect.center) # world coords or screeen coords ? :D
        self.zoom_orig = min (Config.screen_size[0]/ self.map_layer.map_rect.width, 
                            Config.screen_size[1]/ self.map_layer.map_rect.height)
        self.map_layer.zoom = 1        

    
    def on_init(self):
        pygame.init()
        pygame.font.init()
        pygame.mouse.set_visible(False)
        pygame.display.set_caption(Config.caption)
        self.clock = pygame.time.Clock()
        # now, were  normal
        self.screen = pygame.display.set_mode(Config.screen_size, pygame.HWSURFACE|pygame.DOUBLEBUF)
        self._running = True

        self.loadMap("test01.tmx")
        self.initPhysics()
        self.initMap()
        self.sprites = pygame.sprite.RenderPlain((self.starship))
        
        #create walls:
        self.walls = []

        p_width = Config.W2P_S(Config.world_size[0])
        p_height = Config.W2P_S(Config.world_size[1])
   
        print(p_width, p_height)
        self.walls.append( self.world.CreateStaticBody(position=(0.5,p_height/2),  shapes=b2PolygonShape(box=(0.5,p_height/2))))
        self.walls.append( self.world.CreateStaticBody(position=(p_width-0.5,p_height/2),  shapes=b2PolygonShape(box=(0.5,p_height/2))))
        self.walls.append( self.world.CreateStaticBody(position=(p_width/2,0.5),  shapes=b2PolygonShape(box=(p_width/2,0.5))))
        self.walls.append( self.world.CreateStaticBody(position=(p_width/2,p_height-0.5),  shapes=b2PolygonShape(box=(p_width/2,0.5))))

        


    def on_event(self, event):
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
            self._running = False
        if event.type == pygame.KEYDOWN and event.key == ord('q'):
            self.force = True
        if event.type == pygame.KEYUP and event.key == ord('q'):
            self.force = False
             
        
        if event.type == pygame.KEYDOWN and event.key == ord('o'):
            self.starship.body.ApplyAngularImpulse(impulse=500, wake=True)

        if event.type == pygame.KEYDOWN and event.key == ord('p'):
            self.starship.body.ApplyAngularImpulse(impulse=-500, wake=True)


        # if event.type == pygame.KEYDOWN and event.key == ord('+'):
        #     self.zoom += 0.1

        # if event.type == pygame.KEYDOWN and event.key == ord('-'):
        #     self.zoom += -0.1
        #     if self.zoom <= 0: self.zoom = 1

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]:
            self.py -= 5
        if pressed[pygame.K_DOWN]:            
            self.py += 5
        if pressed[pygame.K_LEFT]:            
            self.px -= 5
        if pressed[pygame.K_RIGHT]:            
            self.px += 5
        if pressed[pygame.K_PLUS]:            
            self.map_layer.zoom += 0.01
            # debug the objects

        if pressed[pygame.K_MINUS]:            
            self.map_layer.zoom -= 0.01
            if self.map_layer.zoom < self.zoom_orig:
                self.map_layer.zoom = self.zoom_orig        

    def on_loop(self):
        if self.force:
            #self.obj.ApplyForce(force=self.force, point=self.obj.worldCenter, wake=True)
            impulse = self.starship.body.mass * 1.2
            angle =  self.starship.body.angle + math.pi/2
            y = math.sin(angle)*impulse
            x = math.cos(angle)*impulse
            self.starship.body.ApplyLinearImpulse( (x,y), self.starship.body.worldCenter, wake=True )

        self.sprites.update()
        #self.map_layer.center( self.starship.rect.center )
        self.map_layer.scroll((5,0))
        self.map_layer.scroll((0,5))
    def on_render(self):
        
        
        self.map_layer.draw(self.screen, self.screen.get_rect())
        self.sprites.draw(self.screen)


        self.drawPolygons(self.starship.body, color=(255,0,0), wireFrame=True)
        for wall in self.walls:
            self.drawPolygons(wall)

        for obj in self.tmx_data.objects:
            self.drawWorldPolygons(obj,color=(100,255,100), wireFrame=True)

   
    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        self.on_init()
        # Load TMX data
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            
            self.on_loop()
            self.on_render()

            self.world.Step(1/60, 10, 10)
            self.clock.tick(60)
            pygame.display.flip()

        self.on_cleanup()


    def drawWorldPolygons(self, obj, color=(255,100,100), wireFrame=False):
        #print(obj.name)
        #print(obj.type)
        def m(a,b): return ( a[0]*b, a[1]*b )

        if obj.type.lower() == "circle":
            #obj.__dict__["radius"] = obj.width/2.0
            #obj.__dict__["x"] = obj.x + (obj.width/2.0)
            #obj.__dict__["y"] = obj.y + (obj.height/2.0)
            x, y, width, height = [ v * self.map_layer.zoom  for v in [obj.x, obj.y, obj.width, obj.height] ]
            #print(x,y,width, height)
            cx = int(x + width/2.0)
            cy = int(y + height/2.0)
            cr = int(width / 2.0)
            if not wireFrame:
                pygame.draw.circle(self.screen, color, (cx,cy), cr)
            else:
                pygame.draw.circle(self.screen, color, (cx,cy), cr,1)
            return

        if not hasattr(obj, "points") or obj.type == None:
            #obj.height
            #obj.width
            #obj.x
            #obj.y
            obj.__dict__["points"] = [ (obj.x, obj.y), (obj.x, obj.y + obj.height), 
                                       (obj.x + obj.width, obj.y + obj.height), (obj.x + obj.width, obj.y) ]


        
        pzoom = [ m(v,self.map_layer.zoom) for v in obj.points ]
        #for p in pzoom:
            #print(p)
        if not wireFrame:
            pygame.draw.polygon(self.screen, color, pzoom)
        else:
            pygame.draw.polygon(self.screen, color,  pzoom,1)  

    def drawPolygons(self, body, color=(255,100,100), wireFrame=False):
        for fixture in body.fixtures:
            shape = fixture.shape
            vertices = [Config.P2W(body.transform * v) for v in shape.vertices]
            if not wireFrame:
                pygame.draw.polygon(self.screen, color, vertices)
            else:
                pygame.draw.polygon(self.screen, color, vertices,1)




def main():
    app = App()
    app.on_execute()

if __name__ == "__main__" :
    main()    