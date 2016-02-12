import numpy as np
from .Parser import register_class

#TODO: The Scene module should ultimately not rely on handsome
from handsome.util import parse_color

@register_class
class MicropolygonMesh(object):
    def __init__(self, data):
        self.data = data

        input = np.array(
            data['vertices'],
            dtype=np.float32,
        )

        self.points = self.reshape_input(input, data.get('color'))


    def reshape_input(self, input, color=None):
        if len(input.shape) != 3:
            raise RuntimeError('input must have shape of length 3')

        dimension = input.shape[2]

        if dimension > 8:
            raise RuntimeError('input dimension too high')

        if dimension == 8:
            return input

        shape = list(input.shape)
        shape[2] = 8

        out = np.zeros(shape=shape, dtype=np.float32)
        out[:,:,:dimension] = input

        if dimension < 3:
            out[:,:,2] = 1

        if dimension < 4:
            out[:,:,3] = 1

        if color is None:
            color = np.array([0, 0, 0, 0], dtype=np.float32).reshape([1, 1, 4])
        elif isinstance(color, str):
            color = [ c / 255. for c in parse_color(color)]
            color = np.array(color, dtype=np.float32).reshape([1, 1, 4])
        elif isinstance(color, (tuple, list)):
            color = [ c / 255. if isinstance(c, int) else c for c in color ]
            color = np.array(color, dtype=np.float32).reshape([1, 1, 4])
        
        out[:,:,4:] = color

        return out


    @classmethod
    def convert_to_object(cls, data):
        return MicropolygonMesh(data)
