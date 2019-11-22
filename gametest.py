import gamebase
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count")
    parser.add_argument("mapfile", help="map file")
    args = parser.parse_args()

    app = gamebase.pyGameAppPhysicsMap((800,600),"test",args.mapfile,fps=60)
    app.on_execute()
    print("finish")