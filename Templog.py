from datetime import datetime
import time
from BMP085 import Bmp085
import daemon
from pidfile import PidFile

class Templog(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.bmp085 = Bmp085(0x77, 0)

    def log(self):
        startdate = time.time()
        count = 0
        totaltemp = 0
        while (True):
            temp = self.bmp085.readTemp()
            totaltemp += temp
            count += 1
            # less than 30 min as passed since last startdate definition.
            if time.time() - startdate > 600:
                averagetemp = totaltemp / count
                with open(self.file_path, 'a') as f:
                    date = datetime.now()
                    t = time.time()
                    line = date.__str__() + "," + str(t) + "," + str(averagetemp)  + "\n"
                    print line
                    f.write(line)
                startdate = time.time()
                count = 0
                totaltemp = 0
            time.sleep(30)


try:
    context = daemon.DaemonContext(
        pidfile=PidFile('/var/run/templog.pid'))
    with context:
        tmplogger = Templog("/home/pi/logs/temp.log")
        tmplogger.log()
except:
    raise
