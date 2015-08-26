from abc import ABCMeta, abstractmethod


class Stage(metaclass=ABCMeta):
    #{'plugname':{'options':value}}
    PLUGINS = dict()

    def __init__(self, game_vars, transport, **kwargs):
        self.game_vars = game_vars
        self.transport = transport
        self.start(**kwargs)

    @abstractmethod
    def start(self, **kwargs):
        pass

    @abstractmethod
    @property
    def finished(self):
        pass
