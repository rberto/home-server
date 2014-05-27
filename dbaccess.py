# File containing class in order to access the database containing logs of Temp, and pressure.
# Author: rbertolini
# Since: 25/04/2014
import sqlite3
import time
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
        temp_data = [["Time", "Temperature"]]
        pressure_data = [["Time", "Pressure"]]
        cursor = self.__connect().cursor()
        i = 1
        summ = 0
        for row in cursor.execute('SELECT hour, minute, temp, pressure FROM data WHERE year = ? AND month = ? AND day = ?', [date.year, date.month, date.day]):
            # Adding an other empty item (time, value) to the data list.
            temp_data.append([])
            pressure_data.append([])
            # Populating the new item with date for both temp and pressure data list.
            temp_data[i].append("%s:%s" % (str(row[0]), str(row[1])))
            pressure_data[i].append("%s:%s" % (str(row[0]), str(row[1])))
            # Populating the new item with the value of the relevant info for each of
            # the temp and pressure data list.
            temp_data[i].append(float(row[2]))
            pressure_data[i].append(float(row[3]))
            # Adding together all the temps
            summ = summ + float(row[2])
            i = i + 1
        self.__disconnect()
        if len(temp_data) > 1 :
            # Averaging the temp. (-1 id for taking count of the title at the beginning of the list.)
            average = summ / (len(temp_data)-1)
            return (average, temp_data, pressure_data)
        else:
            # If theres no data for the Day return None.
            return (None, None, None)

    def store_btcoin_data(self, hash_rate, rewards):
        cursor = self.__connect().cursor()
        values = [int(time.time()), hash_rate, rewards]
        cursor.execute('INSERT INTO btcoin VALUES (?,?,?)', values)
        cursor.close()
        self.__disconnect()
        

    def get_btcoin_day_data(self):
        """
        Returns stored hashrate in Mh/s and rewards for the last 24h.
        return: list of 3 elements tuples. (date, hash rate, reward)
        """
        cursor = self.__connect().cursor()
        limit = (str(int(time.time() - 24*60*60)),)
        hashdata = []
        rewarddata = []
        summ = 0
        for row in cursor.execute('SELECT * from btcoin where key > ? ORDER BY key ASC', limit):
            date = int(row[0])
            hashrate = str(row[1])
            if "G" in hashrate.upper():
                hashrate = float(hashrate.split(" ")[0])*1000
            elif "M" in hashrate.upper():
                hashrate = float(hashrate.split(" ")[0])
            elif "K" in hasrate.upper():
                hashrate = float(hashrate.split(" ")[0])/1000
            else:
                hashrate = 0
            summ = summ + hashrate
            reward = float(row[2])
            hashdata.append([date, hashrate])
            rewarddata.append([date, reward])
        cursor.close()
        self.__disconnect()
        hashaverage = summ / len(hashdata)
        return (hashaverage, hashdata, rewarddata)
