import invoke

import numpy as np
import ctypes
import math
from handsome.Tile import Tile, Interval, Pixel
from handsome.util import save_array_as_image, parse_color, rotate_left
from handsome.Line import Line


class c_void_p(ctypes.c_void_p):
    pass

NULL_PTR = ctypes.c_void_p(0)

def generate_numpy_span(array):
    begin = c_void_p(array.ctypes.data)
    byte_length = len(array) * array.itemsize
    end = c_void_p(begin.value + byte_length)
    return begin, end


def point(x, y, z=1):
    return np.array([x, y, 1], dtype=np.float32).T


def normalize(vector):
    return vector / math.sqrt(sum(vector * vector))


def splay_line(line, width):
    hw = width / 2.
    left = hw * normalize(rotate_left(line.direction))
    right = -left

    return [
        Line(line.start + right, line.end + right),
        Line(line.end + right, line.end + left),
        Line(line.end + left, line.start + left),
        Line(line.start + left, line.start + right),
    ]


def make_translate_transform(x, y):
    return np.array([
        [ 1, 0, x ],
        [ 0, 1, y ],
        [ 0, 0, 1 ],
    ], dtype=np.float32)


def make_raster_transform(height):
    return np.array([
        [ 1, 0,       0      ], 
        [ 0, -1,      height ], 
        [ 0, 0,       1      ], 
    ], dtype=np.float32)


@invoke.task
def test_conversion():
    shape = [ 640, 480 ]
    image = make_coordinate_image(shape)

    # out = nd.zeros

@invoke.task
def test_fill():
    shape=[640,480]
    p = point(100, 100)

    l = Line(
        point(100, 100),
        point(0, 200)
    )

    coords = make_coordinate_image(shape)
    delta = coords - l.start[:2].reshape(1,1,2)
    direction = (l.end - l.start)[:2].reshape(1,1,2)

    mask = np.inner(delta, direction).reshape(640, 480) >= 0.

    white = np.array([(255, 255, 255, 255)], dtype=Pixel)
    red   = np.array([(180, 0, 0, 255)], dtype=Pixel)

    image = np.empty(shape, dtype=Pixel, order='F')
    image[:,:] = white
    image[mask] = red

    save_array_as_image(image, 'red_white.tiff', 'RGBA')


def draw_line(line, width, color):
    shape = [640, 480]
    image = np.zeros(shape, dtype=Pixel, order='F')

    mask = np.ones(dtype=np.bool_, shape=shape)
    coords = make_coordinate_image(shape)

    for line in splay_line(line, width):
        delta = coords - line.start[:2].reshape(1,1,2)
        direction = rotate_left(line.direction)[:2].reshape(1,1,2)
        mask = mask & (np.inner(delta, direction).reshape(*shape) >= 0.)

    image[mask] = color

    return image

def composite_image(top, bottom):
    alpha = top['A'] / 255.
    alpha_prime = 1 - alpha

    for channel in ('R', 'G', 'B'):
        bottom[channel] = (top[channel] * alpha + bottom[channel] * alpha_prime).astype(np.uint8)

@invoke.task
def test_line():
    shape = [640,480]

    lines = [
        [ (100, 100), (300, 300) ],
        [ (100, 300), (300, 100) ],
        [ (100, 200), (300, 200) ],
        [ (200, 100), (200, 300) ],
    ]

    width = 10.

    white = np.array([(255, 255, 255, 255)], dtype=Pixel)

    image = np.empty(shape, dtype=Pixel, order='F')
    image[::] = white

    red = np.array([(180, 0, 0, 127)], dtype=Pixel)

    for line in lines:
        line = Line(point(*line[0]), point(*line[1]))
        composite_image(draw_line(line, width, red), image)

    save_array_as_image('test_line.tiff', image, 'RGBA')

class Vertex(object):
    pass

class Patch(object):
    pass

@invoke.task
def test_dll():
    lib = ctypes.CDLL('test.dylib')

    test = lib['test']
    test()

def fill_white(image):
    fill_white = ctypes.CDLL('test.dylib')['fill_white']
    begin,end = generate_numpy_span(image)
    width,height=image.shape
    fill_white(begin, width, height)

@invoke.task
def test_tile_intersection_slices():
    master = Tile((0, 0), (640, 400))
    tile = Tile((100, 100), (100, 300))

    blue = np.array([(0, 0, 153, 255)], dtype=Pixel)
    red = np.array([(153, 0, 0, 255)], dtype=Pixel)
    white = np.array([(255, 255, 255, 255)], dtype=Pixel)

    master.buffer[::] = white
    tile.buffer[::] = red

    m, t = master.intersection_slices(tile)
    master.buffer[m] = tile.buffer[t]

    save_array_as_image('test_tile_2.tiff', master.buffer, 'RGBA')


