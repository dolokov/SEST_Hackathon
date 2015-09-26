
import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
from tornado.options import define, options

import tornado.websocket

from tornado import gen

import settings

class ClientParameters(object):
    def __init__(self,_id):
        self.id = _id
        self.ws = []

client_connections = {}


define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MapHandler),
            (r"/map/(\w+)",MapHandler),
            (r"/mapWS", MapWebSocketHandler),
            (r'/(.*)', tornado.web.StaticFileHandler, {'path': Settings.STATIC_PATH})

        ]
        settings = {
            "template_path":Settings.TEMPLATE_PATH,
            "static_path": Settings.STATIC_PATH,
            "debug":Settings.DEBUG
        }

        tornado.web.Application.__init__(self, handlers)

class MapHandler(tornado.web.RequestHandler):
    def get(self,params=None):
        # render html page
        if not params:
            self.render("templates/map.html")
        else:
            pass

    def post(self):
        # redirect to floorplan url
        #self.render('templates/floorplan.html',url= 'http://'+Settings.DOMAIN+'/uploads/'+final_filename, domain=Settings.DOMAIN)
        pass

class MapWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.id = uuid.uuid4()
        new_connection = ClientParameters(self.id)
        new_connection.ws = self
        client_connections[new_connection.id]=new_connection

        print 'websocket openend for uuid',self.id

    def on_message(self,message):    
        print '\nserver received:', message

        # get name of floorplan and send back wall candidates
        if message.startswith('fn_floorplan#'):
            #client_connections[self.id].sendContour2JS('contours_walls', client_connections[self.id].pipelineCoordinator.getContoursWallCandidates())
            
    

    def on_close(self):
        print "websocket closed"



def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
