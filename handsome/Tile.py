__all__ =  [ 'Pixel', 'FloatPixel', 'Interval', 'Tile' ]

import numpy as np

def pixel_type(dtype):
    return np.dtype(
        [
            ('R', np.uint8),
            ('G', np.uint8),
            ('B', np.uint8),
            ('A', np.uint8),
        ],
        align=True
    )


Pixel = pixel_type(np.uint8)
FloatPixel = pixel_type(np.float32)

class Interval(object):
    '''Interval - Arbitrary half-closed interval of the form [start, end)'''

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __call__(self, value):
        return (1. - value) * self.start + value * self.end

    def __str__(self):
        return 'Interval({self.start}, {self.end})'.format(self=self)

    def __repr__(self):
        return 'Interval({self.start}, {self.end})'.format(self=self)

    def __eq__(self, right):
        return self.start == right.start and self.end == right.end

    def contains(self, value):
        return self.start <= value < self.end

    def __intersection(self, right):
        return (
            max(self.start, right.start),
            min(self.end, right.end)
        )

    def overlaps(self, other):
        start, end = self.__intersection(other)
        return start < end

    def intersection(self, other):
        start, end = self.__intersection(other)

        if start < end: return Interval(start, end)
        else: return None


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

    out = np.zeros(list(shape) + [ 2 ], dtype=np.float32)

    for x in range(shape[1]): out[:,x,0] = xs 
    for y in range(shape[0]): out[y,:,1] = ys

    return out
