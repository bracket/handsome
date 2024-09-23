from pathlib import Path
from handsome import *
from pprint import pprint
from functools import lru_cache

from dataclasses import dataclass
from typing import List, Tuple

from groupby import list_groupby

import numpy as np

FILE = Path(__file__).resolve().absolute()
HERE = FILE.parent
RENDER = HERE / 'render' / '010'

cache = lru_cache(None)

@dataclass
class Dot:
    cell: Tuple[int]
    center : Tuple[float]
    level: float


def main():
    width = height = 512
    diagonal = np.array((width, height))

    length_sq = np.sum(diagonal * diagonal)
    diagonal = diagonal / length_sq

    dots = generate_stipple_dots(width, height)
    by_cell = list_groupby(dots, key = lambda d: (d.cell[0]//16 * 16, d.cell[1]//16 * 16))

    new_dots = [ ]

    for k, v in by_cell.items():
        position = np.array(k)
        value = 1 - np.dot(position, diagonal)
        new_dots.extend(d for d in v if d.level < value)

    print(len(new_dots))
    render_stipple_texture(width, height, new_dots)


def constant(f):
    return f()


@constant
def palette():
    colors = {
        'clear':  '#0000',
        'white':  '#fff',
        'red':    '#7f0000',
        'black':  '#000',
        'blue':   '#0000bf',
        'orange': '#FF9701',
        'green':  '#00FF00',
    }

    colors = {
        key : np.array([c / 255. for c in parse_color(value)], dtype=np.float32)
        for key, value
        in colors.items()
    }

    return colors


@cache
def dot_points():
    div_level = 2
    divisions = 2 ** div_level

    radius = 2.25
    scale = 2 ** -.5

    center = np.array([ 0, 0, 1, 1], dtype=np.float32)

    points = [
        [ scale * point(u, v, 0, 0) for u in np.linspace(-1, 1, divisions + 1, endpoint=True) ]
        for v in np.linspace(1, -1, divisions + 1, endpoint = True)
    ]

    for i, row in enumerate(points):
        if i == 0 or i == len(points) - 1:
            for j, p in enumerate(row):
                row[j] = normalize(p)

        row[0] = normalize(row[0])
        row[-1] = normalize(row[-1])

    points = [ [ center + radius * p for p in row ] for row in points ]
    points = np.squeeze(np.array(points).view(Position))

    return points


def generate_dot_mesh(transform):
    points = dot_points()

    array_type = np.dtype((np.float32 , 4))

    points = points.view(array_type)
    points = np.einsum('ij,lkj->lki', transform, points).astype(np.float32)

    points = np.squeeze(points.view(Position))

    rows, cols = points.shape
    shape = (rows - 1, cols - 1)

    mesh = MicropolygonMesh(shape)

    mesh.buffer[:,:]['position'] = points
    mesh.buffer[:,:]['color'] = palette['black'].view(FloatPixel)

    return mesh


def render_mesh(mesh):
    cache = TileCache((16, 16), 4, FloatPixel)

    mesh_bounds = mesh.outer_bounds
    mesh_width, mesh_height = mesh.buffer.shape

    for tile in cache.get_tiles_for_bounds(mesh_bounds):
        tile_width, tile_height = tile.buffer.shape

        fill_micropolygon_mesh(
            mesh_width, mesh_height,
            generate_numpy_begin(mesh.buffer),
            generate_numpy_begin(mesh.bounds),
            tile_width, tile_height,
            tile.bounds,
            generate_numpy_begin(tile.coordinate_image),
            generate_numpy_begin(tile.buffer)
        )

    return cache


def generate_stipple_dots(width, height):
    from random import Random

    cell_size = 2

    dots = [ ]

    for x in range(0, width, cell_size):
        for y in range(0, height, cell_size):
            center = (
                x + r.uniform(0., cell_size),
                y + r.uniform(0., cell_size),
            )

            dot = Dot(
                cell = (x, y),
                center = center,
                level = -1.
            )

            dots.append(dot)

    r = Random(0xdeadbeef)
    r.shuffle(dots)

    for i, d in enumerate(dots):
        d.level = (i / len(dots)) ** (1/3)

    return dots


def render_stipple_texture(width, height, dots):
    size = (width, height)

    image = Tile((0, 0), size, 4, dtype=FloatPixel)
    image.buffer[:,:] = palette['white'].view(dtype=FloatPixel)

    for d in dots:
        X = np.array([
            [ 1., 0,  0,  d.center[0] ],
            [ 0,  1., 0,  d.center[1] ],
            [ 0,  0,  1., 0. ],
            [ 0,  0,  0,  1. ],
        ])

        mesh = generate_dot_mesh(X)

        cache = render_mesh(mesh)
        cache.composite_into(image)

    buffer = array_view(image.downsample(1))
    buffer = np.clip(buffer, 0., 1.)
    buffer = (255. * buffer).astype(dtype=np.uint8)

    path = Path(RENDER / 'levels.tiff')
    path.parent.mkdir(exist_ok=True, parents=True)

    save_array_as_image(pixel_view(buffer), path, 'RGBA')


def read_image(path):
    from PIL import Image
    image = Image.open(str(path))

    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    out = np.array(image).astype(np.float32) / 255.
    out = np.squeeze(out.view(FloatPixel))

    out['A'] = 1.

    return out


if __name__ == '__main__':
    main()
