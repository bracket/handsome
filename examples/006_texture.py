from handsome.MicropolygonMesh import MicropolygonMesh, Vertex, Position
from handsome.Pixel import FloatPixel, array_view, pixel_view
from handsome.Tile import Tile
from handsome.TileCache import TileCache
from handsome.util import point, render_mesh
from handsome.capi import generate_numpy_begin, generate_numpy_span

import numpy as np
import os

def main():
    from handsome.util import save_array_as_image

    canvas = make_canvas({
        'extents' : (512, 512),
        'color'   : '#fff',
    })

    surface = generate_surface()
    shader = generate_texture_shader()

    mesh = generate_mesh(surface, shader)

    cache = render_mesh(mesh)
    cache.composite_into(canvas)

    buffer = array_view(canvas.downsample(1))
    buffer = np.clip(buffer, 0., 1.)
    buffer = (255 * buffer).astype(np.uint8)

    save_array_as_image(pixel_view(buffer), 'render/006_texture.tiff', 'RGBA')


def generate_surface():
    lower_left  = point(0, 0, 1, 1,)

    # up = 128 * np.array([0, 1, 0, 0], dtype=np.float32)
    # right = 128 * np.array([1, 0, 0, 0], dtype=np.float32)

    # up = np.array([256, 512, 0, 0], dtype=np.float32)
    # right = np.array([256, 0, 0, 0], dtype=np.float32)
    
    up = np.array([256, 512, 0, 0], dtype=np.float32)
    right = np.array([256, 0, 0, 0], dtype=np.float32)

    def surface(u, v):
        return lower_left + u * right + v * up

    return surface


def generate_texture_shader():
    dir_path, base_path = os.path.split(__file__)
    texture_path = os.path.abspath(os.path.join(dir_path, 'render', 'texture.tiff'))
    # texture_path = os.path.abspath(os.path.join(dir_path, 'render', 'texture_black.tif'))
    texture = read_texture(texture_path)

    c_sample_texture = load_sampler_lib()['sample_texture']

    texture_start, texture_end = generate_numpy_span(texture)
    rows, columns = texture.shape

    def shader(u, v):
        nonlocal texture # forces closure so texture isn't garbage collected
        return c_sample_texture(texture_start, texture_end, columns, rows, u, v)
        # return sample_texture(texture, u, v)

    return shader


def generate_mesh(surface, shader):
    # shape = (128, 128)
    shape = (256, 256)

    mesh = MicropolygonMesh(shape)
    shape = mesh.buffer.shape

    u_steps = np.linspace(0, 1, shape[1], endpoint=True)
    v_steps = np.linspace(0, 1, shape[0], endpoint=True)

    points = [ [ surface(u, v) for u in u_steps ] for v in v_steps ]
    mesh.buffer[:,:]['position'] = points

    colors = [ [ shader(u, v) for u in u_steps ] for v in v_steps ]
    mesh.buffer[:,:]['color'] = colors

    return mesh


    sample_texture_to_mesh = load_sampler_lib()['sample_texture_to_mesh']

    mesh_start = generate_numpy_begin(mesh.buffer)
    mesh_width, mesh_height = mesh.buffer.shape

    dir_path, base_path = os.path.split(__file__)
    texture_path = os.path.abspath(os.path.join(dir_path, 'render', 'texture.tiff'))
    # texture_path = os.path.abspath(os.path.join(dir_path, 'render', 'texture_black.tif'))
    texture = read_texture(texture_path)

    texture_start = generate_numpy_begin(texture)
    texture_width, texture_height = texture.shape

    sample_texture_to_mesh(
        mesh_start, mesh_width, mesh_height,
        texture_start, texture_width, texture_height,
    )

    return mesh


def read_texture(path):
    from PIL import Image
    image = Image.open(path)

    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    out = np.array(image).astype(np.float32) / 255.
    out = np.squeeze(out.view(FloatPixel))

    return out


