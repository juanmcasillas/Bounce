import bounce

import argparse

def test_pyGameApp():
    app = bounce.pyGameApp()
    app.on_execute()

def test_pyGameAppPhysics():
    
    bounce.update_world_size((2048,1536))
    app = bounce.pyGameAppPhysics()
    bounce.test_physics()
    app.on_execute()

def test_pyGameAppMap():
    print(bounce.MapFile)
    print(bounce.LOG)
    app = bounce.pyGameAppMap(bounce.MapFile)
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
    test_pyGameAppMap()

    #app = gamebase.pyGameAppPhysicsMap((800,600),"test",args.mapfile,fps=60)
    #app.on_execute()
    #print("finish")