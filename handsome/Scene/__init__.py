from handsome.TransformStack import TransformStack
from handsome.Pixel import pixel_view
from handsome.util import render_mesh

import numpy as np
import os
import sweatervest

__all__ = [
    'render_scene',
    'make_canvas',
    'MeshExtractor',
]


def render_scene(scene, mesh_extractor=None):
    canvas = make_canvas(scene.data['canvas'])

    if mesh_extractor is None:
        mesh_extractor = MeshExtractor(scene)

    top = scene.data['top']
    meshes = mesh_extractor.extract_meshes(top)

    meshes = list(meshes)

    for mesh in meshes:
        cache = render_mesh(mesh)
        cache.composite_into(canvas)

    return canvas


def make_canvas(canvas, sample_rate=4):
    from handsome.Tile import Tile
    from handsome.Pixel import FloatPixel
    from sweatervest.util import color_to_float

    extents = canvas['extents']

    color = color_to_float(canvas.get('color', None))

    out = Tile((0, 0), extents, sample_rate, dtype=FloatPixel)
    out.buffer[:,:] = color

    return out


default_mesh_extractors = { }


class MeshExtractor(object):
    def __init__(self, scene, mesh_extractors=None):
        self.scene = scene

        self.mesh_extractors = { }

        if mesh_extractors is not None:
            for cls, function in mesh_extractors.items():
                self.mesh_extractors[cls] = function.__get__(self)

        self.current_xform = TransformStack()


    def get_extractor(self, cls):
        extractor = self.mesh_extractors.get(cls)

        if extractor is not None:
            return extractor

        extractor = default_mesh_extractors[cls].__get__(self)
        self.mesh_extractors[cls] = extractor

        return extractor


    def extract_meshes(self, obj):
        extractor = self.get_extractor(type(obj))
        return extractor(obj)


def extract_meshes_from_group(self, group_data):
    with self.current_xform(group_data.xform):
        for child in group_data.children:
            yield from self.extract_meshes(child)


def extract_meshes_from_micropolygon_mesh(self, mesh_data):
    from handsome.MicropolygonMesh import MicropolygonMesh, Vertex

    shape = tuple(d - 1 for d in mesh_data.vertices.shape[:-1])
    mesh = MicropolygonMesh(shape)

    mesh.buffer[:] = np.squeeze(mesh_data.vertices.view(Vertex))
    apply_transform_to_mesh(self.current_xform, mesh)

    texture = mesh_data.data.get('texture')

    if texture is not None:
        from handsome.capi import generate_numpy_begin
        import ctypes

        texture_module = load_texture_module()

        subdivide_mesh = texture_module.c_subdivide_mesh

        factor = 1000

        old_cols, old_rows = mesh.shape
        new_cols, new_rows = factor * old_cols, factor * old_rows
        # new_cols, new_rows = 20 * old_cols, 20 * old_rows
        new_mesh = MicropolygonMesh((new_cols, new_rows))

        # TODO: Make this type conversion automatic
        argtypes = subdivide_mesh.argtypes
        new_mesh_pointer = ctypes.cast(generate_numpy_begin(new_mesh.buffer), argtypes[0])
        old_mesh_pointer = ctypes.cast(generate_numpy_begin(mesh.buffer), argtypes[3])
        
        b = subdivide_mesh(
            new_mesh_pointer, new_rows, new_cols,
            old_mesh_pointer, old_rows, old_cols,
        )

        mesh = new_mesh

        sample_texture_to_mesh = texture_module.c_sample_texture_to_mesh

        # TODO: Make this type conversion automatic
        argtypes = sample_texture_to_mesh.argtypes
        mesh_pointer = ctypes.cast(generate_numpy_begin(mesh.buffer), argtypes[0])
        texture_pointer = ctypes.cast(generate_numpy_begin(texture.buffer), argtypes[3])

        mesh_height, mesh_width = mesh.buffer.shape
        texture_height, texture_width = texture.shape

        texture_module.c_sample_texture_to_mesh(
            mesh_pointer, mesh_width, mesh_height,
            texture_pointer, texture_width, texture_height,
        )

    yield from slice_mesh(mesh, int(factor / 100))

