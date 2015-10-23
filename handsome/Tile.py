__all__ =  [ 'Tile' ]

from .Coordinate import Coordinate
from .Exceptions import HandsomeException
from .Interval import Interval
from .Pixel import Pixel, array_view, pixel_view
import math
import numpy as np


class Tile:
    def __init__(self, origin, shape, sample_rate = 1, dtype=Pixel):
        self.shape = shape
        self.sample_rate = sample_rate
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

        shape = (self.shape[0] * self.sample_rate, self.shape[1] * self.sample_rate)
        self.__buffer = np.zeros(shape=shape, dtype=self.dtype, order='F')
        return self.__buffer


    @property
    def coordinate_image(self):
        if self.__coordinate_image is not None:
            return self.__coordinate_image

        self.__coordinate_image = make_coordinate_image(self.origin, self.shape, self.sample_rate)

        return self.__coordinate_image


    def downsample(self, sample_rate):
        downrate = int(math.ceil(self.sample_rate / float(sample_rate)))

        buffer = array_view(self.buffer)

        kernel = np.full(
            shape = (downrate, downrate, buffer.shape[-1]),
            fill_value = (1. / downrate)**2,
            dtype=buffer.dtype
        )

        return self.block_filter(kernel)


    def block_filter(self, kernel):
        buffer = array_view(self.buffer)

        new_shape = [
            int(math.ceil(float(o)/float(k)))
            for o, k in zip(buffer.shape, kernel.shape)
        ]

        new_shape[-1] = buffer.shape[-1]
        new_shape = tuple(new_shape)

        out = np.empty(
            shape=new_shape,
            dtype=buffer.dtype
        )

        for i, (x_start, x_end) in enumerate(strides(0, buffer.shape[0], kernel.shape[0])):
            for j, (y_start, y_end) in enumerate(strides(0, buffer.shape[1], kernel.shape[1])):
                pixel = buffer[x_start:x_end,y_start:y_end,:] * kernel
                pixel = pixel.sum(axis=(0,1), keepdims=True)
                out[i,j] = pixel

        return pixel_view(out)


    def composite_from(self, from_tile):
        if self.sample_rate != from_tile.sample_rate:
            raise HandsomeException(
                'sample rates do not match',
                {
                    'self.sample_rate'      : sample_rate,
                    'from_tile.sample_rate' : from_tile.sample_rate
                }
            )


def make_coordinate_image(origin, shape, sample_rate):
    xs = np.linspace(
        origin[0], float(origin[0] + shape[0]), shape[0] * sample_rate,
        endpoint = False, dtype = np.float32
    )

    ys = np.linspace(
        origin[1], origin[1] + shape[1], shape[1] * sample_rate,
        endpoint = False, dtype = np.float32
    )[::-1]

    shape = (len(xs), len(ys))
    out = np.zeros(shape, dtype=Coordinate, order='F')

    for x in range(shape[0]):
        out[x,:]['y'] = ys

    for y in range(shape[1]):
        out[:,y]['x'] = xs

    return out

def strides(start, stop, step=1):
    begin, end = None, None

    for i in range(start, stop, step):
        begin,end = end,i
        if begin is None:
            continue
        yield (begin, end)

    if end is not None:
        yield (end, stop)
