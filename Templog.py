from datetime import datetime
import time
from BMP085 import Bmp085
import daemon
from pidfile import PidFile

class Templog(object):
# TODO: add debug logging capabilities. Maybe create my
# own logging module in order to factorise code from
# wakeshutdown deamon.
    def __init__(self, file_path):
        """ initialise the temperature logging class"""
        # Store the path to the file where the data
        # will be stored.
        self.file_path = file_path
        # Initialize the I2C temperature and pressure sensor.
        self.bmp085 = Bmp085(0x77, 0)
        # Initialize both temperature and pressure list
        # used to store all data before averaging.
        self.temps = []
        self.pressures = []

    def log(self):
        """Function that mesures and loggs temp and pressure data."""
        # storing the date of launch of the capture.
        startdate = time.time()
        while (True):
            # read both temp and pressure from sensor.
            (temp, p) = self.bmp085.readTempPressure()
            # add read values to buffer lists.
            self.temps.append(temp)
            self.pressures.append(p)
            if time.time() - startdate > 600:
                # averaging temp and pressure every 10 mins.
                averagetemp = self.__getaverage(self.temps)
                averagepressure = self.__getaverage(self.pressures)
                # Logging these values to the log file.
                self.__logtofile([averagetemp, averagepressure])
                # TODO: add logging to BDD.
                # Reinitializing the start date and temperature and pressure values.
                startdate = time.time()
                self.temps = []
                self.pressures = []
            # Measuring every 30 seconds.
            time.sleep(30)

    def __getaverage(self, li):
        """ returns the average of values contained in the list passed in parameters"""
        return sum(li) / len(li)

    def __logtofile(self, li):
        """ Write the data passed in parameter in a file. the format is all data
        on the same line, each term separated by a coma. before the data it also
        print an str rep of the date and time and the time.time() also separated
        by coma."""
        # Open the file in amend mode: writes at the end of the file.
        with open(self.file_path, 'a') as f:
            # Gets both representation of the date and time.
            values = [datetime.now(), time.time()]
            # Add the list passed as parameter to the end of the one with the dates.
            values.extend(li)
            # Converting the list to str each values of the list being seperated
            # by comas and adding a return at the end.
            line = ",".join(["%s" % x for x in values]) + "\n"
            # Write this line to the file.
            f.write(line)

# TODO: add no deamon start option.
if __name__ == '__main__':
    try:
        # Load the deamon context, and specify a pid file that will
        # contain the pid number of the deamon.
        context = daemon.DaemonContext(
            pidfile=PidFile('/var/run/templog.pid'))
        with context:
            # initialize the data logger and launch the logging.
            tmplogger = Templog("/home/pi/logs/temp.log")
            tmplogger.log()
    except:
        raise
