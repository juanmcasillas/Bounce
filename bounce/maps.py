class WorldMap:
    fname = None
    tmx = None
    data = None
    layer = None

    def __init__(self, fname):
        self.fname = fname