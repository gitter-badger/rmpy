

class Stage(object):
    #{'plugname':{'options':value}}
    PLUGINS = dict()
    def __init__(self,game_vars, transport,**kwargs):
        self.game_vars = game_vars
        self.transport = transport
        self.start(**kwargs)

    def start(self,**kwargs):
        pass

    @property
    def finished(self):
        return True
