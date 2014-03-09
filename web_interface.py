import tornado.ioloop
import tornado.web
import daemon
import sqlite3

WEB_INTERFACE_PORT = 8889

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("GUI should go there, with some nice graphs.")

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
        application = tornado.web.Application([
                (r"/", MainHandler),
                (r"/api", ApiHandler)
                ])
        application.listen(WEB_INTERFACE_PORT)
        tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    try:
        # Load the deamon context, and specify a pid file that will
        # contain the pid number of the deamon.
        context = daemon.DaemonContext()
#        with context:
            # start the web interface.
        web = WebInterface()
        web.start()
    except:
        raise
