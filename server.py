"""
client opens webpage
server receives: act pos

server receives: dst pos



"""


import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
from tornado.options import define, options

import tornado.websocket
import uuid
from tornado import gen


import Settings
import Interface


class ClientParameters(object):
    def __init__(self,_id):
        self.id = _id
        self.ws = []
        self.act_pos  = (0,0)
        self.dst_pos  = (0,0)
        self.bike_pos = (0,0)

client_connections = {}

db_connection = Interface.get_connection()


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
        self.render("templates/map_example.html",domain = Settings.DOMAIN,app_id = Settings.HERE_APP_ID, app_code = Settings.HERE_APP_CODE)

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
            lat,lon = message.split('#')[1].split('$')
            lat,lon = float(lat), float(lon)
            ### FAKY FAKY
            #lat,lon = ( 52.480658, 13.465260 )
            client_connections[self.id].act_pos = (lat,lon)
            print 'new act_pos', client_connections[self.id].act_pos

        if message.startswith('dst_pos#'):
            lat,lon = message.split('#')[1].split('$')
            lat,lon = float(lat), float(lon)
            client_connections[self.id].dst_pos = (lat,lon)
            print 'dst lat',lat,'lon',lon
    
            _number_of_bikes,_radius = 10, 0.5
            list_of_jobs = Interface.get_closest_bikes(db_connection, client_connections[self.id].act_pos[0],client_connections[self.id].act_pos[1],lat,lon, number_of_bikes = _number_of_bikes, radius = _radius)
            print 'list len',len(list_of_jobs)
            print 'act',client_connections[self.id].act_pos
            for _job in list_of_jobs:
                # possible _job.value, _job.position, _job.target
                client_connections[self.id].ws.write_message('bike_pos#'+str(_job.position.latitude)+'$'+str(_job.position.longitude)+'$'+str(_job.value))
                print 'bike_pos', client_connections[self.id].act_pos, 'dst_pos', client_connections[self.id].dst_pos, 'job to do',_job
                _job.print_job()
            # send bike destination to client
            

    def on_close(self):
        print "websocket closed"



def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
