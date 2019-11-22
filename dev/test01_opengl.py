import pygame
import sys
import os
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import glsvg
from Box2D import *
import math
import pyscroll
from pytmx.util_pygame import load_pygame
import sys
import numpy

class Config:
    screen_size = (1024,768)
    world_size = (80,60) # meters
    caption = "Sample1 demo"
    rocket_file = "svgs/rocket2.svg"

    def T( v ):
        # first, map the world coords to screen cords
        # then remap (lower left to upper left)
        x = v[0] * Config.screen_size[0] / Config.world_size[0]
        y = v[1] * Config.screen_size[1] / Config.world_size[1]
        return(x,Config.screen_size[1]-y)


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = Config.screen_size
        self.bitmap_tex = None

    def reset_camera(self):
        self.zoom = 1
        self.angle = 0
        self.draw_x = self.width/2
        self.draw_y = self.height/2

    def switch_file(self, dir=0):
        self.reset_camera()
        self.filename = Config.rocket_file
        print('Parsing', self.filename)
        self.svg = glsvg.SVGDoc(self.filename)
        self.svg.anchor_x, self.svg.anchor_y = self.svg.width/2, self.svg.height/2

    def on_init(self):

        pygame.init()
        pygame.font.init()
        pygame.mouse.set_visible(False)
        pygame.display.set_caption(Config.caption)
        self.clock = pygame.time.Clock()
        self.forces = False

        # now, were are openGL 
        #self._display_surf = pygame.display.set_mode(Config.screen_size, pygame.HWSURFACE|pygame.DOUBLEBUF)
        self._display_surf = pygame.display.set_mode(self.size,
                                                     pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF) #pygame.OPENGLBLIT
        self._running = True
        self.svg = None
        self.switch_file() # load the rocket 

        self.world = b2World(gravity = (0, -9.83), doSleep=True)
        #create walls:
        self.walls = []

        wx,wy = Config.world_size

        self.walls.append( self.world.CreateStaticBody(position=(0.5,wy/2),  shapes=b2PolygonShape(box=(0.5,wy/2))))
        self.walls.append( self.world.CreateStaticBody(position=(wx-0.5,wy/2),  shapes=b2PolygonShape(box=(0.5,wy/2))))
        self.walls.append( self.world.CreateStaticBody(position=(wx/2,0.5),  shapes=b2PolygonShape(box=(wx/2,0.5))))
        self.walls.append( self.world.CreateStaticBody(position=(wx/2,wy-0.5),  shapes=b2PolygonShape(box=(wx/2,0.5))))

        self.obj = self.world.CreateDynamicBody(
                position = (wx/2,wy-10),
                #angle =math.pi/4.2,
                angle = 0,
                fixtures = b2FixtureDef(
                    shape = b2PolygonShape(box= (2,8)),
                    #shape = b2PolygonShape(vertices = [ (5,10),(0,0), (10,0) ]),
                    density = 1,
                    friction = 5,
                    restitution = 0.1)
                )
    force = None
  


    def on_event(self, event):
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
            self._running = False
        if event.type == pygame.KEYDOWN and event.key == ord('q'):
            self.force = True
        if event.type == pygame.KEYUP and event.key == ord('q'):
            self.force = False
             
        
        if event.type == pygame.KEYDOWN and event.key == ord('o'):
            self.obj.ApplyAngularImpulse(impulse=500, wake=True)

        if event.type == pygame.KEYDOWN and event.key == ord('p'):
            self.obj.ApplyAngularImpulse(impulse=-500, wake=True)


        if event.type == pygame.KEYDOWN and event.key == ord('+'):
            self.zoom += 0.1

        if event.type == pygame.KEYDOWN and event.key == ord('-'):
            self.zoom += -0.1
            if self.zoom <= 0: self.zoom = 1
        
    def on_loop(self):
        if self.force:
            #self.obj.ApplyForce(force=self.force, point=self.obj.worldCenter, wake=True)
            impulse = self.obj.mass * 1.2
            angle = self.obj.angle + math.pi/2
           
            y = math.sin(angle)*impulse
            x = math.cos(angle)*impulse

            self.obj.ApplyLinearImpulse( (x,y), self.obj.worldCenter, wake=True )
    def on_render(self):
        glClearColor(0.2,0.2,0.2,1)
        glStencilMask(0xFF)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0, 0, self.width, self.height)
        gluOrtho2D(0.0, self.width, self.height, 0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        #self.svg.draw(self.draw_x, self.draw_y, scale=self.zoom, angle=self.angle)

        x, y = Config.T(self.obj.transform.position)
        r = self.obj.transform.angle
        self.svg.draw(x,y, scale=self.zoom, angle=-math.degrees(r))

        self.drawPolygons(self.obj, color=(1,0,0), wireFrame=True)

        for wall in self.walls:
            self.drawPolygons(wall)


    def on_cleanup(self):
        del self.svg
        pygame.quit()

    def on_execute(self):
        self.on_init()
        # Load TMX data
        tmx_data = load_pygame("test01.tmx")
    
        for obj in tmx_data.objects:
            print(obj.name)
            if not hasattr(obj, "points"):
                #obj.height
                #obj.width
                #obj.x
                #obj.y
                obj.__dict__["points"] = [ (obj.x, obj.y), (obj.x, obj.y + obj.height), (obj.x + obj.width, obj.y + obj.height), (obj.x + obj.width, 0) ]

            for p in obj.points:
                print(p)

        
            # Make data source for the map
            map_data = pyscroll.TiledMapData(tmx_data)

            # Make the scrolling layer
            for p in tmx_data.properties.keys():
                print("%s: %s", p, tmx_data.properties[p])

            map_layer = pyscroll.BufferedRenderer(map_data, Config.screen_size, alpha=False)

            # make the pygame SpriteGroup with a scrolling map
            group = pyscroll.PyscrollGroup(map_layer=map_layer)
            
            px, py = (map_layer.map_rect.width / 2, map_layer.map_rect.height / 2)
            group.center( (px, py))
            # Add sprites to the group
            #group.add(sprite)

            # Center the layer and sprites on a sprite

            # Draw the layer
            # If the map covers the entire screen, do not clear the screen:
            # Clearing the screen is not needed since the map will clear it when drawn
            # This map covers the screen, so no clearing!
            
            #bgimage = tmx_data.layers[1].image
            #pygame.image.save(bgimage, "exit.jpg")
            #sys.exit(0)
            zoom_orig = min (Config.screen_size[0]/ map_layer.map_rect.width, 
                             Config.screen_size[1]/ map_layer.map_rect.height)
            map_layer.zoom = zoom_orig

        mysurface = pygame.Surface(Config.screen_size)

        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            group.center((px, py))
            group.draw(mysurface)
            self.blit_image(0,0,mysurface,1,1,1)

           
            

            self.world.Step(1/60, 10, 10)
            self.clock.tick(60)
            pygame.display.flip()

        self.on_cleanup()


    

    def drawPolygons(self, body, color=(0.5,0.3,0.3), wireFrame=False):
        for fixture in body.fixtures:
            shape = fixture.shape
            vertices = [Config.T(body.transform * v) for v in shape.vertices]
            glColor3f(*color)
            if not wireFrame:
                glBegin(GL_POLYGON)
            else:
                glBegin(GL_LINE_LOOP)
            for vertice in vertices:
                glVertex2fv(vertice)
            glEnd()

            #pygame.draw.polygon(screen, color, vertices)



    def blit_image(self, x,y,img,r,g,b):
        

        # get texture data
        w,h = img.get_size()
        raw_data = img.get_buffer().raw
        data = numpy.fromstring(raw_data, numpy.uint8)

        # create texture object
        if self.bitmap_tex == None:
            self.bitmap_tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.bitmap_tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,w,h,0,GL_RGBA,GL_UNSIGNED_BYTE,img.get_buffer().raw)

        # save and set model view and projection matrix
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # enable blending
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

        # draw textured quad
        glColor3f(r,g,b)

        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1)
        glVertex2f(x, y)
        glTexCoord2f(1, 1)
        glVertex2f(x+w, y)
        glTexCoord2f(1, 0)
        glVertex2f(x+w, y+h)
        glTexCoord2f(0, 0)
        glVertex2f(x, y+h)
        glEnd()
        glDisable(GL_TEXTURE_2D)

        # restore matrices
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        # disable blending
        glDisable(GL_BLEND)
        #usage
        #pauseimg = pygame.image.load(path + "pause.png").convert_alpha()
        #blit_image(300,300,pauseimg,1,1,1)

def main():
    app = App()
    app.on_execute()

if __name__ == "__main__" :
    main()    