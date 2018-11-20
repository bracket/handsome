import numpy as np
import os
import math
import random

from handsome.MicropolygonMesh import MicropolygonMesh, Vertex, Position
from handsome.Pixel import FloatPixel, array_view, pixel_view
from handsome.Tile import Tile
from handsome.TileCache import TileCache
from handsome.util import render_mesh
from handsome.TransformStack import TransformStack

import sweatervest
from sweatervest import parse_scene


def main():
    import sys

    scene_path = sys.argv[1]
    render_path = sys.argv[2]

    render_image(scene_path, render_path)


def render_image(scene_path, out_path):
    from handsome.util import save_array_as_image

    scene = parse_scene(scene_path)
    canvas = render_scene(scene)

    buffer = array_view(canvas.downsample(1))
    buffer = np.clip(buffer, 0., 1.)
    buffer = (255. * buffer).astype(dtype=np.uint8)

    save_array_as_image(pixel_view(buffer), out_path, 'RGBA')


def make_canvas(canvas, sample_rate=4):
    from sweatervest.util import parse_color

    extents = canvas['extents']

    color = canvas.get('color', None)

    if color is None:
        color = np.array([1, 1, 1, 1], dtype=np.float32).view(dtype=FloatPixel)
    elif isinstance(color, str):
        color = [ c / 255. for c in parse_color(color) ]
        color = np.array(color, dtype=np.float32).view(dtype=FloatPixel)
    elif isinstance(color, (tuple, list)):
        color = [ c / 255. if isinstance(c, int) else c for c in color ]
        color = np.array(color, dtype=np.float32).view(dtype=FloatPixel)

    out = Tile((0, 0), extents, sample_rate, dtype=FloatPixel)
    out.buffer[:,:] = color

    return out


mesh_extractors = { }

current_xform = TransformStack()

def extract_meshes(obj):
    return mesh_extractors[type(obj)](obj)


def render_scene(scene):
    canvas = make_canvas(scene.data['canvas'])
    meshes = extract_meshes(scene.data['top'])

    for mesh in meshes:
        cache = render_mesh(mesh)
        cache.composite_into(canvas)

    return canvas


def extract_meshes_from_group(group_data):
    with current_xform(group_data.xform):
        for child in group_data.children:
            yield from extract_meshes(child)


def extract_meshes_from_micropolygon_mesh(mesh_data):
    shape = tuple(d - 1 for d in mesh_data.vertices.shape[:-1])
    mesh = MicropolygonMesh(shape)

    mesh.buffer[:] = np.squeeze(mesh_data.vertices.view(Vertex))
    apply_transform_to_mesh(current_xform, mesh)

    yield mesh


def apply_transform_to_mesh(xform, mesh):
    buffer = mesh.buffer

    array_dtype = np.dtype((np.float32, 4))

    positions = np.ravel(buffer['position']).view(array_dtype)
    positions = xform.dot(positions.T).T
    positions = np.ravel(positions).astype(np.float32).reshape(buffer.shape + (4,))
    positions = np.squeeze(positions.view(Position))

    buffer['position'] = positions


def surface_from_circle(circle):
    from math import cos, sin, pi
    from handsome.util import point

    tau = 2 * pi

    center = circle.center
    radius = circle.radius

    def surface(u, v):
        return point(
            center[0] + radius * u * cos(v * tau),
            center[1] + radius * u * sin(v * tau),
            1, 1
        )

    return surface


def generate_mesh_from_surface(surface, shader, shape, u_range, v_range):
    u_start, u_end = u_range
    v_start, v_end = v_range

    u_steps = np.linspace(u_start, u_end, shape[0] + 1, endpoint=True, dtype=np.float32)
    v_steps = np.linspace(v_start, v_end, shape[1] + 1, endpoint=True, dtype=np.float32)

    points = [
        [ surface(u, v) for u in u_steps ]
        for v in v_steps
    ]

    colors = [
        [ shader(u, v) for u in u_steps ]
        for v in v_steps
    ]

    points = np.squeeze(np.array(points).view(Position)).T
    colors = np.squeeze(np.array(colors).view(FloatPixel)).T

    mesh = MicropolygonMesh(shape)

    mesh.buffer[:,:]['position'] = points
    mesh.buffer[:,:]['color'] = colors

    return mesh

palette = [
    np.array([0, .1, 1.1, .5], dtype=np.float32),
    np.array([.5, 0, 0, .5], dtype=np.float32),
]

center_colors = [
    np.array([ 0, 0, 0, 0 ], dtype=np.float32),
    np.array([.1, 0, .1, 1], dtype=np.float32),
]

interior_colors = [
    np.array([ .7, 0, 0, .5 ], dtype=np.float32),
    np.array([  1, 1, 1, 1 ], dtype=np.float32),
    np.array([  0, 0, .7, .5 ], dtype=np.float32),
]

edge_colors = [
    np.array([ .7, 0, 0, 1 ], dtype=np.float32),
    np.array([  0, 0, 0, 1 ], dtype=np.float32),
    np.array([  0, 0, .7, 1 ], dtype=np.float32),
]

def step(x, cutoff):
    if x < cutoff:
        return 0.
    else:
        return 1.


