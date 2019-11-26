import bounce
import pygame


class pyGameApp:
    def __init__(self):
        self._running = False
        self._pause = False
        self.screen = None
        self.clock = None
        self.viewport = type('', (object,), {})() 
        self.viewport.rect = None
        self.viewport.surface = None
        self._zoom=1
        self.keypressed_time = {}
        self.sprites = None

    def get_keypressed_time(self, key):
        return self.keypressed_time[key] 

    def add_keypressed_time(self, key):
        self.keypressed_time[key] = 0

    def update_keypressed_time(self, key):
        self.keypressed_time[key] += self.clock.get_time() #  * 10 # in msecs (frame) 1/1000 

    def reset_keypressed_time(self, key):
        self.keypressed_time[key] = 0

    def on_init(self):
        pygame.init()
        pygame.font.init()
        pygame.mouse.set_visible(bounce.Screen.visibleMouse)
        pygame.display.set_caption(bounce.App.title)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(bounce.Screen.rect.size, bounce.Screen.surface_flags)
        #self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        
        self.viewport.rect = pygame.Rect((0,0),bounce.Screen.rect.size)
        self.viewport.surface = pygame.Surface(self.viewport.rect.size, bounce.Screen.surface_flags) 
        
        self.sprites = pygame.sprite.Group()
        self._running = True

    def on_event(self):
         for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                self._running = False
                return
            
    def on_loop(self):
        b = pygame.mouse.get_pressed()
        pos = bounce.Screen.rect.center
        if b[0]:
            # scale the window coordinates to all the world, so when pressing the button
            # and panning with the mouse, you can check all the window.
            x,y = pygame.mouse.get_pos()
            wx,wy = bounce.Physics.pixel_rect.size
            pos = ( x * wx / self.viewport.rect.width,
                    y * wy / self.viewport.rect.height)
      
        
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


    def on_render(self):
        self.viewport.surface.fill(bounce.Colors.viewport_bg)
        self.screen.blit(self.viewport.surface,self.screen.get_rect())


    def on_cleanup(self):
        pygame.quit()

    def on_step(self):
        self.clock.tick_busy_loop(bounce.App.fps)
        #self.clock.tick(bounce.App.fps)
        #self.clock.tick(30)

    def on_execute(self):
        self.on_init()
     
        while( self._running ):

            self.on_event()
            if self._pause:
                continue

            self.on_loop()
            self.on_render()
            self.on_step()

            pygame.display.update()
       

        self.on_cleanup()
