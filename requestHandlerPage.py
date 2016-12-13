import tornado
import registerHandler as reg

class RequestHandler(tornado.web.RequestHandler):

    def get(self):
        print(repr(self.request))
        data = dict()
        temp24 = []
        pressure24 = []
        name = self.get_argument("name", None)
        ip = self.get_argument("ip", None)
        if not (name is None) and not (ip is None):
            reg.registerObject(str(name), str(ip))
        self.write(str(reg.readClientList()))
