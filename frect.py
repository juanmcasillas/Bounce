#!/usr/bin/env python3

import copy

"float rectangle implentation. Useful to get the data and coords"

class FRect:
    
    def __init__(self, *args):
    
        self.__dict__["x"] = 0
        self.__dict__["y"] = 0
        self.__dict__["w"] = 0
        self.__dict__["h"] = 0

        
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, Rect):
                self.__dict__["x"]= arg.x
                self.__dict__["y"]= arg.y
                self.__dict__["w"] = arg.w
                self.__dict__["h"] = arg.h    
                return
            else:
                raise TypeError('Argument must be rect style object')

        if len(args) == 4:
            if args[2] < 0 or args[3] < 0:
                print("TBD", args)
            else:
                self.__dict__["x"] = args[0]
                self.__dict__["y"] = args[1]
                self.__dict__["w"] = args[2]
                self.__dict__["h"] = args[3]
             
        elif len(args) == 2:
                self.__dict__["x"] = args[0][0]
                self.__dict__["y"] = args[0][1]
                self.__dict__["w"] = args[1][0]
                self.__dict__["h"] = args[1][1]
        else:
            raise TypeError('Argument must be rect style object')

    def __copy__(self):
        return Rect(self)

    def __repr__(self):
        return '<frect(%f, %f, %f, %f)>' % \
            (self.x, self.y, self.w, self.h)

    def __cmp__(self, *other):
        other = FRect._rect_from_object(other)

        if self.x != other.x:
            return cmp(self.x, other.x)
        if self.y != other.y:
            return cmp(self.y, other.y)
        if self.w != other.w:
            return cmp(self.w, other.w)
        if self.h != other.h:
            return cmp(self.h, other.h)
        return 0

    def __nonzero__(self):
        return self.w != 0 and self.h != 0

    def __getattr__(self, name):
        if name == 'top':
            return self.y
        elif name == 'left':
            return self.x
        elif name == 'bottom':
            return self.y + self.h
        elif name == 'right':
            return self.x + self.w
        elif name == 'topleft':
            return self.x, self.y
        elif name == 'bottomleft':
            return self.x, self.y + self.h
        elif name == 'topright':
            return self.x + self.w, self.y
        elif name == 'bottomright':
            return self.x + self.w, self.y + self.h
        elif name == 'midtop':
            return self.x + self.w / 2, self.y
        elif name == 'midleft':
            return self.x, self.y + self.h / 2
        elif name == 'midbottom':
            return self.x + self.w / 2, self.y + self.h
        elif name == 'midright':
            return self.x + self.w, self.y + self.h / 2
        elif name == 'center':
            return self.x + self.w / 2, self.y + self.h / 2
        elif name == 'centerx':
            return self.x + self.w / 2
        elif name == 'centery':
            return self.y + self.h / 2
        elif name == 'size':
            return self.w, self.h
        elif name == 'width':
            return self.w
        elif name == 'height':
            return self.h
        else:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name == 'top' or name == 'y':
            self.y = value
        elif name == 'left' or name == 'x':
            self.x = value
        elif name == 'bottom':
            self.y = value - self.h
        elif name == 'right':
            self.x = value - self.w
        elif name == 'topleft':
            self.x = value[0]
            self.y = value[1]
        elif name == 'bottomleft':
            self.x = value[0]
            self.y = value[1] - self.h
        elif name == 'topright':
            self.x = value[0] - self.w
            self.y = value[1]
        elif name == 'bottomright':
            self.x = value[0] - self.w
            self.y = value[1] - self.h
        elif name == 'midtop':
            self.x = value[0] - self.w / 2
            self.y = value[1]
        elif name == 'midleft':
            self.x = value[0]
            self.y = value[1] - self.h / 2
        elif name == 'midbottom':
            self.x = value[0] - self.w / 2
            self.y = value[1] - self.h
        elif name == 'midright':
            self.x = value[0] - self.w
            self.y = value[1] - self.h / 2
        elif name == 'center':
            self.x = value[0] - self.w / 2
            self.y = value[1] - self.h / 2
        elif name == 'centerx':
            self.x = value - self.w / 2
        elif name == 'centery':
            self.y = value - self.h / 2
        elif name == 'size':
            if value[0] < 0 or value[1] < 0:
                self._ensure_proxy()
            self.w, self.h = value
        elif name == 'width':
            if value < 0:
                self._ensure_proxy()
            self.w = value
        elif name == 'height':
            if value < 0:
                self._ensure_proxy()
            self.h = value
        else:
            raise AttributeError(name)

    def __len__(self):
        return 4

    def __getitem__(self, key):
        return (self.x, self.y, self.w, self.h)[key]

    def __setitem__(self, key, value):
        r = [self.x, self.y, self.w, self.h]
        r[key] = value
        self.x, self.y, self.w, self.h = r

    def __coerce__(self, *other):
        try:
            return self, Rect(*other)
        except TypeError:
            return None

    def move(self, *pos):
        x, y = FRect._two_ints_from_args(pos)
        return FRect(self.x + x, self.y + y, self.w, self.h)

    def move_ip(self, *pos):
        x, y = FRect._two_ints_from_args(pos)
        self.x += x
        self.y += y

    def inflate(self, x, y):
        return FRect(self.x - x / 2, self.y - y / 2, 
                    self.w + x, self.h + y)

    def inflate_ip(self, x, y):
        self.x -= x / 2
        self.y -= y / 2
        self.w += x
        self.h += y

    def clamp(self, *other):
        r = Rect(self)
        r.clamp_ip(*other)
        return r

    def clamp_ip(self, *other):
        other = Rect._rect_from_object(other)._r
        if self.w >= other.w:
            x = other.x + other.w / 2 - self.w / 2
        elif self.x < other.x:
            x = other.x
        elif self.x + self.w > other.x + other.w:
            x = other.x + other.w - self.w
        else:
            x = self.x

        if self.h >= other.h:
            y = other.y + other.h / 2 - self.h / 2
        elif self.y < other.y:
            y = other.y
        elif self.y + self.h > other.y + other.h:
            y = other.y + other.h - self.h
        else:
            y = self.y

        self.x, self.y = x, y

    def clip(self, *other):
        r = Rect(self)
        r.clip_ip(*other)
        return r

    def clip_ip(self, *other):
        other = FRect._rect_from_object(other)._r
        x = max(self.x, other.x)
        w = min(self.x + self.w, other.x + other.w) - x
        y = max(self.y, other.y)
        h = min(self.y + self.h, other.y + other.h) - y

        if w <= 0 or h <= 0:
            self.w, self.h = 0, 0
        else:
            self.x, self.y, self.w, self.h = x, y, w, h

    def union(self, *other):
        r = FRect(self)
        r.union_ip(*other)
        return r

    def union_ip(self, *other):
        other = FRect._rect_from_object(other)._r
        x = min(self.x, other.x)
        y = min(self.y, other.y)
        w = max(self.x + self.w, other.x + other.w) - x
        h = max(self.y + self.h, other.y + other.h) - y
        self.x, self.y, self.w, self.h = x, y, w, h

    def unionall(self, others):
        r = FRect(self)
        r.unionall_ip(others)
        return r

    def unionall_ip(self, others):
        l = self.x
        r = self.x + self.w
        t = self.y
        b = self.y + self.h
        for other in others:
            other = FRect._rect_from_object(other)._r
            l = min(l, other.x)
            r = max(r, other.x + other.w)
            t = min(t, other.y)
            b = max(b, other.y + other.h)
        self.x, self.y, self.w, self.h = l, t, r - l, b - t

    def fit(self, *other):
        r = FRect(self)
        r.fit_ip(*other)
        return r
    
    def fit_ip(self, *other):
        other = FRect._rect_from_object(other)._r

        xratio = self.w / float(other.w)
        yratio = self.h / float(other.h)
        maxratio = max(xratio, yratio)
        self.w = self.w / maxratio
        self.h = self.h / maxratio
        self.x = other.x + (other.w - self.w) / 2
        self.y = other.y + (other.h - self.h) / 2

    def normalize(self):
        if self.w < 0:
            self.x += self.w
            self.w = -self.w
        if self.h < 0:
            self.y += self.h
            self.h = -self.h

    def contains(self, *other):
        other = FRect._rect_from_object(other)._r
        return self.x <= other.x and \
               self.y <= other.y and \
               self.x + self.w >= other.x + other.w and \
               self.y + self.h >= other.y + other.h and \
               self.x + self.w > other.x and \
               self.y + self.h > other.y

    def _rect_from_object(obj):
        if isinstance(obj, FRect):
            return obj
        if type(obj) in (tuple, list):
            return FRect(*obj)
        else:
            return FRect(obj)

    def _two_ints_from_args(arg):
        if len(arg) == 1:
            return FRect._two_ints_from_args(arg[0])
        else:
            return arg[:2]


if __name__ == "__main__":
    a = FRect(0,0,100, 200)
    b = FRect((11.3,12.4),(50.5,100))

    print(a)
    print(b)
    print(a.move((10,10)))

    for i in ["x","y","top", "left", "bottom", "right",
                "topleft", "bottomleft", "topright", "bottomright",
                "midtop", "midleft", "midbottom", "midright",
                "center", "centerx", "centery",
                "size", "width", "height",
                "w","h"]:
        print(i, getattr(a,i))
