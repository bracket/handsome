from handsome.Tile import Tile
from handsome.capi import generate_numpy_begin
from pathlib import Path

import ctypes
import json

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
