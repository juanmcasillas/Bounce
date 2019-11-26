import pygame
from Box2D import *
import math
import  bounce


class SpriteAnim(pygame.sprite.Sprite):
    def __init__(self,clock):
        self.clock = clock
        pygame.sprite.Sprite.__init__(self)   
        # frames have (image, ms_duration)
        self.frames = []
        self.index = 0
        self.timestamp = 0
        self.index = 0
        self._state = "play"
        self.image = None
        self.rect = None
        self.pos = (0,0)
        
    def isRunning(self):
        return self._state == "play"

    def init(self, stopped=False):
        if len(self.frames) == 0:
            raise ValueError("Sprite has no frames. Bailing out")
        
        self.rect = self.frames[0][0].get_rect()
        self.empty = pygame.Surface((0,0),  bounce.Screen.surface_flags_alpha)
        self.empty.fill(bounce.Colors.black)
        self.image = self.frames[0][0]

        if stopped:
            self.stop()  # animation stopped
            self.clear() # image empty

    def play(self):
        self._state = "play"
    
    def stop(self):
        self._state = "stop"

    def move(self,pos):
        self.pos = pos

    def clear(self):
        self._state = "clear"
        self.image = self.empty
        #self.rect = self.empty.get_rect()
        #self.rect.move_ip(self.pos[0],self.pos[1])
        self.index = 0 # reset cycle animation
        self.timestamp = 0

    def add_frame(self, image, duration=100):
        self.frames.append( (image, duration) )
        self.rect = image.get_rect()

    def update(self, update_pos=True):
        
        if self._state != "play": 
            return
        
        if len(self.frames) == 0:
            raise ValueError("Sprite has no frames. Bailing out")
        
        if len(self.frames) == 1:
            self.index = 0

        time_delta = self.clock.get_time()
  
        frame, duration = self.frames[self.index]

        if (self.timestamp + time_delta)  > duration:
            # move to other frame.
            self.timestamp = 0
            self.index += 1
            if self.index > len(self.frames)-1:
                self.index = 0
        else:
            self.timestamp += time_delta    

        self.image = frame
        if update_pos:
            self.rect = frame.get_rect()
            self.rect.move_ip(self.pos[0],self.pos[1])
