import os 

def neodisplay(hub_home, name, data):
        try:
                f = open(hub_home + '/tmp/' + name + '.dat','w')
                f.truncate()
                f.write(data + '\n')
        except Exception as e:
                print (str(e))
        finally:
                f.close()

