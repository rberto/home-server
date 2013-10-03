from datetime import datetime
import time
from BMP085 import Bmp085


class Templog(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.bmp085 = Bmp085(0x77, 0)

    def log(self):
        while (True):
            with open(self.file_path, 'a') as f:
                temp = str(self.bmp085.readTemp())
                date = datetime.now()
                line = date.__str__() + " , " + temp + "\n"
                print line
                f.write(line)
            time.sleep(30)


try:
    tmplogger = Templog("/home/pi/templog.log")
    tmplogger.log()
except:
    raise