def slice_mesh(mesh, factor):
    from handsome.MicropolygonMesh import MicropolygonMesh

    buffer = mesh.buffer
    rows, columns = mesh.shape

    row_stride = rows // factor
    column_stride = columns // factor

    row_start = 0

    while row_start < rows:
        row_end = row_start + row_stride
        column_start = 0

        while column_start < columns:
            column_end = column_start + column_stride

            mesh_slice = buffer[row_start:row_end + 1, column_start:column_end + 1]

            r, c = mesh_slice.shape

            mesh = MicropolygonMesh((r - 1, c - 1))
            mesh.buffer[:,:] = mesh_slice

            yield mesh

            column_start = column_end

        row_start = row_end

red = pixel_view(np.array([ 1., 0., 0., 1. ], dtype=np.float32))

# def sample_texture_to_mesh(texture, mesh):
#     mesh.buffer['color'] = red

clear = pixel_view(np.array([ 0., 0., 0., 0. ], dtype=np.float32))

def sample_texture(s, t, texture):
    from math import floor

    t = 1. - t
    s, t = t, s

    if not (0. <= s < 1.):
        return clear

    if not (0. <= t < 1.):
        return clear

    shape = texture.shape

    s = s * (shape[0] - 1)
    s_index = floor(s)
    s_frac = s - s_index
    s_index = int(s_index)

    t = t * (shape[1] - 1)
    t_index  = floor(t)
    t_frac = t - t_index
    t_index = int(t_index)

    texture      = array_view(texture)
    top_left     = texture[s_index,     t_index,:]
    bottom_left  = texture[s_index,     t_index + 1,:]
    top_right    = texture[s_index + 1, t_index,:]
    bottom_right = texture[s_index + 1, t_index + 1,:]

    u  = s_frac
    up = 1 - s_frac
    v  = t_frac
    vp = 1 - t_frac

    out  = up * vp * top_left
    out += up * v * bottom_left
    out += u * vp * top_right
    out += u * v * bottom_right

    return out


def find_handsome_cpp_dir():
    import handsome

    handsome_dir,_ = os.path.split(handsome.__file__)
    return os.path.join(handsome_dir, 'data', 'cpp')


def find_handsome_include_dir():
    import handsome

    handsome_dir, _ = os.path.split(handsome.__file__)
    return os.path.abspath(os.path.join(handsome_dir, '..', 'src', 'cpp'))


def read_cpp_file(path):
    path = os.path.join(find_handsome_cpp_dir(), path)

    with open(path, 'r') as fd:
        return fd.read()


def generate_texture_module():
    from phillip.module_generator import ModuleGenerator, Variable, Function

    from handsome.Pixel import FloatPixel
    from handsome.MicropolygonMesh import Position, Vertex

    generator = ModuleGenerator()

    generator.headers.extend([ '"Vec.hpp"', '<vector>', '<cmath>' ])

    generator.add_structure(FloatPixel, 'Color')
    generator.add_structure(Position, 'Position')
    generator.add_structure(Vertex, 'Vertex')

    # generator.add_variable(Variable('green', 'Color', '{ 0., 1., 0., 1. }', True))

    f = generator.add_function(
        'sample_texture',
        FloatPixel,
        [
            Variable('texture_start', 'Vec4 const *', None, False),
            Variable('texture_width', int, None, False),
            Variable('texture_height', int, None, False),
            Variable('s', float, None, False),
            Variable('t', float, None, False),
        ],
        read_cpp_file('sample_texture.cpp')
    )

    generator.add_function(
        'cast_vec',
        'Vec4 const &',
        [
            Variable('position', 'Position const &', None, False),
        ],
        'return *reinterpret_cast<Vec4 const *>(&position);'
    )

    generator.add_function(
        'cast_vec',
        'Vec4 const &',
        [
            Variable('color', 'Color const &', None, False),
        ],
        'return *reinterpret_cast<Vec4 const *>(&color);'
    )

    generator.add_function(
        'cast_position',
        'Position const &',
        [
            Variable('vec', 'Vec4 const &', None, False),
        ],
        'return *reinterpret_cast<Position const *>(&vec);'
    )

    generator.add_function(
        'cast_color',
        'Color const &',
        [
            Variable('vec', 'Vec4 const &', None, False),
        ],
        'return *reinterpret_cast<Color const *>(&vec);'
    )


    #TODO: Ugh...
    import ctypes
    from handsome.capi import c_void_p
    sg = generator.structure_generator

    vertex_pointer = ctypes.POINTER(sg.get_ctypes_definition(Vertex))
    color_pointer  = ctypes.POINTER(sg.get_ctypes_definition(FloatPixel))

    f = generator.add_function(
        'sample_texture_to_mesh',
        None,
        [
            Variable('mesh', vertex_pointer, None, False),
            Variable('mesh_width', int, None, False),
            Variable('mesh_height', int, None, False),
            Variable('texture', color_pointer, None, False),
            Variable('texture_width', int, None, False),
            Variable('texture_height', int, None, False),
        ],
        read_cpp_file('sample_texture_to_mesh.cpp')
    )

    generator.add_interface(f.generate_default_interface())

    f = generator.add_function(
        'subdivide_mesh',
        ctypes.c_bool,
        [
            Variable('out_mesh', vertex_pointer, None, False),
            Variable('out_rows', int, None, False),
            Variable('out_cols', int, None, False),
            Variable('in_mesh', vertex_pointer, None, False),
            Variable('in_rows', int, None, False),
            Variable('in_cols', int, None, False),
        ],
        read_cpp_file('subdivide_mesh.cpp')
    )

    generator.add_interface(f.generate_default_interface())

    return generator


