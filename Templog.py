from datetime import datetime
import time
from BMP085 import Bmp085
import daemon
from pidfile import PidFile

class Templog(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.bmp085 = Bmp085(0x77, 0)
        self.temps = []
        self.pressures = []

    def log(self):
        startdate = time.time()
        while (True):
            (temp, p) = self.bmp085.readTempPressure()
            self.temps.append(temp)
            self.pressures.append(p)
            if time.time() - startdate > 600:
                # averaging temp and pressure every 10 mins.
                averagetemp = self.__getaverage(self.temps)
                averagepressure = self.__getaverage(self.pressures)
                # Logging these values to the log file.
                self.__logtofile([averagetemp, averagepressure])
                # Reinitializing the start date and temperature and pressure values.
                startdate = time.time()
                self.temps = []
                self.pressures = []
            time.sleep(30)

    def __getaverage(self, li):
        return sum(li) / len(li)

    def __logtofile(self, li):
        with open(self.file_path, 'a') as f:
            values = [datetime.now(), time.time()]
            values.extend(li)
            line = ",".join(["%s" % x for x in values]) + "\n"
            f.write(line)


try:
    context = daemon.DaemonContext(
        pidfile=PidFile('/var/run/templog.pid'))
    with context:
        tmplogger = Templog("/home/pi/logs/temp.log")
        tmplogger.log()
except:
    raise
