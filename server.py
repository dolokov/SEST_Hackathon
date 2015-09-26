
import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
from tornado.options import define, options

import tornado.websocket
import uuid
from tornado import gen

import Settings

class ClientParameters(object):
    def __init__(self,_id):
        self.id = _id
        self.ws = []

client_connections = {}


define("port", default=80, help="run on the given port", type=int)


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
            self.render("templates/map_example.html",domain = Settings.DOMAIN,app_id = Settings.HERE_APP_ID, app_code = Settings.HERE_APP_CODE)
        else:
            pass

    def post(self):
        # redirect to floorplan url
        #self.render('templates/floorplan.html',url= 'http://'+Settings.DOMAIN+'/uploads/'+final_filename, domain=Settings.DOMAIN)
        pass

class MapWebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True
    
    def open(self):
        self.id = uuid.uuid4()
        new_connection = ClientParameters(self.id)
        new_connection.ws = self
        client_connections[new_connection.id]=new_connection

        print 'websocket openend for uuid',self.id

    def on_message(self,message):    
        print 'server received:', message

        # get name of floorplan and send back wall candidates
        if message.startswith('act_pos#'):
            #client_connections[self.id].sendContour2JS('contours_walls', client_connections[self.id].pipelineCoordinator.getContoursWallCandidates())
            lat,lon = message.split('#')[1].split('$')
            lat,lon = float(lat), float(lon)
            print 'user lat',lat,'lon',lon
        if message.startswith('dst_pos#'):
            #client_connections[self.id].sendContour2JS('contours_walls', client_connections[self.id].pipelineCoordinator.getContoursWallCandidates())
            lat,lon = message.split('#')[1].split('$')
            lat,lon = float(lat), float(lon)
            print 'dst lat',lat,'lon',lon
    

    def on_close(self):
        print "websocket closed"



def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
