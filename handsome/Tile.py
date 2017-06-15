__all__ =  [ 'Tile' ]

from .Coordinate import Coordinate
from .Exceptions import HandsomeException
from .Interval import Interval
from .Pixel import Pixel, array_view, pixel_view
from .capi import generate_numpy_begin, c_void_p
from handsome.capi import Rectangle, downsample_tile, generate_numpy_begin
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
        self.__tile_bounds = None

        self.__buffer_ptr = None


    def set_origin(self, origin):
        self.origin     = origin
        self.horizontal = Interval(origin[0], origin[0] + self.shape[0])
        self.vertical   = Interval(origin[1], origin[1] + self.shape[1])
        self.__coordinate_image = None
        self.__tile_bounds = None


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
        if horizontal is None:
            return None

        vertical = self.vertical.intersection(other.vertical)
        if vertical is None:
            return None

        return (
            self.slice_from_intervals(horizontal, vertical),
            other.slice_from_intervals(horizontal, vertical)
        )


    def slice_from_intervals(self, horizontal, vertical):
        left = self.origin[0]
        top = self.origin[1] + self.shape[1]
        sample_rate = self.sample_rate

        return np.s_[
            (horizontal.start - left) * sample_rate : (horizontal.end - left) * sample_rate : 1,
            (top - vertical.end) * sample_rate : (top - vertical.start) * sample_rate : 1
        ]


    @property
    def buffer(self):
        if self.__buffer is not None:
            return self.__buffer

        dtype = self.dtype
        shape = (self.shape[1] * self.sample_rate, self.shape[0] * self.sample_rate)
        cacher = tile_cachers.get((shape, dtype))

        if cacher is None:
            cacher = tile_cachers[(shape, dtype)] = make_tile_cacher(shape, dtype)

        ptr, buffer = next(cacher)

        self.__buffer_ptr = ptr
        self.__buffer = buffer

        return buffer


    @property
    def buffer_ptr(self):
        if self.__buffer_ptr is not None:
            return self.__buffer_ptr

        buffer = self.buffer

        return self.__buffer_ptr


    @property
    def coordinate_image(self):
        if self.__coordinate_image is not None:
            return self.__coordinate_image

        self.__coordinate_image = make_coordinate_image(self.origin, self.shape, self.sample_rate)

        return self.__coordinate_image

    @property
    def bounds(self):
        if self.__tile_bounds is not None:
            return self.__tile_bounds

        self.__tile_bounds = Rectangle(
            self.origin[0],
            self.origin[1],
            self.origin[0] + self.shape[0],
            self.origin[1] + self.shape[1]
        )

        return self.__tile_bounds

    def downsample(self, sample_rate):
        downrate = int(math.ceil(self.sample_rate / sample_rate))

        in_height, in_width = self.buffer.shape
        buffer = array_view(self.buffer)

        new_shape = [
            int(math.ceil(o / downrate))
            for o in buffer.shape
        ]

        new_shape[-1] = buffer.shape[-1]
        out_height, out_width = new_shape[:2]

        out = np.zeros(shape=new_shape, dtype=np.float32)

        downsample_tile(
            generate_numpy_begin(buffer),
            in_width, in_height,
            downrate, downrate,
            generate_numpy_begin(out),
            out_width, out_height

        )

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

        slices = self.intersection_slices(from_tile)

        if slices is None:
            return

        target_slice, source_slice = slices

        alpha = np.copy(from_tile.buffer[source_slice]['A'])
        alpha = alpha.reshape(alpha.shape + (1,))

        target = array_view(self.buffer[target_slice])

        target[:] = (
            (1 - alpha) * array_view(self.buffer[target_slice])
            + alpha * array_view(from_tile.buffer[source_slice])
        )

def make_coordinate_image(origin, shape, sample_rate):
    width, height = shape

    xs = np.linspace(
        origin[0], float(origin[0] + width), width * sample_rate,
        endpoint = False, dtype = np.float32
    )

    ys = np.linspace(
        origin[1], origin[1] + height, height * sample_rate,
        endpoint = False, dtype = np.float32
    )[::-1]

    shape = (len(ys), len(xs))
    out = np.zeros(shape, dtype=Coordinate)

    for x in range(len(xs)):
        out[:,x]['y'] = ys

    for y in range(len(ys)):
        out[y,:]['x'] = xs

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


tile_cachers = { }


def make_tile_cacher(shape, dtype, cache_size=int(4 * 2 ** 20)):
    from functools import reduce
    from operator import mul

    item_size = dtype.itemsize

    if not isinstance(item_size, int):
        item_size = dtype().itemsize

    items_per_tile = reduce(mul, shape)
    tile_size = item_size * items_per_tile
    tiles_per_cache = max(int(cache_size // tile_size), 1)

    while True:
        cache = np.zeros(tiles_per_cache * items_per_tile, dtype=dtype)
        begin = generate_numpy_begin(cache)

        for offset in range(tiles_per_cache):
            start, end = offset * items_per_tile, (offset + 1) * items_per_tile

            ptr = c_void_p(begin.value + start * item_size)
            out = cache[start:end].reshape(shape)

            yield (ptr, out)
