import time
import os
from BMP085 import Bmp085

# I2C address of the BMP085 sensor.
SENSOR_ADDRESS = 0x77
print "Initialize sensor on I2C address: %s" % SENSOR_ADDRESS
bmp085 = Bmp085(SENSOR_ADDRESS, 0)
start_time = time.time()
temps = []
pressures = []
default_interval = 30
default_average_time = 600
while time.time() - startdate < default_average_time:
    # read both temp and pressure from sensor.
    (temp, p) = bmp085.readTempPressure()
    # add read values to buffer lists.
    temps.append(temp)
    pressures.append(p)
    time.sleep(default_interval)
temp_avg = sum(temps)/len(temps)
pressure_avg = sum(pressures)/len(pressures)


key = time.time()
now = datetime.now()
values = [key, now.year, now.month, now.day, now.hour, now.minute, now.second]
values.append(temp_avg)
values.append(pressure_avg)
# Convert list to list of str.
values = ["%s" % x for x in values]
dbconnection = sqlite3.connect('/home/pi/db/temppressure.db')
cursor = dbconnection.cursor()
cursor.execute("INSERT INTO data VALUES (?,?,?,?,?,?,?,?,?)", values)
dbconnection.commit()
cursor.close()
dbconnection.close()
