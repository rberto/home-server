# File containing class in order to access the database containing logs of Temp, and pressure.
# Author: rbertolini
# Since: 25/04/2014
import sqlite3
import time
from datetime import datetime

DATA_BASE_PATH = '/home/pi/db/'


class DBAccess():


# TODO: modify, insert of hashrate so convertion is done directly in Mh/s and not as a str.
    def __init__(self, dbname):
        self.path = DATA_BASE_PATH + dbname
        self.dbconnection = None
        self.__connect()
        self.cursor = None

    def __enter__(self):
        self.cursor = self.__connect().cursor()
        return self

    def __exit__(self, type, value, traceback):
        self.cursor.close()
        self.__disconnect()
        
    def __connect(self):
        self.dbconnection = sqlite3.connect(self.path)
        return self.dbconnection

    def __disconnect(self):
        self.dbconnection.commit()
        self.dbconnection.close()

    def temp_data_last_hours(self, hrs=24):
        limit = str(int(time.time() - hrs*60*60))        
        for row in self.cursor.execute('SELECT hour, minute, temp, temp_ext from data where key > ? ORDER BY key ASC', (limit,)):
            yield ["%s:%s" % (str(row[0]), str(row[1])), float(row[2]), float(row[3])]

    def pressure_data_last_hours(self, hrs=24):
        limit = str(int(time.time() - hrs*60*60))        
        for row in self.cursor.execute('SELECT hour, minute, pressure, presure_ext from data where key > ? ORDER BY key ASC', (limit,)):
            yield ["%s:%s" % (str(row[0]), str(row[1])), float(row[2]), float(row[3])]

    def hash_data_last_hours(self, hrs=24):
        limit = str(int(time.time() - hrs*60*60))        
        for row in self.cursor.execute('SELECT key, hashrate from data where key > ? ORDER BY key ASC', (limit,)):
            yield [int(row[0]), float(row[1])]


    def get_last_temp(self):
        self.cursor.execute('SELECT temp FROM data ORDER BY key DESC LIMIT 1')
        s_temp = self.cursor.fetchone()
        return float(s_temp[0])

    def get_last_ext_pressure(self):
        self.cursor.execute('SELECT presure_ext FROM data ORDER BY key DESC LIMIT 1')
        s_pressure_ext = self.cursor.fetchone()
        return float(s_pressure_ext[0])

    def get_last_ext_temp(self):
        self.cursor.execute('SELECT temp_ext FROM data ORDER BY key DESC LIMIT 1')
        s_temp_ext = self.cursor.fetchone()
        return float(s_temp_ext[0])

    def get_last_pressure(self):
        self.cursor.execute('SELECT pressure FROM data ORDER BY key DESC LIMIT 1')
        s_pressure = self.cursor.fetchone()
        return float(s_pressure[0])

    def get_last_hashrate(self):
        cursor = self.__connect().cursor()
        cursor.execute('SELECT hashrate FROM btcoin ORDER BY key DESC LIMIT 1')
        s_hashrate = self.cursor.fetchone()
        fhashrate = self.convert_hashrate_to_float(s_hashrate[0])
        cursor.close()
        self.__disconnect()
        return fhashrate

    def get_last_reward(self):
        cursor = self.__connect().cursor()
        cursor.execute('SELECT confirmedrewards FROM btcoin ORDER BY key DESC LIMIT 1')
        s_reward = cursor.fetchone()
        cursor.close()
        self.__disconnect()
        return float(s_reward[0])


    def get_data_for_day(self, date):
        temp_data = [["Time", "Temperature", "Temperature Exterieur"]]
        pressure_data = [["Time", "Pressure", "Pression Exterieur"]]
        cursor = self.__connect().cursor()
        i = 1
        summ = 0
        for row in cursor.execute('SELECT hour,minute,temp,pressure,temp_ext,presure_ext FROM data WHERE year = ? AND month = ? AND day = ?', [date.year, date.month, date.day]):
            # Adding an other empty item (time, value) to the data list.
            temp_data.append([])
            pressure_data.append([])
            # Populating the new item with date for both temp and pressure data list.
            temp_data[i].append("%s:%s" % (str(row[0]), str(row[1])))
            pressure_data[i].append("%s:%s" % (str(row[0]), str(row[1])))
            # Populating the new item with the value of the relevant info for each of
            # the temp and pressure data list.
            temp_data[i].append(float(row[2]))
            temp_data[i].append(float(row[4]))
            pressure_data[i].append(float(row[3]))
            pressure_data[i].append(float(row[5]))
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
            hashrate = self.convert_hashrate_to_float(hashrate)
            summ = summ + hashrate
            reward = float(row[2])
            hashdata.append([date, hashrate])
            rewarddata.append([date, reward])
        cursor.close()
        self.__disconnect()
        if len(hashdata) != 0:
            hashaverage = summ / len(hashdata)
            return (hashaverage, hashdata, rewarddata)
        else:
            return (-1, hashdata, rewarddata)

    def get_data(self, arg, hrs):
        d = {}
        con = self.__connect()
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        limit = str(int(time.time() - hrs*60*60))
        if arg in ("pressure", "temp"):
            for row in cursor.execute('SELECT * from data where key > ? ORDER BY key ASC', (limit,)):
                d[int(float(row["key"]))] = float(row[str(arg)])
        elif arg in ("hashrate", "confirmedrewards"):
            for row in cursor.execute('SELECT * from btcoin where key > ? ORDER BY key ASC', (limit,)):
                d[int(row[0])] = float(row[str(arg)])
        return d


    def convert_hashrate_to_float(self, hashrate):
        if "G" in hashrate.upper():
            fhashrate = float(hashrate.split(" ")[0])*1000
        elif "M" in hashrate.upper():
            fhashrate = float(hashrate.split(" ")[0])
        elif "K" in hashrate.upper():
            fhashrate = float(hashrate.split(" ")[0])/1000
        elif hashrate == " ":
            fhashrate = 0
        else:
            fhashrate = -1
        return fhashrate
