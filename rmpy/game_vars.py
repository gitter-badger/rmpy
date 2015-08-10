import collections
import threading

class GameVars(collections.abc.MutableMapping):
    def __init__(self):
        self.data = dict()
        self.lock = threading.Lock()

    def __getitem__(self, key):
        with self.lock:
            return self.data[self.__keytransform__(key)][0]

    def __setitem__(self, key, value):
        if key not in self.data.keys():
                self.data[self.__keytransform__(key)] = [value,False]
        with self.lock:
            self.data[self.__keytransform__(key)][0] = value

    def __delitem__(self, key):
        with self.lock:
            del self.data[self.__keytransform__(key)]

    def __iter__(self):
        with self.lock:
            return iter(self.data)

    def __len__(self):
        with self.lock:
            return len(self.data)

    def __keytransform__(self, key):
        return key

    def globalkeys(self,*args):
        for key in args:
            self.data[self.__keytransform__(key)] = [None,True]

    def values(self):
        with self.lock:
            return [x[0] for x in self.data.values() if x[1] is True]

    def global_items_dict(self):
        with self.lock:
            return {x:y[0] for x,y in self.data.items() if y[1]is True}


    def items(self):
        with self.lock:
            return [(x,y[0]) for x,y in self.data.items() if y[1] is True]

