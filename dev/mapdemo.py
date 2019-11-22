import pyscroll
from pytmx.util_pygame import load_pygame
import pygame
import sys

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    pygame.mouse.set_visible(False)
    pygame.display.set_caption("test")
    clock = pygame.time.Clock()

    screen_size = (1024, 700)
    screen =  pygame.display.set_mode(screen_size, pygame.HWSURFACE | pygame.DOUBLEBUF )

    
    # Load TMX data
    tmx_data = load_pygame("sample_map.tmx")
    
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

    map_layer = pyscroll.BufferedRenderer(map_data, screen_size, alpha=False)

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
    map_layer.zoom = min (screen_size[0]/ map_layer.map_rect.width, screen_size[1]/ map_layer.map_rect.height)
    running = True
    
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]:
            py -= 5
        if pressed[pygame.K_DOWN]:            
            py += 5
        if pressed[pygame.K_LEFT]:            
            px -= 5
        if pressed[pygame.K_RIGHT]:            
            px += 5
        if pressed[pygame.K_PLUS]:            
            map_layer.zoom += 0.01
        if pressed[pygame.K_MINUS]:            
            map_layer.zoom -= 0.01
        
       
        group.center((px, py))
        group.draw(screen)
        pygame.display.flip()
    # adjust the zoom (out)


    # adjust the zoom (in)
    #map_layer.zoom = 2.0