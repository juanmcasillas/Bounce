import pygame
from Box2D import *
import math
import  bounce




class Starship(bounce.SpriteComposite):
    def __init__(self, clock, wmap):
        bounce.SpriteComposite.__init__(self, clock, None) # load after
        self.engine = bounce.SpriteAnim(clock)
        self.loadFromMap(wmap)
        self.engine.init()

        self.add_child( "engine", self.engine, (0, self.rect.height/2 + self.engine.rect.height/2 ))
        self.init()

    def loadFromMap(self,wmap):
        try:
            group = wmap.tmx.get_layer_by_name("objects")
        except ValueError as e:
            print("Can't find objects layer in the map. Ignoring them")
            return

        # load animations

        for gid, props in wmap.tmx.tile_properties.items():
            if 'parent' in props.keys() and props['parent'].lower() == "starship":
                for animation_frame in props['frames']:
                    image = wmap.tmx.get_tile_image_by_gid(gid)
                    self.engine.add_frame(image, animation_frame.duration)
                    print("adding animation frame %d" % gid)

        group = wmap.tmx.get_layer_by_name("objects")
        starship =wmap.tmx.get_object_by_name("starship")
        if starship == None:
            print("Can't find starship layer in the map. Fatal. Bailing out")
            sys.exit(0)

        # load startship info from here.
        self.add_frame( starship.image )
        rect = starship.image.get_rect()

        #define the Physics body    
        wcenter = bounce.ScaleToWorld( ( rect.width/2, rect.height/2 ))

        self.body = bounce.Physics.world.CreateDynamicBody(
                position = bounce.ToWorld(rect.center),
                angle = math.radians(-starship.rotation),
                fixtures = b2FixtureDef(
                    shape = b2PolygonShape(box= wcenter),
                    density = starship.properties['density'],
                    friction = starship.properties['friction'],
                    restitution = starship.properties['restitution'])
                )       
        