import os
import tornado.ioloop
import tornado.web
import sqlite3
from datetime import datetime

WEB_INTERFACE_PORT = 8889

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        data = [["Time", "Temperature"]]
        now = datetime.now()
        today = [now.year, now.month, now.day]
        dbconnection = sqlite3.connect('/home/pi/db/temppressure.db')
        cursor = dbconnection.cursor()
        i = 1
        for row in cursor.execute('SELECT * FROM data WHERE year = ? AND month = ? AND day = ?', today):
            data.append([])
            data[i].append("%s:%s:%s" % (str(row[4]), str(row[5]), str(row[6])))
            data[i].append(float(row[7]))
            i = i+1
        if len(data) > 1:
            self.render('index.html', graph_list = str(data))
        else:
            data.append(['No data', 0])
            self.render('index.html', graph_list = str(data))

class ApiHandler(tornado.web.RequestHandler):
    def get(self):
        data = dict()
        dbconnection = sqlite3.connect('/home/pi/db/temppressure.db')
        cursor = dbconnection.cursor()
        for row in cursor.execute('SELECT * FROM data WHERE year = 2014 AND month = 01 AND day = 02'):
            data[row[0]] = row[7]
        dbconnection.commit()
        cursor.close()
        dbconnection.close()
        self.write(data)

class WebInterface():
    def start(self):
        application = tornado.web.Application(
            handlers = [(r"/", MainHandler), (r"/api", ApiHandler)],
            template_path = os.path.join(os.path.dirname(__file__), "www"),
            autoescape=None)
        application.listen(WEB_INTERFACE_PORT)
        tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    try:
        web = WebInterface()
        web.start()
    except:
        raise
