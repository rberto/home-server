# File containing class in order to access the database containing logs of Temp, and pressure.
# Author: rbertolini
# Since: 25/04/2014
import sqlite3
from datetime import datetime

DATA_BASE_PATH = '/home/pi/db/temppressure.db'

class DBAccess():

    def __init__(self):
        self.dbconnection = None

    def __connect(self):
        self.dbconnection = sqlite3.connect(DATA_BASE_PATH)
        return self.dbconnection

    def __disconnect(self):
        self.dbconnection.commit()
        self.dbconnection.close()

    def get_last_temp(self):
        cursor = self.__connect().cursor()
        cursor.execute('SELECT temp FROM data ORDER BY key DESC LIMIT 1')
        s_temp = cursor.fetchone()
        cursor.close()
        self.__disconnect()
        return float(s_temp[0])

    def get_last_pressure(self):
        cursor = self.__connect().cursor()
        cursor.execute('SELECT pressure FROM data ORDER BY key DESC LIMIT 1')
        s_pressure = cursor.fetchone()
        cursor.close()
        self.__disconnect()
        return float(s_pressure[0])


    def get_data_for_day(self, date):
        data = [["Time", "Temperature"]]
        cursor = self.__connect().cursor()
        i = 1
        summ = 0
        for row in cursor.execute('SELECT hour, minute, temp FROM data WHERE year = ? AND month = ? AND day = ?', [date.year, date.month, date.day]):
            data.append([])
            data[i].append("%s:%s" % (str(row[0]), str(row[1])))
            data[i].append(float(row[2]))
            summ = summ + float(row[2])
            i = i + 1
        self.__disconnect()
        if len(data) > 1 :
            average = summ / (len(data)-1)
            return (average, data)
        else:
            return (None, None)
