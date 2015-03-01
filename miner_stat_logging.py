import time
import os
import argparse
import sqlite3
from datetime import datetime
import cgmclt

def list_avg(l, roun = True):
    if roun:
        return round(sum(l)/len(l), 2)
    else:
        return sum(l)/len(l)

# Parsing command line arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--interval", type=int, help="interval between measurements in seconds.", default=30)
parser.add_argument("-p", "--period", type=int, help="Time in seconds for the program to continue measurement.", default=600)
parser.add_argument("--debug", "-d", help="Prints some useful debug information during execution.", action="store_true")
args = parser.parse_args()

start_time = time.time()
cg = cgmclt.CgminerClient("192.168.1.72", 4028)
hashrate = []
temp1 = []
temp2 = []
fanspeed = []
difficulty = 0
errorrate = []

while time.time()-start_time < args.period:
    summary = cg.command("summary", "")["SUMMARY"][0]
    stats = cg.command("stats", "")["STATS"][0]
    coin = cg.command("coin", "")["COIN"][0]

    hashrate.append(float(summary["GHS 5s"]))
    errorrate.append(float(summary["Device Hardware%"]))
    temp1.append(float(stats["temp1"]))
    temp2.append(float(stats["temp2"]))
    fanspeed.append(float(stats["fan1"]))
    difficulty = float(coin["Network Difficulty"])

    if args.debug:
        print "hashrate = %s"%hashrate[len(hashrate)-1]
        print "error rate = %s"%errorrate[len(errorrate)-1]
        print "temp1 = %s, temp2 = %s"%(temp1[len(temp1)-1], temp2[len(temp2)-1])
        print "fan speed = %s"%fanspeed[len(fanspeed)-1]
    time.sleep(args.interval)

key = int(time.time())
hashrate_avg = list_avg(hashrate)
temp1_avg = list_avg(temp1)
temp2_avg = list_avg(temp2)
errorrate_avg = list_avg(errorrate, False)
fanspeed_avg = list_avg(fanspeed)

values = [key, hashrate_avg, temp1_avg, temp2_avg, fanspeed_avg, errorrate_avg]

dbconnection = sqlite3.connect('/home/pi/db/miner.db')
cursor = dbconnection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS data (key int primary key, hashrate real, temp1 real, temp2 real, fanspeed real, errorrate real)")
if args.debug:
    print "Storing %s values in database"%str(values)
cursor.execute("INSERT INTO data VALUES (?,?,?,?,?,?)", values)

cursor.execute("CREATE TABLE IF NOT EXISTS diff (key int primary key, difficulty real)")
cursor.execute("SELECT difficulty FROM diff ORDER BY key DESC LIMIT 1")
last_difficulty = cursor.fetchone()

if args.debug:
    print "Last Difficulty = %s"%last_difficulty
if (difficulty != last_difficulty):
    values = [key, difficulty]
    if args.debug:
        cursor.execute("INSERT INTO diff VALUES (?,?)", values)
        print "Storing %s values in database"%str(values)

dbconnection.commit()
cursor.close()
dbconnection.close()
