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
        (hash_avg, hashrate_data, reward_data) = db.get_btcoin_day_data()
        for item in hashrate_data:
            item.append(hash_avg)
        hashrate_data.insert(0, ['Time', 'Hash Rate', 'Hash Rate Average'])
        if average is not None:
            self.render('index.html',
                        temp_graph_list = str(temp_data),
                        pressure_graph_list = str(pressure_data),
                        tmp_average = average,
                        current_temp = last_temp,
                        current_pressure = last_pressure,
                        hashrate_graph_list = str(hashrate_data))
        else:
            temp_data = [["Time", "Temperature"], ['No data', 0]]
            pressure_data = [["Time", "Pressure"], ['No data', 0]]
            hashrate_data.append(["No Value", -1, -1])
            self.render('index.html',
                        temp_graph_list = str(temp_data),
                        pressure_graph_list = str(pressure_data),
                        tmp_average = "No Value",
                        current_temp = "No Value",
                        current_pressure = "No Value",
                        hashrate_graph_list = str(hashrate_data))

class ApiHandler(tornado.web.RequestHandler):
    def get(self):
        data = dict()
        db = DBAccess()
        data["temp"]= db.get_last_temp()
        data["pressure"] = db.get_last_pressure()
        data["logger_status"] = self.get_logger_status()
        data["hashrate"] = db.get_last_hashrate()
        data["reward"] = db.get_last_reward()
        self.write(data)

    def get_logger_status(self):
        if os.path.isfile("/var/run/templog.pid"):
            return "running"
        else:
            return "stopped"

class ChartHandler(tornado.web.RequestHandler):
    def get(self):
        arg = self.get_arguments("data_to_display", None)[0]
        hrs = self.get_arguments("hours_to_display", None)[0]
        if arg in ("pressure", "temp", "hashrate", "confirmedrewards"):
            print arg
            db = DBAccess()
            data = db.get_data(arg, int(hrs))
            ldata = [[k,v] for k,v in data.items()] #Sort the list by increassing value of first element of item in list.
            ldata = sorted(ldata, key=lambda x: x[0])
            ldata.insert(0, ['Time', str(arg)])
            self.render('chart.html',
                        graph_list = str(ldata),
                        title = str(arg))
            #self.write(data)
        else:
            print arg
            self.write("error not such data.")

class WebInterface():
    def start(self):
        application = tornado.web.Application(
            handlers = [(r"/", MainHandler), (r"/api", ApiHandler), (r"/chart", ChartHandler)],
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