def generate_module_so(module_generator):
    from phillip.build import build_so
    import ctypes
    import tempfile

    # with tempfile.TemporaryDirectory() as tmpdir:
    if True:
        tmpdir = 'tmp'
        # TODO: Generate unique path and module name from the module generator
        source_path = os.path.join(str(tmpdir), 'texture_library.cpp')

        with open(source_path, 'w') as fd:
            fd.write(module_generator.render_module())

        so_path = build_so(
            '___test__.texture_library',
            str(tmpdir),
            [ source_path ],
            { 'include_dirs' : [ find_handsome_include_dir() ] }
        )

        return ctypes.cdll.LoadLibrary(so_path)


def load_texture_module():
    import types

    out = types.ModuleType('texture_module')

    module = generate_texture_module()
    shared_object = generate_module_so(module)

    structure_generator = module.structure_generator
    
    for interface in module.interfaces:
        function = shared_object[interface.name]
        function.restype = structure_generator.get_ctypes_definition(interface.return_type)

        function.argtypes = [
            structure_generator.get_ctypes_definition(arg.type)
            for arg in interface.arguments
        ]

        setattr(out, interface.name, function)

    return out


def apply_transform_to_mesh(xform, mesh):
    from handsome.MicropolygonMesh import Position

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
    from handsome.MicropolygonMesh import MicropolygonMesh, Position
    from handsome.Pixel import FloatPixel

    u_start, u_end = u_range
    v_start, v_end = v_range

    u_steps = np.linspace(u_start, u_end, shape[0] + 1, endpoint=True, dtype=np.float32)
    v_steps = np.linspace(v_start, v_end, shape[1] + 1, endpoint=True, dtype=np.float32)

    points = [
        [ surface(u, v) for u in u_steps ]
        for v in v_steps
    ]

    points = np.squeeze(np.array(points).view(Position)).T

    mesh = MicropolygonMesh(shape)
    mesh.buffer[:,:]['position'] = points

    if shader is not None:
        colors = [
            [ shader(u, v) for u in u_steps ]
            for v in v_steps
        ]

        colors = np.squeeze(np.array(colors).view(FloatPixel)).T

        mesh.buffer[:,:]['color'] = colors

    return mesh


def extract_meshes_from_circle(self, circle):
    from math import pi
    from handsome.Pixel import FloatPixel

    surface = surface_from_circle(circle)

    mesh = generate_mesh_from_surface(
        surface, None,
        (int(circle.radius / 2), int(circle.radius * pi / 3)),
        (.0001, 1),
        (0, 1.),
    )

    mesh.buffer[:]['color'] = circle.color.view(FloatPixel)

    apply_transform_to_mesh(self.current_xform, mesh)

    yield mesh


default_mesh_extractors[sweatervest.MicropolygonMesh] = extract_meshes_from_micropolygon_mesh
default_mesh_extractors[sweatervest.Group] = extract_meshes_from_group
default_mesh_extractors[sweatervest.Circle] = extract_meshes_from_circle
