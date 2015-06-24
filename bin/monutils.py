import os 

def neodisplay(name, data):
        try:
                f = open('/opt/monpanel.com/hub/' + '/tmp/' + name + '.dat','w')
                f.truncate()
                f.write(data + '\n')
        except Exception as e:
                print (str(e))
        finally:
                f.close()