def extract_meshes_from_circle(circle):
    from math import pi
    import random

    surface = surface_from_circle(circle)

    low_cutoff = 3 / circle.radius
    high_cutoff = 1 - 3 / circle.radius

    center_color = random.choice(center_colors)
    interior_color = random.choice(interior_colors)
    edge_color = random.choice(edge_colors)

    def shader(u, v):
        t_0 = (1 - step(u, low_cutoff))
        t_2 = step(u, high_cutoff)
        t_1 = 1 - (t_0 + t_2)
        return t_0 * center_color + t_1 * interior_color + t_2 * edge_color

    mesh = generate_mesh_from_surface(
        surface, shader,
        (circle.radius / 2, circle.radius * pi / 3),
        (.0001, 1),
        (0, 1.),
    )

    # mesh.buffer[:]['color'] = circle.color.view(FloatPixel)

    apply_transform_to_mesh(current_xform, mesh)

    yield mesh

class TriangleDistribution(object):
    def __init__(self, min_x, mid_x, max_x):
        self.min_x = min_x
        self.mid_x = mid_x
        self.max_x = max_x

        integral = .5 * (max_x - min_x)
        self.max_y = 1 / integral


    def __call__(self, x):
        if x <= self.min_x:
            return 0.

        if self.max_x < x:
            return 0.

        if x <= self.mid_x:
            low, high = self.min_x, self.mid_x
            t = (x - low) / (high - low)
        else:
            low, high = self.mid_x, self.max_x
            t = (high - x) / (high - low)

        return t * self.max_y


    def sample(self):
        import random

        min_x = self.min_x
        max_x = self.max_x
        max_y = self.max_y

        while True:
            x = random.uniform(min_x, max_x)
            y = random.uniform(0, max_y)

            if y < self(x):
                return x


angle_distribution =  TriangleDistribution(
    30 / 180. * math.pi,
    55 / 180. * math.pi,
    65 / 180. * math.pi
)

def read_blank_scene():
    scene_path = os.path.join(os.path.split(__file__)[0], 'data', 'blank_scene.yaml')
    return parse_scene(scene_path)


def _generate_texture_scene():
    import random
    from math import cos, sin, pi
    from sweatervest import Circle

    tau = 2 * pi

    scene = read_blank_scene()

    scene.data['top'].xform = np.array([
        [ 1, 0, 0, 256, ],
        [ 0, 1, 0, 256,   ],
        [ 0, 0, 1, 0,   ],
        [ 0, 0, 0, 1,   ],
    ], dtype=np.float32)

    radius = 25
    r_scale = np.linspace(25., 15., 10, endpoint=True)

    base = np.array([ 0, 0, 1, 1 ], dtype=np.float32)

    spine = np.array([ 0, 1, 0, 0 ], dtype=np.float32)
    left = np.array([ -1, 0, 0, 0 ], dtype=np.float32)

    offset = 2 * radius * spine

    circles = scene.data['top'].children

    center = base + .5 * offset

    for r in r_scale:
        circles.append(Circle({
            'center' : center + random.uniform(1.1, 1.2) * r * left,
            'radius' : random.uniform(1, 1.1) * r,
        }))

        center += .275 * offset

        circles.append(Circle({
            'center' : center - random.uniform(1.1, 1.2) * r * left,
            'radius' : random.uniform(1, 1.1) * r,
        }))

        center += .775 * offset

    return scene

class Circle(object):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius


    def intersects(self, other):
        delta = self.center - other.center
        d_sq = delta.dot(delta)

        r = self.radius
        o = other.radius

        s = r * r + 2 * r * o + o * o

        if d_sq < s:
            return True
        else:
            return False

def check_intersects(test_circle, circles):
    for circle in circles:
        if circle.intersects(test_circle):
            return True

    return False


def generate_texture_scene():
    from math import cos, sin, pi

    radii = TriangleDistribution(10, 40, 50)

    scene = read_blank_scene()

    scene.data['top'].xform = np.array([
        [ 1 , 0 , 0 , 256 , ],
        [ 0 , 1 , 0 , 256 , ],
        [ 0 , 0 , 1 , 0   , ],
        [ 0 , 0 , 0 , 1   , ],
    ], dtype=np.float32)

    max_circles = 200
    max_tries = 100000
    circles = [ ]

    t = 0

    while len(circles) < max_circles and t < max_tries:
        t += 1
        x = random.uniform(-256, 256)
        y = random.uniform(-256, 256)
        r = radii.sample()

        test_circle = Circle(np.array([ x, y ], dtype=np.float32), r)

        if check_intersects(test_circle, circles):
            continue

        circles.append(test_circle)


    for c in circles:
        scene.data['top'].children.append(
            sweatervest.Circle({
                'center' : c.center,
                'radius' : c.radius,
            })
        )

    return scene


def generate_texture():
    from handsome.util import save_array_as_image

    scene = generate_texture_scene()
    canvas = render_scene(scene)

    buffer = array_view(canvas.downsample(1))
    buffer = np.clip(buffer, 0., 1.)
    buffer = (255. * buffer).astype(dtype=np.uint8)

    save_array_as_image(pixel_view(buffer), 'render/texture.tiff', 'RGBA')


mesh_extractors[sweatervest.MicropolygonMesh] = extract_meshes_from_micropolygon_mesh
mesh_extractors[sweatervest.Group] = extract_meshes_from_group
mesh_extractors[sweatervest.Circle] = extract_meshes_from_circle


if __name__ == '__main__':
    main()
    # generate_texture()
