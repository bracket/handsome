from handsome.MicropolygonMesh import MicropolygonMesh, Position
from handsome.Pixel import FloatPixel, array_view, pixel_view
from handsome.Tile import Tile
from handsome.TileCache import TileCache
from handsome.capi import fill_micropolygon_mesh, generate_numpy_begin
from handsome.util import save_array_as_image, point, parse_color
import numpy as np


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


def star(center, radius):
    from math import cos, sin, pi

    start = pi / 2
    delta = 2. * pi / 5

    center = np.array(center + (1, 1), dtype=np.float32)

    outer = np.array([
        (
            center[0] + radius * cos(start + i * delta),
            center[1] + radius * sin(start + i * delta),
            1,
            1
        )
        for i in range(5)
    ], dtype=np.float32)

    p = outer[2,:2] - outer[0,:2]
    q = outer[1,:2] - outer[4,:2]
    b = outer[1,:2] - outer[0,:2]

    A = np.array([p, q]).T
    (u, v) = np.linalg.solve(A, b)

    inner = [ ]

    for i in range(5):
        start = outer[i,:]
        end   = outer[(i + 2) % len(outer),:]
        inner.append((1 - u) * start + u * end)

    points = [
        [ outer[1], inner[0],                   outer[0], inner[4],                   outer[4], ],
        [ inner[1], .5 * (inner[1] + center),   center ,  .5 * (center + inner[3]),   inner[3], ],
        [ outer[2], .5 * (outer[2] + inner[2]), inner[2], .5 * (inner[2] + outer[3]), outer[3], ],
    ]

    red, black, blue = [
        palette[color].view(dtype=FloatPixel)
        for color in ('red', 'black', 'blue')
    ]

    colors = [
        [ red ,  black, blue , red,   black, ],
        [ blue,  red,   black, blue,  red,   ],
        [ black, blue,  red,   black, blue,  ],
    ]

    rows = len(points) - 1
    columns = len(points[0]) - 1

    mesh = MicropolygonMesh((rows, columns))
    mesh.buffer[:,:]['position'] = points
    mesh.buffer[:,:]['color'] = colors

    return mesh


def main():
    render_frame(0)


def render_frame(frame_no):
    print('rendering frame {}'.format(frame_no))

    image = Tile((0, 0), (512,512), 4, dtype=FloatPixel)
    image.buffer[:,:] = palette['white'].view(dtype=FloatPixel)

    center = (256, 256)
    radius = 192

    mesh = star(center, radius)

    cache = render_mesh(mesh)
    cache.composite_into(image)

    buffer = array_view(image.downsample(1))
    buffer = np.clip(buffer, 0., 1.)
    buffer = (255. * buffer).astype(dtype=np.uint8)

    path = 'render/004/frame_{:03}.tiff'.format(frame_no)
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

def shader(u, v):
    high_color = palette['clear']

    s = step(wrap(v, 10), .5)
    low_color = (1. - s) * palette['black'] + s * palette['blue']

    t = step(wrap(v, 20), .5)
    return (1. - t) * low_color + t * high_color


def render_mesh(mesh):
    cache = TileCache((16, 16), 4, FloatPixel)

    mesh_bounds = mesh.outer_bounds
    mesh_rows, mesh_columns = mesh.buffer.shape

    for tile in cache.get_tiles_for_bounds(mesh_bounds):
        tile_rows, tile_columns = tile.buffer.shape

        fill_micropolygon_mesh(
            mesh_rows, mesh_columns,
            generate_numpy_begin(mesh.buffer),
            generate_numpy_begin(mesh.bounds),
            tile_rows, tile_columns,
            tile.bounds,
            generate_numpy_begin(tile.coordinate_image),
            generate_numpy_begin(tile.buffer)
        )

    return cache


if __name__ == '__main__':
    main()
