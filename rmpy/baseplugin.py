from pluginconfig import Pluginconfig
from event import Event
import re
from abc import ABCMeta, abstractmethod

class NotImplemented(Exception):
    pass

class BasePlugin(metaclass=ABCMeta):
    # str like:
    # REQUIRES = ['modulename.classname']
    REQUIRES = []
    DEFAULT_CONFIG = Pluginconfig()

    def __init__(self, pluginmanager, eventhandler, transport, gamevars, config=None, **kwargs):
        """Args:
        @pluginmanager used to reload the plugin completly
        @eventhandler used communicate with other plugins
        @transport used to send or recv commands to the Server
        @gamevars 'global object' all important var for a game are stored here
        @confg overwrites the DEFAULT_CONFIG
        """
        self._pluginmanager = pluginmanager
        self._eventhandler = eventhandler
        self.transport = transport
        if config:
            self.config = self.DEFAULT_CONFIG.update(**config).copy()

        # name from Pluginmanager like 'modulename.classname'
        self._importname = '%s.%s' % (__name__, self.__class__.__name__)
        self.__dict__.update(kwargs)
        self.running = False

    def recv_request_data(self):
        raise NotImplemented('recv_request_data has no content yet')

    def recv_event(self, event):
        raise NotImplemented('recv_event has no content yet')

    @abstractmethod
    def start(self):
            self.running = True

    def reload(self):
        # After unhook this object will be piced by the garbage collector
        self._pluginmanager.unload(self.name)
        # code is still in stack so this will still be executed
        self._pluginmanager.load(self.name, self.DEFAULT_CONFIG.defaultdict())

    def soft_reload(self):
        self.config = self.DEFAULT_CONFIG.copy()

    def listen_on_event(self, regex_string, callback):
        self._eventhandler.register_listener(self._importname, re.compile(regex_string), callback)

    def listen_on_pre_event(self, regex_string, callback):
        self._eventhandler.register_pre_listener(self._importname, re.compile(regex_string), callback)

    def deploy_event(self, extend_eventtype=None, event=None, **kwargs):
        eventtype = self._importname if not extend_eventtype else self._importname + extend_eventtype
        if not event:
            event = Event(self, eventtype, **kwargs)
        else:
            event.eventtype = eventtype
        self._eventhandler.deploy_event(event)
