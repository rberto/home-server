import time
import sqlite3
from dbaccess import DBAccess

PAGE_NAME = "/register"
object_list = dict()

#def get():
#    object_id = str(self.get_argument("id", None))
#    object_ip = str(self.get_argument("ip", None))
#    self.registerObject(object_id, object_ip)
        
def registerObject(name, ip):
    object_list[name] = ip
    with DBAccess('temppressure.db') as db:
        db.registerObject(name, ip)

def getIp(id):
    global object_list
    if not object_list:
        object_list = readClientList()
    return object_list[id]

def readClientList():
    result = dict()
    dbconnection = sqlite3.connect('/home/pi/db/temppressure.db')
    cursor = dbconnection.cursor()
    for row in cursor.execute("SELECT name, ip from clients"):
        result[row[0]] = row[1]
    return result

if __name__ == '__main__':
    registerObject("test", "127.0.0.1")
    print(getIp("test"))
    registerObject("test", "127.0.0.2")
    print(getIp("test"))
        
