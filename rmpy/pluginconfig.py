import copy


class Pluginconfig(object):
    def __init__(self, **kwargs):
        self.update(**kwargs)

    def update(self, **kwargs):
        self.__dict__.update(kwargs)

    def copy(self):
        return copy.deepcopy(self)

    def defaultdict(self):
        return self.__dict__.copy()
