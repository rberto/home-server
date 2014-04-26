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
        (average, temp_data, pressure_data) = db.get_data_for_day(date)
        last_temp = db.get_last_temp()
        last_pressure = db.get_last_pressure()
        if average is not None:
            self.render('index.html',
                        temp_graph_list = str(temp_data),
                        pressure_graph_list = str(pressure_data),
                        tmp_average = average,
                        current_temp = last_temp,
                        current_pressure = last_pressure)
        else:
            temp_data = [["Time", "Temperature"], ['No data', 0]]
            pressure_data = [["Time", "Pressure"], ['No data', 0]]
            self.render('index.html',
                        temp_graph_list = str(temp_data),
                        pressure_graph_list = str(pressure_data),
                        tmp_average = "No Value",
                        current_temp = "No Value",
                        current_pressure = "No Value")

class ApiHandler(tornado.web.RequestHandler):
    def get(self):
        data = dict()
        db = DBAccess()
        data["temp"]= db.get_last_temp()
        data["pressure"] = db.get_last_pressure()
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
