import pygame
import sys
import os
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import glsvg
from Box2D import *
import math

class Config:
    screen_size = (800,600)
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
        # screen = pygame.display.set_mode(Config.screen_size)
        self._display_surf = pygame.display.set_mode(self.size,
                                                     pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF)
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

        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()

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

def main():
    app = App()
    app.on_execute()

if __name__ == "__main__" :
    main()