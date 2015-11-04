__all__ = [ 'MicropolygonMesh' ]

import numpy as np
from .Pixel import FloatPixel
from handsome.capi import fill_bounds_buffer, generate_numpy_begin

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
        self.__bounds = None

    @property
    def buffer(self):
        if self.__buffer is not None:
            return self.__buffer

        shape = (self.shape[0] + 1, self.shape[1] + 1)
        self.__buffer = np.zeros(shape=shape, dtype=Vertex, order='F')

        return self.__buffer

    @property
    def bounds(self):
        if self.__bounds is not None:
            return self.__bounds

        buffer = self.__buffer
        self.__bounds = np.zeros(self.shape, dtype=Position, order='F')

        fill_bounds_buffer(
            self.shape[0] + 1,
            self.shape[1] + 1,
            generate_numpy_begin(buffer),
            generate_numpy_begin(self.__bounds),
        )

        return self.__bounds
