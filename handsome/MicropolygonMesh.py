__all__ = [ 'MicropolygonMesh' ]

import numpy as np

# TODO: Flexible vertex types

Vertex = np.dtype([
        ('x', np.float32),
        ('y', np.float32),
        ('z', np.float32),
        ('w', np.float32),
        ('R', np.float32),
        ('G', np.float32),
        ('B', np.float32),
        ('A', np.float32),
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
        self.__buffer = np.zeros(shape=shape, dtype=Vertex)

        return self.__buffer
