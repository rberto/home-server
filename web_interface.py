import os
import tornado.ioloop
import tornado.web
import sqlite3
from datetime import datetime
from dbaccess import DBAccess

WEB_INTERFACE_PORT = 8889

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        now = datetime.now()
        self.render_graph(now)

    def post(self):
        s_date = self.get_argument("selectedday", None)
        s_date = str(s_date).split("-")
        l_date = [int(x) for x in s_date ]
        date = datetime(l_date[0], l_date[1], l_date[2])
        self.render_graph(date)

    def render_graph(self, date):
        db = DBAccess()
        (average, raw_data) = db.get_data_for_day(date)
        last_temp = db.get_last_temp()
        last_pressure = db.get_last_pressure()
        if average is not None:
            self.render('index.html',
                        graph_list = str(raw_data),
                        tmp_average = average,
                        current_temp = last_temp,
                        current_pressure = last_pressure)
        else:
            data.append(['No data', 0])
            self.render('index.html',
                        graph_list = str(raw_data),
                        tmp_average = 0,
                        current_temp = 0,
                        current_pressure = 0)

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
