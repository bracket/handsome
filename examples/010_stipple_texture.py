from pathlib import Path
from handsome import *
from pprint import pprint

import numpy as np

FILE = Path(__file__).resolve().absolute()
HERE = FILE.parent
RENDER = HERE / 'render' / '010'

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


def generate_dot_mesh():
    from math import pi, cos, sin
    div_level = 2
    divisions = 2 ** div_level

    shape = (divisions, divisions)

    mesh = MicropolygonMesh(shape)

    center = np.array((256, 256, 1, 1), dtype=np.float32)
    radius = 100

    scale = 2 ** -.5

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

    mesh.buffer[:,:]['position'] = points
    mesh.buffer[:,:]['color'] = palette['black'].view(FloatPixel)

    pprint(points)

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

def main():
    image = Tile((0, 0), (512, 512), 4, dtype=FloatPixel)
    image.buffer[:,:] = palette['white'].view(dtype=FloatPixel)

    frame_no = 0

    mesh = generate_dot_mesh()

    cache = render_mesh(mesh)
    cache.composite_into(image)

    buffer = array_view(image.downsample(1))
    buffer = np.clip(buffer, 0., 1.)
    buffer = (255. * buffer).astype(dtype=np.uint8)

    path = Path(RENDER / 'frame_{:03}.tiff'.format(frame_no))
    path.parent.mkdir(exist_ok=True, parents=True)

    save_array_as_image(pixel_view(buffer), path, 'RGBA')


if __name__ == '__main__':
    main()
