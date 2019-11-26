#from .helpers import *
import pygame
from Box2D import *
import math
import pyscroll
from pytmx.util_pygame import load_pygame

import sys
import os
import numpy

from . settings import *
from . pygame_helpers import *
from . physics_helpers import *
from . gameapp_base import *
from . gameapp_physics import *
from . gameapp_map import *

from . maps import *
from . frect import FRect
from . starship import *

# remap some global objects.
      
def scale_tuple(v, x):
    return b2Vec2(v) * x
    
def int_tuple(v):
    return (int(v[0]), int(v[1]) )

def init_screen():
    bounce.Screen.rect = pygame.Rect((0,0),(bounce.Screen.width, bounce.Screen.height))

def init():   
    global Physics
    global Screen
    global App
    global LOG
    global MapFile
    global Colors

    Screen = settings.Screen
    Physics = settings.Physics
    App = settings.App
    LOG = settings.LOG
    MapFile = settings.MapFile
    Colors = settings.Colors

    # static, non configurable options
    # SRCALPHA slows down A LOT the game.
    #Screen.surface_flags = pygame.SRCALPHA | pygame.HWSURFACE 
    Screen.surface_flags = pygame.HWSURFACE | pygame.DOUBLEBUF
    Screen.surface_flags_alpha = pygame.SRCALPHA | pygame.HWSURFACE | pygame.DOUBLEBUF

    init_screen()
    init_physics()


