import time
import os
import argparse
import sqlite3
from BMP085 import Bmp085
from datetime import datetime

# Parsing command line arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--interval", type=int, help="interval between measurements in seconds.", default=30)
parser.add_argument("-p", "--period", type=int, help="Time in seconds for the program to continue measurement.", default=600)
parser.add_argument("--debug", "-d", help="Prints some useful debug information during execution.", action="store_true")
args = parser.parse_args()

# I2C address of the BMP085 sensor.
SENSOR_ADDRESS = 0x77
temps = []
pressures = []
start_time = time.time()

if args.debug:
    print "Initialize sensor on I2C address: %s" % SENSOR_ADDRESS
bmp085 = Bmp085(SENSOR_ADDRESS, 0)

while time.time() - start_time < args.period:
    # read both temp and pressure from sensor.
    (temp, p) = bmp085.readTempPressure()
    # add read values to buffer lists.
    temps.append(temp)
    pressures.append(p)
    if args.debug:
        print "Temp=%s, Pressure=%s"%(temp, p)
    # Wait for the set time between intervals.
    time.sleep(args.interval)

key = time.time()
now = datetime.now()
values = [key, now.year, now.month, now.day, now.hour, now.minute, now.second]
values.append(round(sum(temps)/len(temps), 2))
values.append(round(sum(pressures)/len(pressures), 2))
if args.debug:
    print "Storing these values in database: %s" %values
# Convert list to list of str.
values = ["%s" % x for x in values]
# Connect to database.
dbconnection = sqlite3.connect('/home/pi/db/temppressure.db')
cursor = dbconnection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS data (key int primary key, year int, month int, day int, hour int, minute int, seconds int, temp real, pressure real)")
# Insert data into database.
cursor.execute("INSERT INTO data VALUES (?,?,?,?,?,?,?,?,?)", values)
dbconnection.commit()
cursor.close()
dbconnection.close()
