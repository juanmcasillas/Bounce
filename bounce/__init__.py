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

    Screen = settings.Screen
    Physics = settings.Physics
    App = settings.App
    LOG = settings.LOG
    MapFile = settings.MapFile

    # static, non configurable options
    Screen.surface_flags = pygame.SRCALPHA | pygame.HWSURFACE

    init_screen()
    init_physics()


