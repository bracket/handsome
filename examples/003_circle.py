from handsome.Micropolygon import Micropolygon
from handsome.MicropolygonMesh import MicropolygonMesh, Position
from handsome.Pixel import FloatPixel, array_view, pixel_view
from handsome.Tile import Tile
from handsome.TileCache import TileCache
from handsome.capi import fill_micropolygon_mesh, generate_numpy_begin
from handsome.util import save_array_as_image, point, parse_color
import numpy as np

from pathlib import Path

def constant(f):
    return f()


@constant
def palette():
    colors = {
        'clear'  : '#0000',
        'white'  : '#fff',
        'red'    : '#7f0000',
        'black'  : '#000',
        'blue' : '#0000bf',
        # 'blue'   : '#0000ff',
        'orange' : '#FF9701'
    }

    colors = {
        key : np.array([c / 255. for c in parse_color(value)], dtype=np.float32)
        for key, value
        in colors.items()
    }

    return colors


def circle(center, radius):
    from math import cos, sin, pi
    tau = 2. * pi

    def point_from_polar(u, v):
        return point(
            center[0] + radius * u * cos(v * tau),
            center[1] + radius * u * sin(v * tau),
            1, 1
        )

    return point_from_polar


def generate_meshes(surface):
    splits = 16

    u_steps = 256
    v_steps = 1024

    u_step_size = int(u_steps / splits)
    v_step_size = int(v_steps / splits)


    out = []
    for u in range(0, u_steps, u_step_size):
        for v in range(0, v_steps, v_step_size):
            mesh = generate_mesh_from_surface(
                surface,
                (u_step_size, v_step_size),
                (u / u_steps, (u + u_step_size) / u_steps),
                (v / v_steps, (v + v_step_size) / v_steps),
            )

            out.append(mesh)

    return out


def generate_meshes_(surface):
    out = [
        generate_mesh_from_surface(
            surface,
            (1, 8),
            (0.0001, 1.),
            (0.0001, 1.)
        )
    ]

    return out


def main():
    render_frame(29)


def render_frame(frame_no):
    print('rendering frame {}'.format(frame_no))

    from math import sin, pi
    tau = 2. * pi

    image = Tile((0, 0), (512,512), 4, dtype=FloatPixel)
    image.buffer[:,:] = palette['white'].view(dtype=FloatPixel)

    center = (256, 256)
    radius = 100

    surface = circle(center, radius)

    global transform

    transform = np.array(
        [
            [ 1., .0 ],
            [ .5 * sin(tau * frame_no / 60.), 1. ]
        ],
        dtype=np.float32
    )

    meshes = generate_meshes(surface)

    for mesh in meshes:
        cache = render_mesh(mesh)
        cache.composite_into(image)

    buffer = array_view(image.downsample(1))
    buffer = np.clip(buffer, 0., 1.)
    buffer = (255. * buffer).astype(dtype=np.uint8)

    path = Path('render/003/frame_{:03}.tiff'.format(frame_no))
    path.parent.mkdir(exist_ok=True, parents=True)

    save_array_as_image(pixel_view(buffer), path, 'RGBA')


def generate_mesh_from_surface(surface, shape, u_range, v_range):
    u_start, u_end = u_range
    v_start, v_end = v_range

    u_steps = np.linspace(u_start, u_end, shape[0] + 1, endpoint=True, dtype=np.float32)
    v_steps = np.linspace(v_start, v_end, shape[1] + 1, endpoint=True, dtype=np.float32)

    points = [
        [ surface(u, v) for u in u_steps ]
        for v in v_steps
    ]

    points = np.squeeze(np.array(points).view(Position)).T

    start_color = palette['blue']
    end_color = palette['black']

    colors = [
        [ shader(u, v) for u in u_steps ] for v in v_steps
    ]

    colors = np.squeeze(np.array(colors).view(FloatPixel)).T

    mesh = MicropolygonMesh(shape)

    mesh.buffer[:,:]['position'] = points
    mesh.buffer[:,:]['color']    = colors
    # mesh.buffer[:,:]['color']    = palette['red'].view(FloatPixel)

    return mesh

def wrap(value, frequency):
    return value * frequency % 1.

def step(value, cutoff):
    if value < cutoff:
        return 0.
    else:
        return 1.

uv = np.array([ 0, 0 ], np.float32)

transform = np.array([
    [ 1,   0 ],
    [ -.5, 1 ]
], dtype=np.float32)

def shader(u, v):
    uv[:] = (u, v)
    u, v = transform.dot(uv)

    high_color = palette['clear']

    s = step(wrap(v, 10), .5)
    low_color = (1. - s) * palette['black'] + s * palette['blue']

    t = step(wrap(v, 20), .5)
    return (1. - t) * low_color + t * high_color


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


if __name__ == '__main__':
    main()
