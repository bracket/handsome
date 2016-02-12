from .Parser import register_class
import numpy as np


@register_class
class Group(object):
    def __init__(self, data):
        self.data = data

        xform = data.get('transformation', None)

        if xform is None:
            self.xform = None
        else:
            self.xform = np.array(xform, dtype=np.float32)

        self.children = data['children']


    @classmethod
    def convert_to_object(cls, data):
        return Group(data)
