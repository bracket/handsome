__all__ =  [ 'Tile' ]

from .Coordinate import Coordinate
from .Interval import Interval
from .Pixel import Pixel
import numpy as np


class Tile:
    def __init__(self, origin, shape, dtype=Pixel):
        self.shape = shape
        self.dtype = dtype

        self.set_origin(origin)

        self.__buffer = None
        self.__coordinate_image = None


    def set_origin(self, origin):
        self.origin     = origin
        self.horizontal = Interval(origin[0], origin[0] + self.shape[0])
        self.vertical   = Interval(origin[1], origin[1] + self.shape[1])
        self.__coordinate_image = None


    def contains_point(self, point):
        return (
            self.horizontal.contains(point[0])
            and self.vertical.contains(point[1])
        )


    def overlaps(self, other):
        return (
            self.horizontal.overlaps(other.horizontal)
            and self.vertical.overlaps(other.vertical)
        )


    def intersection_slices(self, other):
        horizontal = self.horizontal.intersection(other.horizontal)
        if horizontal is None: return None

        vertical = self.vertical.intersection(other.vertical)
        if vertical is None: return None

        return (
            self.slice_from_intervals(horizontal, vertical),
            other.slice_from_intervals(horizontal, vertical)
        )


    def slice_from_intervals(self, horizontal, vertical):
        left = self.origin[0]
        top = self.origin[1] + self.shape[1]

        return np.s_[
            horizontal.start - left : horizontal.end - left : 1,
            top - vertical.end : top - vertical.start : 1
        ]

        
    @property
    def buffer(self):
        if self.__buffer is not None:
            return self.__buffer

        self.__buffer = np.zeros(shape=self.shape, dtype=self.dtype, order='F')
        return self.__buffer


    @property
    def coordinate_image(self):
        if self.__coordinate_image is not None:
            return self.__coordinate_image

        self.__coordinate_image = make_coordinate_image(self.origin, self.shape)

        return self.__coordinate_image


    def composite_into(self, from_tile):
        pass


def make_coordinate_image(origin, shape):
    xs = np.arange(origin[0], origin[0] + shape[0], dtype=np.float32)
    ys = np.arange(origin[1] + shape[1] - 1, origin[1] - 1, -1, dtype=np.float32)

    out = np.zeros(list(shape), dtype=Coordinate, order='F')

    for x in range(shape[0]):
        out[x,:]['y'] = ys

    for y in range(shape[1]):
        out[:,y]['x'] = xs

    return out
