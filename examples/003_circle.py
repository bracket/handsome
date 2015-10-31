from handsome.Micropolygon import Micropolygon
from handsome.MicropolygonMesh import MicropolygonMesh, Position
from handsome.Tile import Tile
from handsome.util import save_array_as_image, point, parse_color
from handsome.Pixel import FloatPixel, array_view, pixel_view
import numpy as np
from handsome.capi import fill_micropolygon_mesh, generate_numpy_begin

def constant(f):
    return f()

@constant
def palette():
    colors = {
        'white' : '#fff',
        'red'   : '#7f0000',
        'black' : '#000',
        # 'blue'  : '#0000bf',
        'blue'  : '#0000ff',
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


def main():
    image = Tile((0, 0), (512,512), 4, dtype=FloatPixel)
    image.buffer[:,:] = palette['white'].view(dtype=FloatPixel)

    center = (256, 256)
    radius = 100
    
    surface = circle(center, radius)

    # mesh = generate_mesh(center, radius)
    mesh = generate_mesh_from_surface(surface, (1, 64), 1., 1.)
    image = render_mesh(mesh, image)

    buffer = array_view(image.downsample(1))
    buffer = np.clip(buffer, 0., 1.)
    buffer = (255. * buffer).astype(dtype=np.uint8)

    save_array_as_image(pixel_view(buffer), 'render/003_circle.tiff', 'RGBA')

def generate_mesh_from_surface(surface, shape, max_u, max_v):
    u_steps = np.linspace(0.0001, max_u, shape[0] + 1, endpoint=True, dtype=np.float32)
    v_steps = np.linspace(0, max_v, shape[1] + 1, endpoint=True, dtype=np.float32)

    points = [
        [ surface(u, v) for u in u_steps ]
        for v in v_steps
    ]

    points = np.squeeze(np.array(points).view(Position)).T

    start_color = palette['blue']
    end_color = palette['black']

    colors = [
        [ (1 - v) * start_color + v * end_color for u in u_steps ]
        for v in v_steps
    ]

    colors = np.squeeze(np.array(colors).view(FloatPixel)).T
    
    mesh = MicropolygonMesh(shape)

    mesh.buffer[:,:]['position'] = points
    mesh.buffer[:,:]['color']    = colors
    # mesh.buffer[:,:]['color']    = palette['red'].view(FloatPixel)

    return mesh
    

def generate_mesh(center, radius):
    from math import cos, sin, pi

    tau = 2. * pi

    center = (256, 256)
    radius = 100

    def point_from_polar(r, p):
        return point(
            center[0] + radius * r * cos(p * tau), 
            center[1] + radius * r * sin(p * tau),
            1, 1
        )

    def color_from_polar(r, p):
        edge_color = (1 - p) * palette['blue'] + p * palette['black']
        return (1 - r) * palette['blue'] + r * edge_color

    upper_left  = (1., (.25 + .5  ) / 2. ) 
    upper_right = (1., (.0  + .25 ) / 2. ) 
    lower_left  = (1., (.5  + .75 ) / 2. ) 
    lower_right = (1., (.75 +  1. ) / 2. ) 

    # a = [
    #     [ upper_left, upper_right ],
    #     [ lower_left, lower_right ],
    # ]

    # def subdivide(points):
    #     out = { }

    #     for j in range(len(points) - 1):
    #         for i in range(len(points[0]) - 1):


    # angles = [
    #     [ .5 * tau,   .375 * tau, .25 * tau,  ],
    #     [ .625 * tau, None,       .125 * tau, ],
    #     [ .75 * tau,  .875 * tau, 0. * tau,   ],
    # ]

    polars = [ 
        [ (1., (.25 + .5)/2), (1., .25), (1., .25 / 2),        ],
        [ (1., .5),           (0., 0.),  (1., 0.),             ],
        [ (1., (.5 + .75)/2), (1., .75), (1., (.75 + 1.) / 2), ],
    ]

    # polars = [ 
    #     [ (1., (.25 + .5)/2), (1., .25 / 2),        ],
    #     [ (1., (.5 + .75)/2), (1., (.75 + 1.) / 2), ],
    # ]

    def subdivide_pair(prev_pair, next_pair):
        r = (prev_pair[0] + next_pair[0]) / 2

        if r == 0.:
            return (r, 0.)
        
        p = (prev_pair[1] + next_pair[1]) / 2
        return (r, p)


    def subdivide_row(row):
        out = [ row[0] ]
        for p, n in zip(row, row[1:]):
            out.append(subdivide_pair(p, n))
            out.append(n)
        return out

    def subdivide_columns(prev_row, next_row):
        out = [ ]
        for p, n in zip(prev_row, next_row):
            out.append(subdivide_pair(p, n))

        return out

    def subdivide_polars(polars):
        next_polars = [ ]

        prev_row = None
        next_row = None

        for row in polars:
            prev_row, next_row = next_row, subdivide_row(row)

            if prev_row is None:
                continue

            if not next_polars:
                next_polars.append(prev_row)

            next_polars.append(subdivide_columns(prev_row, next_row))
            next_polars.append(next_row)

        return next_polars

    polars = subdivide_polars(polars)
    
    points = [ [ point_from_polar(*p) for p in row ] for row in polars ]
    colors = [ [ color_from_polar(*p) for p in row ] for row in polars ]

    shape = (len(polars) - 1, len(polars[0]) - 1)

    mesh = MicropolygonMesh(shape)
    mesh.buffer[:,:]['position'] = points
    mesh.buffer[:,:]['color']    = colors

    return mesh

def render_mesh(mesh, tile):
    tile_width, tile_height = tile.buffer.shape
    mesh_width, mesh_height = mesh.buffer.shape

    fill_micropolygon_mesh(
        mesh_width, mesh_height,
        generate_numpy_begin(mesh.buffer),
        tile_width, tile_height,
        generate_numpy_begin(tile.coordinate_image),
        generate_numpy_begin(tile.buffer)
    )

    return tile



if __name__ == '__main__':
    main()
