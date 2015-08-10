from eventhandler import Eventhandler
from os import path
import os
from itertools import chain

class Pluginmanager(object):
    def __init__(self, configdir, eventhandler=None, transport, gamevars):
        self._configdir = path.abspath(path.expandvars(path.expanduser((confdir))))
        assert path.lexists(self._configdir)
        os.chdir(self._configdir)
        self._plugins = {}
        self._transport = transport
        self._eventhandler = eventhandler if eventhandler else Eventhandler()
        self.gamevars = gamevars

    def load_plugin(self, name, config=None):
        modulename, classname = name.split('.')
        module = __import__('plugins.' + modulename)
        for requred_module in getattr('REQUIRES', module):
            if requred_module not in self._plugins:
                self.load_plugin(requred_module)
        self._plugins[name] = getattr(classname, module)
        self._plugins[name](self, self._eventhandler,self._transport, self.gamevars, config).start()

    def unload_plugin(self, name, with_deps=True,force_unload_deps=False):
        self._plugins[name].stop()
        self._eventhandler.unload_plugin[name]
        plugin = self._plugins[name:]
        del self._plugins[name]
        if with_deps:
            for dep_plugin in plugin.REQUIRES:
                if not dep_plugin in set(chain([plugindep.REQUIRES for plugindep in self._plugins])):
                    self.unload_plugin(dep_plugin)
        self._eventhandler.unhook_plugin(name + '.*')
