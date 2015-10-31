__all__ = [ 'MicropolygonMesh' ]

import numpy as np
from .Pixel import FloatPixel

# TODO: Flexible vertex types

Position = np.dtype([
        ('x', np.float32),
        ('y', np.float32),
        ('z', np.float32),
        ('w', np.float32),
    ],
    align=True
)

Vertex = np.dtype([
        ('position', Position),
        ('color',    FloatPixel),
    ],
    align=True
)

class MicropolygonMesh:
    def __init__(self, shape, vertex_type=Vertex):
        self.shape = shape
        self.__buffer = None

    @property
    def buffer(self):
        if self.__buffer is not None:
            return self.__buffer

        shape = (self.shape[0] + 1, self.shape[1] + 1)
        self.__buffer = np.zeros(shape=shape, dtype=Vertex, order='F')

        return self.__buffer
