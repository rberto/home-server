import tornado.ioloop
import tornado.web
import tornado.httpserver

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
                from subprocess import call
                call(["shutdown", "-h", "now"])
            else:
                raise tornado.web.HTTPError(403, "Wrong action!")
        else:
            raise tornado.web.HTTPError(403, "Wrong password and/or username.")

class WebInterface():
    def start(self):
        local_app = tornado.web.Application(
            handlers = [(r"/", MainHandler)])

        local_server = tornado.httpserver.HTTPServer(local_app)

        local_server.listen(WEB_INTERFACE_PORT)
        tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    try:
        web = WebInterface()
        web.start()
    except:
        raise
