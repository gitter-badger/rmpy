from collections import defaultdict, namedtuple
import re


class NoRequestListener(Exception):
    pass


class Eventhandler(object):

    Listener = namedtuple('Listener', ['event_regex', 'callback'])

    def __init__(self):
        self.__listener = defaultdict(set)
        self.__pre_listener = defaultdict(set)
        self._data_listener = {}

    def register_pre_listener(self, pluginname, event_regex, callback):
        """Listen on events as first plugin, can modify the event completely
        @pluginname name of the plugin 'modulename.classname.*'
        @event_regex the match expression, that the event should listen to
        @callback_succseed this function will be called, if the event_regex succseed
        @callback_failed this will be called if the event_regex failed"""

        self.__pre_listener[pluginname].add(self.Listener(event_regex, callback))

    def register_listener(self, pluginname, pluginclass, event_regex, callback):
        """This function is like register_pre_listener, except all the actions
        will call at the end and cant modify the event."""
        self.__listener[pluginname].add(self.Listener(event_regex, callback))

    def register_data_listener(self, pluginname, callback):
        self._data_listener[pluginname] = callback

    def request_data(self, pluginname, **kwargs):
        try:
            self._data_listener[pluginname](**kwargs)
        except KeyError:
            raise NoRequestListener('No plugin is reqisterd for {0}'.format(pluginname))

    def deploy_event(self, event):
        for listener in self.__pre_listener:
            if listener.event_regex.match(event.eventtype):
                for call in listener.callback:
                    try:
                        call(event)
                    except:
                        pass
        if not event:
            return
        for listener in self.__listener:
            if listener.event_regex.match(event.eventtype):
                for call in listener.callback:
                    try:
                        call(event)
                    except:
                        pass

    def unhook_plugin(self, regex_exppression):
        regex = re.compile(regex_exppression)
        for each in [self.__listener, self.__pre_listener, self._data_listener]:
            for name, _ in each.items():
                if regex.match(name):
                    del each[name]
