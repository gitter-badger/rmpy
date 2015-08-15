import socketserver
import threading
import stagemachine as stage
import event
import os
import os.path
import transport
__BACKUPPATH = '/'

class GameManager(object):
    def __init__(self, configdir, startport):
        self._used_ports = set([startport-1])
        self._games = dict()
        path = os.path.abspath(os.path.expandvars(os.path.expanduser(configdir)))
        assert os.path.exists(path), 'Invalid patInvalid pathh'
    def add_game(self, game_id, config):
        while True:
            port = min(self._used_ports)
            if port+1 not in self._used_ports:
                self._used_ports.add(port + 1)
                self._games[game_id] = self._startgame(port + 1)
                break
    def remove_game(self, game_id):
        self._games[game_id][0].shutdown()
        self._used_ports.remove(game_id)
        del self._games[game_id]

    def game_vars(self, game_id):
        self._games[game_id][1].game_vars

    def _generate_listener(self, stage):
        class Listener(socketserver.DatagramRequestHandler):
            def handle(self):
                stage.tick(event.Event(eventtype = 'server.incomming', data = self.request[0]))
            def server_close(self):
                stage.close()
        return Listener

    def _startgame(self,port):
        transport = transport.Transport(self.game_vars['server'])
        st = stage.stagemachine(self.config, transport)
        listener = self._generate_listener(st)
        server = socketserver.socketserver.UDPServer(("",port), listener)
        threading.Thread(target = server.serve_forever)
        return server,stage

