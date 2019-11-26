import pygame
import argparse
import types # for method replacement
import math
from  Box2D import *
import bounce
from starship import Starship

def test_pyGameApp():
    app = bounce.pyGameApp()
    app.init()
    app.on_execute()

def test_pyGameAppPhysics():
    bounce.update_world_size((2048,1536))
    app = bounce.pyGameAppPhysics()
    app.init()
    bounce.test_physics()
    app.on_execute()

def test_pyGameAppMap():
    print(bounce.MapFile)
    print(bounce.LOG)
    app = bounce.pyGameAppMap(bounce.MapFile)
    app.init()
    app.on_execute()

def test_sprite_base():
    app = bounce.pyGameApp()
    app.init()

    mysprite_single = bounce.SpriteAnim(app.clock)
    image = pygame.image.load("assets/starship.png")
    mysprite_single.add_frame( image )
    mysprite_single.init()
    mysprite_single.move((100,100))
    app.sprites.add(mysprite_single)

    mysprite_anim = bounce.SpriteAnim(app.clock)
    images = bounce.load_spritesheet("assets/engine-layer.png", (35,50))
    for i in images:
        mysprite_anim.add_frame( i )
    mysprite_anim.init()
    mysprite_anim.move((200,200))
    app.sprites.add(mysprite_anim)

    #store them so I can change later.
    app.sprite_dict["single"] = mysprite_single
    app.sprite_dict["anim"] = mysprite_anim

    # how to redefine a method in the class application with a new implementation (cool!)

    def custom_on_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                self._running = False
                return        
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.sprite_dict["anim"].isRunning():
                    self.sprite_dict["anim"].stop()
                else:
                    self.sprite_dict["anim"].play()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                self.sprite_dict["anim"].clear()    
    
    app.on_event = types.MethodType(custom_on_event, app)

    app.on_execute()


def test_sprite_physics():
    app = bounce.pyGameAppPhysics()
    app.init()

    image = pygame.image.load("assets/starship.png")
    rect = image.get_rect()
    wcenter = bounce.ScaleToWorld( ( rect.width/2, rect.height/2 ))

    body = bounce.Physics.world.CreateDynamicBody(
            position = bounce.ToWorld((100,100)),
            angle = math.radians(0),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box= wcenter),
                density = 10,
                friction = 0.5,
                restitution = 0.1)
            )  

    app.bodies.append(body)
    mysprite_single = bounce.SpritePhysics(app.clock, body)
    mysprite_single.add_frame( image )
    mysprite_single.init()
    # move done with the physics engine.
    app.sprites.add(mysprite_single)

    
    rect = pygame.Rect((0,0),(35,50))
    images = bounce.load_spritesheet("assets/engine-layer.png", rect.size)
    wcenter = bounce.ScaleToWorld( ( rect.width/2, rect.height/2 ))

    body = bounce.Physics.world.CreateDynamicBody(
            position = bounce.ToWorld((200,200)),
            angle = math.radians(0),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box= wcenter),
                density = 10,
                friction = 0.5,
                restitution = 0.1)
            )  

    app.bodies.append(body)
    mysprite_anim = bounce.SpritePhysics(app.clock, body)

    for i in images:
        mysprite_anim.add_frame( i )
    mysprite_anim.init()
    app.sprites.add(mysprite_anim)
   
    #store them so I can change later.
    app.sprite_dict["single"] = mysprite_single
    app.sprite_dict["anim"] = mysprite_anim

  
 

    # how to redefine a method in the class application with a new implementation (cool!)
    #app.on_event = types.MethodType(custom_on_event, app)
    
    def custom_on_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                self._running = False
                return        
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.sprite_dict["anim"].isRunning():
                    self.sprite_dict["anim"].stop()
                else:
                    self.sprite_dict["anim"].play()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                self.sprite_dict["anim"].clear()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:

                #single
                impulse = 200
                y = math.sin(math.radians(45))*impulse
                x = math.cos(math.radians(45))*impulse
                body = self.sprite_dict["single"].body
                body.ApplyLinearImpulse( impulse=(x,y), point=body.worldCenter, wake=True )

                #anim
                impulse = 100
                y = math.sin(math.radians(90))*impulse
                x = math.cos(math.radians(90))*impulse
                body = self.sprite_dict["anim"].body
                body.ApplyLinearImpulse( impulse=(x,y), point=body.worldCenter, wake=True )


    app.on_event = types.MethodType(custom_on_event, app)
    app.on_execute()







#
# work only on composite
#

def test_sprite_composite():
    app = bounce.pyGameAppPhysics()
    app.init()

    anim_width, anim_height = (35,50)    
    rect = pygame.Rect((0,0),(anim_width, anim_height ))   
    images = bounce.load_spritesheet("assets/engine-layer.png", rect.size)
    
    mysprite_anim = bounce.SpriteAnim(app.clock)

    for i in images:
        mysprite_anim.add_frame( i )
    mysprite_anim.init()
    # add later to starship

    image = pygame.image.load("assets/starship.png")
    rect = image.get_rect()
    wcenter = bounce.ScaleToWorld( ( rect.width/2, rect.height/2 ))

    body = bounce.Physics.world.CreateDynamicBody(
            position = bounce.ToWorld((100,100)),
            angle = math.radians(0),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box= wcenter),
                density = 10,
                friction = 0.5,
                restitution = 0.1)
            )  

    app.bodies.append(body)
    mysprite_composite = bounce.SpriteComposite(app.clock, body)
    mysprite_composite.add_frame( image )
    mysprite_composite.init()

    mysprite_composite.add_child( "engine", mysprite_anim, (0, rect.height/2 + anim_height/2 ))

    # move done with the physics engine.
    app.sprites.add(mysprite_composite)

    #store them so I can change later.
    app.sprite_dict["composite"] = mysprite_composite
    

 

    # how to redefine a method in the class application with a new implementation (cool!)
    #app.on_event = types.MethodType(custom_on_event, app)
    
    def custom_on_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                self._running = False
                return        
    
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                impulse = 200
                y = math.sin(math.radians(90))*impulse
                x = math.cos(math.radians(90))*impulse
                body = self.sprite_dict["composite"].body
                body.ApplyLinearImpulse( impulse=(x,y), point=body.worldCenter, wake=True )
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
                impulse = 200
                body = self.sprite_dict["composite"].body
                body.ApplyAngularImpulse(impulse=impulse, wake=True)                
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                impulse = 200
                body = self.sprite_dict["composite"].body
                body.ApplyAngularImpulse(impulse=-impulse, wake=True)
               
              
    app.on_event = types.MethodType(custom_on_event, app)
    app.on_execute()



def test_tmx():
    app = bounce.pyGameAppMap(bounce.MapFile)
    app.init()
    app.starship = Starship(app.clock, app.wmap)
    app.sprites.add(app.starship)

    app.on_execute()



if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count")
    parser.add_argument("configfile", help="configuration file")
    args = parser.parse_args()

    bounce.load_config(args.configfile)
    bounce.init()

    #test_pyGameApp()
    #test_pyGameAppPhysics()
    #test_pyGameAppMap()

    #test_sprite_base()
    #test_sprite_physics()
    #test_sprite_composite()
    test_tmx()

    #app = gamebase.pyGameAppPhysicsMap((800,600),"test",args.mapfile,fps=60)
    #app.on_execute()
    #print("finish")