from handsome.Tile import Tile
from handsome.Pixel import FloatPixel, array_view
from handsome.capi import generate_numpy_begin, fill_micropolygon_mesh
from handsome.util import color

from pathlib import Path

import ctypes
import json
import numpy as np


def test_coordinate_image(tmpdir):
    try:
        lib = build_test_so(tmpdir)
    except Exception as e:
        import pdb
        pdb.set_trace()

    print_coordinates = lib['print_coordinates']
    print_coordinates.restype = ctypes.c_char_p

    expected = [ 
        [ 0, 3  ], [ 1, 3 ],
        [ 0, 2  ], [ 1, 2 ],
        [ 0, 1, ], [ 1, 1 ],
        [ 0, 0, ], [ 1, 0 ],
    ]

    tile = Tile((0, 0), (2, 4), 1)

    image = tile.coordinate_image
    width, height = image.shape
    size = width * height

    ptr = generate_numpy_begin(image)

    text = print_coordinates(ptr, size)
    coords = json.loads(text.decode('utf-8'))

    assert coords == expected


def test_tile_render():
    from handsome.MicropolygonMesh import MicropolygonMesh
    from handsome.Tile import Tile

    mesh = MicropolygonMesh((1, 1))

    mesh.buffer[:,:]['position'] = [
        [ (16, 16, 1, 1), (32, 16, 1, 1) ],
        [ (0, 0, 1, 1),   (16, 0, 1, 1) ],
    ]

    red    = color(1, 0, 0)
    green  = color(0, 1, 0)
    orange = color(1, 1, 0)
    black  = color(0, 0, 0, 1)
    zero   = color(0, 0, 0, 0)

    mesh.buffer[:,:]['color'] = [
        [ green, orange, ],
        [ black, red, ],
    ]

    mesh_rows, mesh_columns = mesh.buffer.shape

    tile = Tile((0,0), (32, 16), 1, FloatPixel)

    tile_rows, tile_columns = tile.buffer.shape

    fill_micropolygon_mesh(
        mesh_rows, mesh_columns,
        generate_numpy_begin(mesh.buffer),
        generate_numpy_begin(mesh.bounds),
        tile_rows, tile_columns,
        tile.bounds,
        generate_numpy_begin(tile.coordinate_image),
        generate_numpy_begin(tile.buffer),
    )

    buffer = array_view(tile.buffer)
    rows, columns, channels = buffer.shape

    def image(x, y):
        return buffer[rows - 1 - y, x]

    low, high = 1/16, 15/16

    expected = [
        ((0, 0),   color(0, 0, 0, 1)),
        ((15, 0),  color(15/16, 0, 0, 1)),
        ((16, 0),  color(0, 0, 0, 0)),
        ((31, 0),  color(0, 0, 0, 0)),

        ((0, 8),   color(0, 0, 0, 0)),
        ((8,8),    color(0, 1/2, 0, 1)),
        ((16,8),   color(1/2, 1/2, 0, 1)),
        ((31, 8),  color(0, 0, 0, 0)),

        ((0, 15),  color(0, 0, 0, 0)),
        ((15, 15), low * black + high * green),
        ((30, 15), low * (low * black + high * green) + high * (low * red + high * orange)),
    ]

    for index, c in expected:
        assert points_are_close(image(*index), c)


def build_test_so(tmpdir):
    from phillip.build import build_so, generate_extension_args, load_library

    here = Path(__file__).parent

    sources = list(map(str, [
        here / 'cpp/test_c.cpp'
    ]))

    extension_args = generate_extension_args()

    target_dir = tmpdir / 'build'

    so_path = build_so(
        'test_c', str(tmpdir),
        sources, extension_args
    )

    print("\n", so_path, "\n")

    return load_library(so_path)


def points_are_close(p0, p1, tol=1e-5):
    return np.linalg.norm(p1 - p0) < tol
