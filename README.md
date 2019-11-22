# Bounce
A simple game to test maps, and Box2D physics

# Resources

[Github](https://github.com/pybox2d/pybox2d)
[Tutorial](https://github.com/pybox2d/pybox2d/wiki/manual)
[Advanced Info C++](https://code.google.com/archive/p/box2d/downloads)

# Notes

* pybox2d works with floating point numbers, 
* Box2D has been tuned to work well with moving objects between 0.1 and 10 meters.
* Box2D is tuned for MKS units. Keep the size of moving objects roughly between 0.1 and 10 meters.
* pybox2d uses radians for angles.
* Box2D is tuned for meters, kilograms, and seconds. So you can consider the extents to be in meters. 
* Yes with Box2D the origin is the bottom left corner of the viewport.
* And don't forget, in Box2D, the position of your body is the center of the Body. 


# Requeriments

https://github.com/fathat/glsvg
https://github.com/bitcraft/pyscroll
https://github.com/bitcraft/pytmx


// deprecated, not used https://github.com/los-cocos/cocos

The maps are created with [Tiled](https://www.mapeditor.org)
You should define all the map, using tiles (no background images, doesn't work)
Try to manage the objects right now.