import os
import tornado.ioloop
import tornado.web
import tornado.httpserver
import ssl
import sqlite3
from datetime import datetime
from dbaccess import DBAccess
#from netstatus import netstatus
from actions import actions
from btcoin import btcoin

import cgmclt

WEB_INTERFACE_PORT = 8889
API_PORT = 8899
USER = "romain"
PASSWORD = "azerty"

class MainHandler(tornado.web.RequestHandler):

    def get(self):
        temp_data = [["Time", "Temp", "Ext Temp"]]
        pressure_data = [["Time", "Pressure", "Ext Pressure"]]
        with DBAccess('temppressure.db') as db:
            for data in db.temp_data_last_hours():
                temp_data.append(data)
            for data in db.pressure_data_last_hours():
                pressure_data.append(data)
            self.render('index.html',
                        temp_graph_list = str(temp_data),
                        pressure_graph_list = str(pressure_data),
                        tmp_average = "No Value",
                        current_temp = str(db.get_last_temp()),
                        current_pressure = str(db.get_last_pressure()))


class ApiHandler(tornado.web.RequestHandler):

    def build_object(self, key, title, value, avg, unit):
        obj = dict()
        obj["key"] = key
        obj["title"] = title
        obj["value"] = value
        obj["avg"] = avg
        obj["unit"] = unit
        return obj
    
    def get(self):
        print(repr(self.request))
        data = dict()
        temp24 = []
        pressure24 = []
        user = str(self.get_argument("user", None))
        password = str(self.get_argument("password", None))
        datatype = str(self.get_argument("datatype", None))
        time = int(self.get_argument("time", 24))
        if user == USER and password == PASSWORD:
            if datatype == "summary":
                objs = []
                with DBAccess('temppressure.db') as db:
                    summ1 = 0
                    summ2 = 0
                    nbofelt = 0
                    for elt in db.temp_data_last_hours(time):
                        summ1 = summ1 + elt[1]
                        summ2 = summ2 + elt[2]
                        nbofelt = nbofelt + 1
                    data["avg_temp"] = round(summ1 / nbofelt, 2)
                    data["avg_temp_ext"] = round(summ2 / nbofelt, 2)
                    objs.append(self.build_object("temp_in", 
                                                  "Inside Temp",
                                                  db.get_last_temp(),
                                                  round(summ1 / nbofelt, 2),
                                                  "C"))
                    objs.append(self.build_object("temp_out",
                                                  "Outside Temp",
                                                  db.get_last_ext_temp(),
                                                  round(summ2 / nbofelt, 2),
                                                  "C"))
                    summ1 = 0
                    summ2 = 0
                    nbofelt = 0
                    for elt in db.pressure_data_last_hours(time):
                        summ1 = summ1 + elt[1]
                        summ2 = summ2 + elt[2]
                        nbofelt = nbofelt + 1
                    objs.append(self.build_object("pressure_in",
                                                  "Inside Pressure",
                                                  round(db.get_last_pressure()/1000, 2),
                                                  round((summ1 / nbofelt)/1000, 2),
                                                  "kPa"))
                    objs.append(self.build_object("pressure_out", 
                                                  "Outside Pressure",
                                                  round(db.get_last_pressure()/1000, 2),
                                                  round((summ2 / nbofelt)/1000, 2),
                                                  "kPa"))
                with DBAccess('miner.db') as db:
                    summ1 = 0 
                    nbofelt = 0
                    for elt in db.hash_data_last_hours(time):
                        summ1 = summ1 + elt[1]
                        nbofelt = nbofelt + 1
                    objs.append(self.build_object("hash_rate", 
                                                  "Hash Rate",
                                                  db.get_last_hashrate(),
                                                  round(summ1 / nbofelt, 2),
                                                  "GH/s"))
                    summ1 = 0 
                    nbofelt = 0
                    for elt in db.error_data_last_hours(time):
                        summ1 = summ1 + elt[1]
                        nbofelt = nbofelt + 1
                    objs.append(self.build_object("error_rate", 
                                                  "Error Rate",
                                                  round(db.get_last_errorrate(), 2),
                                                  round(summ1 / nbofelt, 2),
                                                  "%"))
                    summ1 = 0 
                    summ2 = 0
                    nbofelt = 0
                    for elt in db.asic_temp_data_last_hours(time):
                        summ1 = summ1 + elt[1]
                        summ2 = summ2 + elt[2]
                        nbofelt = nbofelt + 1
                    objs.append(self.build_object("asic1_temp", 
                                                  "Asic1 Temp",
                                                  db.get_last_asic1_temp(),
                                                  round(summ1 / nbofelt, 2),
                                                  "C"))
                    objs.append(self.build_object("asic2_temp", 
                                                  "Asic2 Temp",
                                                  db.get_last_asic2_temp(),
                                                  round(summ2 / nbofelt, 2),
                                                  "C"))
                bt = btcoin("http://eclipsemc.com/api.php", "533943365f90f2311df3904bcdbc6c")
                userstat = bt.get_user_stat()
                reward = float(userstat["data"]["user"]["confirmed_rewards"])
                objs.append(self.build_object("reward",
                                              "Pending Reward",
                                              round(reward, 4),
                                              None,
                                              "BTC"))
                                              
                data["data"] = objs
            if datatype == "weather":
                with DBAccess('temppressure.db') as db:
                    data["temp"]= db.get_last_temp()
                    data["pressure"] = db.get_last_pressure()
                    data["temp_ext"] = db.get_last_ext_temp()
                    data["pressure_ext"] = db.get_last_ext_pressure()
                    for elt in db.temp_data_last_hours(time):
                        temp24.append(elt)
                    for elt in db.pressure_data_last_hours(time):
                        pressure24.append(elt)
                    data["temp24"] = temp24
                    data["pressure24"] = pressure24
            elif datatype == "miner":
                hash24 = []
                error24 = []
                asic_temp = []
                cg = cgmclt.CgminerClient("192.168.1.72", 4028)
                data["SUMMARY"] = cg.command("summary", "")["SUMMARY"]
                data["STATS"] = cg.command("stats", "")["STATS"]
                data["COIN"] = cg.command("coin", "")["COIN"]
                with DBAccess('miner.db') as db:
                    for elt in db.hash_data_last_hours(time):
                        hash24.append(elt)
                    data["hash24"] = hash24
                    for elt in db.error_data_last_hours(time):
                        error24.append(elt)
                    data["error24"] = error24
                    for elt in db.asic_temp_data_last_hours(time):
                        asic_temp.append(elt)
                    data["asic_temp"] = asic_temp
            #elif datatype == "network":
            #    ns = netstatus()
            #    netlist = []
            #    for ip, name in ns.get_connected_devices():
            #        netlist.append({"ip": ip, "name": name})
            #    data["network"] = netlist
            elif datatype == "list_actions":
                data["data"] = actions().list_actions()
            elif datatype == "send_action":
                action_name = str(self.get_argument("name", None))
                method = getattr(actions(), action_name)
                data["msg"] = method()
            elif datatype == "data":
                key = str(self.get_argument("name", None))
                array = []
                if key in ("temp_out", "temp_in", "pressure_in", "pressure_out"):
                    with DBAccess('temppressure.db') as db:
                        for elt in getattr(db, 'get_' + key + '_data')():
                            array.append(elt)
                if key in ("hash_rate", "error_rate", "asic1_temp", "asic2_temp"):
                    with DBAccess('miner.db') as db:
                        for elt in getattr(db, 'get_' + key + '_data')():
                            array.append(elt)
                data["data"] = array
                
        else:
            raise tornado.web.HTTPError(403, "Wrong password and/or username.")
        self.write(data)

class WebInterface():
    def start(self):
        local_app = tornado.web.Application(
            handlers = [(r"/", MainHandler), (r"/api", ApiHandler)],
            template_path = os.path.join(os.path.dirname(__file__), "www"),
            autoescape=None)

        api_app = tornado.web.Application(handlers = [(r"/", ApiHandler)], autoescapse=None)

        context = {"certfile": os.path.join(os.path.dirname(__file__), "keys", "server.crt"),
                   "keyfile": os.path.join(os.path.dirname(__file__), "keys", "server.key"), 
                   "ssl_version": ssl.PROTOCOL_SSLv23}
        
        api_server = tornado.httpserver.HTTPServer(api_app, ssl_options=context)
        local_server = tornado.httpserver.HTTPServer(local_app)

        api_server.listen(API_PORT)
        local_server.listen(WEB_INTERFACE_PORT)
        ##application.listen(WEB_INTERFACE_PORT)
        tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    try:
        web = WebInterface()
        web.start()
    except:
        raise
