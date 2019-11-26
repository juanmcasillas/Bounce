
import sys
import json
import logging
import os
import shutil

#configuration objects

#MapFile = None
LogFile = None
Screen = None
Physics = None
App = None
Colors = None
#LOG = None


# JSON CONFIG EXAMPLE
# {
#     "Screen": {
#         "width": 1024,
#         "height": 768,
#         "visibleMouse": False
#     },
#     "App": {
#         "debug": True,
#         "fps": 60,
#         "title": "Sample App Title",
#     },
#     "Physics": {
#         "gravity": [ 0, -9.83 ], # this becomes a vector b2Vec2()
#         "velocityIT": 10,
#         "positionIT": 10,
#         "pToM": 32.0
#     }
#     }   
#     "LogFile": "bounce.log (or - to stdout)",
#     "MapFile": "map01.tmx"
# }



## helpers

def load_from_json(keys, json, obj=None):
    """
    if obj is none, check that keys are in the json dict
    if obj is a string, then lookup all the keys in json[obj] and build a global object
    called "obj"
    """

    json = json
    if obj:
        json = json[obj]
    
    for k in keys:
        if not k.lower() in map(lambda x: x.lower(), json.keys()):
            return False, k
    if not obj:
        return True, k

    # it's ok
    globals().update({ obj: type('', (object,), {})() })

    for k in keys:
         globals()[obj].__dict__[k] = json[k]
    return True, globals()[obj]

## load config from file


def load_config(fname, init=True):
    with open(fname, 'r') as config_file:
        try:
            config_data = json.load(config_file)
        except Exception as e:
            print("Can't read config from %s: %s" % (fname, e))
            sys.exit(1)

    ## ok, get the required fields, or bail out.

    required_keys = [ "Screen", "LogFile", "MapFile", "Physics", "App" ]

    # main tree
    keyfound, k = load_from_json(required_keys, config_data)
    if not keyfound:
        print("Required configuration key %s not found. Bailing out" % k)
        sys.exit(1)

    # screen
    keyfound, k = load_from_json( ["width", "height", "visibleMouse"], config_data, "Screen")
    if not keyfound:   
        print("Required configuration key Screen.%s not found. Bailing out" % k)
        sys.exit(1)

    # physics
    keyfound, k = load_from_json( ["gravity", "velocityIT", "positionIT", "pToM"], config_data, "Physics")
    if not keyfound:   
        print("Required configuration key Gravity.%s not found. Bailing out" % k)
        sys.exit(1)

    # app
    keyfound, k = load_from_json( ["debug", "fps", "title"], config_data, "App")
    if not keyfound:   
        print("Required configuration key Gravity.%s not found. Bailing out" % k)
        sys.exit(1)   

    global LogFile
    global MapFile
    global LOG
    global Colors

    LogFile = config_data["LogFile"]
    MapFile = config_data["MapFile"]

    # Create some default internal colors
    
    Colors = type('', (object,), {})()
    Colors.Physics = type('', (object,), {})()
    Colors.Physics.surface_bg = (0,0,0,0) # alpha
    Colors.Physics.wall_bg = (255,100,100)
    Colors.Physics.dbody_bg = (100,255,100)
    Colors.Physics.sbody_bg = (100,100,100)
    Colors.viewport_bg = (20,60,20)
    Colors.black_bga = (0,0,0,0)

    # #########################################################################
    # 
    # convert some configuration files in anothers
    #
    # convert physics gravity to tuple
    #
    Physics.gravity = ( Physics.gravity[0], Physics.gravity[1])



    # 
    # json config creation done.
    # configure LOG
    #
    if LogFile.lower() != '-':
        # log to file create a new one each run
        if os.path.exists(LogFile):
            tgt = "%s.old" % LogFile
            shutil.copyfile(LogFile,tgt)
        logging.basicConfig(filename=LogFile, filemode='w+',
                format='%(asctime)s [%(levelname)s] %(message)s', 
                level=logging.DEBUG) # normal: logging.INFO
    else:
        # to standard output
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', 
                level=logging.DEBUG) # normal: logging.INFO

    # see this
    # https://flask.palletsprojects.com/en/1.0.x/logging/
    

    LOG = logging.getLogger("bounce")
    #
    # to log exceptions 
    #logging.error("Exception occurred", exc_info=True)

    LOG.info("Bounce config loaded.")