black = pixel_view(np.array([ 0., 0., 0., 0. ], dtype=np.float32))

def sample_texture(texture, s, t):
    from math import floor

    t = 1. - t

    if not (0. <= s < 1.):
        return black

    if not (0. <= t < 1.):
        return black

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
    top_left     = texture[t_index,     s_index,:]
    bottom_left  = texture[t_index,     s_index + 1,:]
    top_right    = texture[t_index + 1, s_index,:]
    bottom_right = texture[t_index + 1, s_index + 1,:]

    u  = s_frac
    up = 1 - s_frac
    v  = t_frac
    vp = 1 - t_frac

    out  = up * vp * top_left
    out += up * v * bottom_left
    out += u * vp * top_right
    out += u * v * bottom_right

    return out


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


def import_from_dll(name, path):
    from importlib.machinery import ExtensionFileLoader
    return ExtensionFileLoader(name, path).load_module()


def load_sampler_lib():
    import ctypes
    from ctypes import c_void_p, c_int, c_float

    so_path = build_so('__main__.006_shader', [ '006/shader.cpp' ])
    lib = ctypes.cdll.LoadLibrary(so_path)

    class Sample(ctypes.Structure):
        _fields_ = [
            ('R', ctypes.c_float),
            ('G', ctypes.c_float),
            ('B', ctypes.c_float),
            ('A', ctypes.c_float),
        ]

    out = { }

    out['sample_texture'] = lib['sample_texture']
    out['sample_texture'].argtypes = (c_void_p, c_void_p, c_int, c_int, c_float, c_float)
    out['sample_texture'].restype = Sample

    out['sample_texture_to_mesh'] = lib['sample_texture_to_mesh']
    out['sample_texture_to_mesh'].argtypes = (c_void_p, c_int, c_int, c_void_p, c_int, c_int)

    return out


def find_handsome_include_dir():
    import handsome

    handsome_dir, _ = os.path.split(handsome.__file__)

    cpp_dir = os.path.join(handsome_dir, '..', 'src', 'cpp')
    cpp_dir = os.path.abspath(cpp_dir)

    return cpp_dir


def build_so(module_name, sources, setup_args=None):
    from distutils.dist import Distribution
    from distutils.errors import DistutilsArgError
    from distutils.extension import Extension
    from shutil import copy2

    setup_args = generate_setup_args(setup_args)

    dist = Distribution(setup_args)

    ext = Extension(
        name = module_name,
        sources = sources,
        include_dirs = [ find_handsome_include_dir() ],

        extra_compile_args = [ '-std=c++11' ],
    )

    if dist.ext_modules is None:
        dist.ext_modules = [ ext ]
    else:
        dist.ext_modules.append(ext)

    target_dir, _ = os.path.split(os.path.abspath(__file__))

    build = dist.get_command_obj('build')
    build.build_base = os.path.join(target_dir, 'build')

    cfgfiles = dist.find_config_files()
    dist.parse_config_files(cfgfiles)

    try:
        ok = dist.parse_command_line()
    except DistutilsArgError:
        raise

    if not ok:
        raise RuntimeError('Build cannot continue')

    command = dist.get_command_obj("build_ext")
    dist.run_commands()

    so_path = os.path.abspath(command.get_outputs()[0])
    _, so_name = os.path.split(so_path)

    target_path = os.path.join(target_dir, so_name)

    if os.path.isfile(target_path):
        os.unlink(target_path)
    
    copy2(so_path, target_path)

    return target_path


def generate_setup_args(setup_args=None):
    setup_args = { } if setup_args is None else dict(setup_args)

    script_args = setup_args.get('script_args')

    if script_args is None:
        script_args = [ ]

    args = [ "--quiet", "build_ext" ]

    setup_args['script_name'] = None
    setup_args['script_args'] = args + script_args

    return setup_args


if __name__ == '__main__':
    main()
