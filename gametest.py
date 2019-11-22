import gamebase




if __name__ == "__main__":

    app = gamebase.pyGameAppPhysicsMap((800,600),"test","test01.tmx",fps=60)
    app.on_execute()
    print("finish")