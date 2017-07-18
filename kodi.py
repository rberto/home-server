#from kodijson import xbmc
import json
#import requests
import socket
import time
import threading
#import kodijson

import select





#print(dir(kodijson))

class KodiNotifListener:

    def __init__(self):
        self.callbacks = dict()
        self.cancel = False

    def start(self):
        t = threading.Thread(target=self.__run)
        t.start()

    def stop(self):
        self.cancel = True

    def add_callback(self, kodi_method_name, callback):
        self.callbacks[kodi_method_name] = callback

    def __run(self):
        while(not self.cancel):
            s = socket.socket()            
            print("connecting...")
            try:
                s.connect(("192.168.0.102", 9090))
            except socket.error:
                time.sleep(10)
                continue
            print("connected")
            while (not self.cancel):
                try:
                    s.setblocking(0)
                    ready = select.select([s], [], [], 1)
                    if ready[0]:
                        resp = s.recv(4096)
                    else:
                        continue
                    if (len(resp) == 0):
                        break
                    jstring = repr(resp)[2:]
                    jstring = jstring[:len(jstring)-1]
                    #print(jstring)
                    js = json.loads(jstring)
                    method = js["method"]
                    if (method in self.callbacks):
                        self.callbacks[method]()
                except ValueError:
                    # ignore all json and parsing errors.
                    pass

if __name__ == '__main__':

    def a():
        print("bite")
    m = KodiNotifListener()
    m.add_callback("Player.OnPlay", a)
    m.start()
    time.sleep(30)
    m.stop()
    
