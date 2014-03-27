import os
import tornado.ioloop
import tornado.web
import sqlite3
from datetime import datetime

WEB_INTERFACE_PORT = 8889

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        now = datetime.now()
        today = [now.year, now.month, now.day]
        self.render_graph(today)

    def post(self):
        date = self.get_argument("selectedday", None)
        date = str(date).split("-")
        date = [int(x) for x in date ]
        self.render_graph(date)

    def render_graph(self, date):
        data = [["Time", "Temperature"]]
        dbconnection = sqlite3.connect('/home/pi/db/temppressure.db')
        cursor = dbconnection.cursor()
        i = 1
        summ = 0
        for row in cursor.execute('SELECT hour, minute, seconds, temp FROM data WHERE year = ? AND month = ? AND day = ?', date):
            data.append([])
            data[i].append("%s:%s:%s" % (str(row[0]), str(row[1]), str(row[2])))
            data[i].append(float(row[3]))
            summ = summ + float(row[3])
            i = i+1
        if len(data) > 1:
            average = summ / len(data)
            self.render('index.html', graph_list = str(data), tmp_average = average)
        else:
            data.append(['No data', 0])
            self.render('index.html', graph_list = str(data), tmp_average = 0)

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
