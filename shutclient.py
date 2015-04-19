###
# Add this scrit to crontab of root of any machine you want to be able to
# shutdown from get request.
# And add this line before cron line as cron PATH is restricted.
# Need to add shutdwon to PATH:
# PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
###

import tornado.ioloop
import tornado.web
import tornado.httpserver
import subprocess

USER = "romain"
PASSWORD = "aqw"
WEB_INTERFACE_PORT = 8886

class MainHandler(tornado.web.RequestHandler):

    def get(self):
        user = str(self.get_argument("user", None))
        password = str(self.get_argument("password", None))
        action = str(self.get_argument("action", None))
        if user == USER and password == PASSWORD:
            if action == "shutdown":
                subprocess.Popen(["shutdown -h now"], shell = True)
            else:
                raise tornado.web.HTTPError(403, "Wrong action!")
        else:
            raise tornado.web.HTTPError(403, "Wrong password and/or username.")

class WebInterface():

    def start(self):
        local_app = tornado.web.Application(
            handlers = [(r"/", MainHandler)], debug = False)

        local_server = tornado.httpserver.HTTPServer(local_app)

        local_server.listen(WEB_INTERFACE_PORT)
        tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    try:
        web = WebInterface()
        web.start()
    except:
        raise
