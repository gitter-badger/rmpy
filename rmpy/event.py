class Event(object):
    """This object stores the data for each deployed event"""
    def __init__(self,cls,eventtype,**kwargs):
        self.cls = cls
        self.eventtype = eventtype
        self.__dict__.update(kwargs)