@invoke.task
def render_tile():
    import random

    mode = 'RGBA'
    image_shape = (640, 480)

    image = Tile((0,0), image_shape)

    r = random.SystemRandom()

    colors = {
        'white'  : '#ffff',
        'black'  : '#000f',
        '205A8C' : '205A8C',
        '6596BF' : '6596BF',
        '98F2EC' : '98F2EC',
        'BF6865' : 'BF6865',
        'F4DBD6' : 'F4DBD6',
    }

    for name, color in colors.items():
        colors[name] = parse_color(color)

    image.buffer[:,:] = colors['white']

    tile_colors = [ color for name, color in colors.items() if name not in ('black', 'white') ]
    # tile = Tile((0, 0), (100, 100))
    tile = Tile((0, 0), (16, 16))

    for x in range(0, image_shape[0], 16):
        for y in range(0, image_shape[1], 16):
            # x = int(r.random() * image_shape[0])
            # y = int(r.random() * image_shape[1])
            tile.set_origin((x, y))
            tile.buffer[:] = r.sample(tile_colors, 1)

            i, t = image.intersection_slices(tile)
            image.buffer[i] = tile.buffer[t]

    save_array_as_image('test_tile.gif', image.buffer, 'RGBA')

@invoke.task
def blocktopus():
    import random
    import math
    r = random.SystemRandom()

    mode = 'RGBA'
    image_shape = (1280, 960)
    # image_shape = (640, 480)

    image = Tile((0, 0), image_shape)

    colors = {
        'white'        : '#ffff',
        'black'        : '#000f',
        '205A8C'       : '205A8C',
        '6596BF'       : '6596BF',
        '98F2EC'       : '98F2EC',
        'BF6865'       : 'BF6865',
        'F4DBD6'       : 'F4DBD6',
        'dark_blue'    : '05115B',
        'light_blue'   : '60CAF0',
        'brown_yellow' : 'DAB32B',
        'brown'        : '855E14',
        'yellow'       : 'FFDD06',
    }

    for name, color in colors.items():
        colors[name] = parse_color(color)

    def make_tile(color):
        tile = Tile((0, 0), (16, 16))
        tile.buffer[:] = color
        return tile

    blocktopus_colors = (
        'brown',
        'brown_yellow',
        'dark_blue',
        'light_blue',
        'yellow',
    )

    tiles = { }

    def get_tile(tile_id):
        tile = tiles.get(tile_id)
        if tile is not None:
            return tile
        
        color = r.choice(blocktopus_colors)
        tiles[tile_id] = out = make_tile(color)
        out.buffer[:] = colors[color]
        return out

    spine = Line(
        point(.1 * image_shape[0], .5 * image_shape[1]),
        point(.9 * image_shape[0], .5 * image_shape[1])
    )

    direction = normalize(spine.direction)
    up = normalize(rotate_left(spine.direction))

    steps = 30 
    step_size = 1. / steps
    frequency = 2.5 * 2. * math.pi * step_size

    frames = 10 * 30

    for frame in range(frames):
        image.buffer[:] = colors['white']

        phase = 2 * 2. * math.pi * frame / frames
        phase_offset = .5 - math.cos(phase)

        for i in range(steps):
            width_factor = (1. - float(i) / (steps - 1))
            width = width_factor * .15 * image_shape[1]

            s = math.cos(frequency * i + phase) + phase_offset

            base = spine(i * step_size)

            offsets = [
                s * width * up,
                (s - 1) * width * up,
            ]

            for (j, offset) in enumerate(offsets):
                p = base + offset
                tile = get_tile((i, j))
                tile.set_origin(p[:2])

                intersection = image.intersection_slices(tile)
                if intersection is None: continue

                m, t = intersection
                image.buffer[m] = tile.buffer[t]

        path = 'blocktopus/frame_{frame:03}.tiff'.format(frame=frame)
        save_array_as_image(path, image.buffer, 'RGBA')


@invoke.task
def test_opencl():
    import numpy as np
    import pyopencl as cl

    a = np.random.rand(50000).astype(np.float32)
    b = np.random.rand(50000).astype(np.float32)

    context = cl.create_some_context()
    queue = cl.CommandQueue(context)

    mf = cl.mem_flags

    a_cl = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a)
    b_cl = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b)

    program = cl.Program(context, r'''
        __kernel void sum(__global const float * a, __global const float * b, __global float * out) {
            int gid = get_global_id(0);
            out[gid] = a[gid] + b[gid];
        }
    ''').build()

    out_cl = cl.Buffer(context, mf.WRITE_ONLY, a.nbytes)

    program.sum(queue, a.shape, None, a_cl, b_cl, out_cl)

    out = np.empty_like(a)
    cl.enqueue_copy(queue, out, out_cl)

    print(np.linalg.norm(out - (a + b)))
