from handsome.MicropolygonMesh import MicropolygonMesh, Vertex, Position
from handsome.Pixel import FloatPixel, array_view, pixel_view
from handsome.Tile import Tile
from handsome.TileCache import TileCache
from handsome.util import point, render_mesh
from handsome.capi import generate_numpy_begin

from phillip.generate import split_and_dedent_lines, render_indents, transform_lines

import numpy as np
import os


def main():
    from handsome.util import save_array_as_image

    canvas = make_canvas({
        'extents' : (512, 512),
        'color'   : '#fff',
    })

    surface = generate_surface()
    shader = generate_shader()

    mesh = generate_mesh(surface, shader)
    meshes = subdivide_mesh(mesh)

    for mesh in meshes:
        cache = render_mesh(mesh)
        cache.composite_into(canvas)

    buffer = array_view(canvas.downsample(1))
    buffer = np.clip(buffer, 0., 1.)
    buffer = (255 * buffer).astype(np.uint8)

    save_array_as_image(pixel_view(buffer), 'render/007_subdivider.tiff', 'RGBA')


def generate_mesh(surface, shader):
    # shape = (128, 128)
    shape = (256, 256)

    mesh = MicropolygonMesh(shape)
    shape = mesh.buffer.shape

    dir_path, base_path = os.path.split(__file__)
    texture_path = os.path.abspath(os.path.join(dir_path, 'render', 'texture.tiff'))
    texture = read_texture(texture_path)

    texture_start = generate_numpy_begin(texture)
    texture_width, texture_height = texture.shape

    mesh_width, mesh_height = mesh.buffer.shape

    c_generate_mesh = load_sampler_lib()['generate_mesh']

    c_generate_mesh(
        generate_numpy_begin(mesh.buffer),
        mesh_width, mesh_height,
        texture_start,
        texture_width, texture_height
    )

    return mesh


def subdivide_mesh(mesh):
    buffer = mesh.buffer
    rows, columns = mesh.shape

    row_stride = rows // 4
    column_stride = columns // 4

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


def generate_surface():
    lower_left  = point(64, 64, 1, 1,)
    upper_left  = point(127,256, 1, 1)
    lower_right = point(256, 127, 1, 1)
    upper_right = point(496, 496, 1, 1)


    def surface(u, v):
        low = (1 - u) * lower_left + u * lower_right
        high = (1 - u) * upper_left + u * upper_right
        return (1 - v) * low + v * high

    return surface


def generate_shader():
    dir_path, base_path = os.path.split(__file__)
    texture_path = os.path.abspath(os.path.join(dir_path, 'render', 'texture.tiff'))
    texture = read_texture(texture_path)

    def shader(u, v):
        return sample_texture(texture, u, v)

    return shader

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


def read_texture(path):
    from PIL import Image
    image = Image.open(path)

    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    out = np.array(image).astype(np.float32) / 255.
    out = np.squeeze(out.view(FloatPixel))

    out['A'] = 1.

    return out


def sample_texture_template():
    return split_and_dedent_lines(r'''
        Sample sample_texture(
            Vec4 const * texture_start,
            int columns, int rows,
            float s, float t
        )
        {
            t = 1. - t;

            if (s < 0.) { return black; }
            if (1. <= s) { return black; }

            if (t < 0.) { return black; }
            if (1. <= t) { return black; }

            s = s * (columns - 1);
            float s_index_f = std::floor(s);
            float s_frac = s - s_index_f;
            int s_index = static_cast<int>(s_index_f);

            t = t * (rows - 1);
            float t_index_f  = std::floor(t);
            float t_frac = t - t_index_f;
            int t_index = static_cast<int>(t_index_f);

            Vec4 const * top_left     = texture_start + s_index        + columns * t_index;
            Vec4 const * bottom_left  = texture_start + s_index        + columns * (t_index + 1);
            Vec4 const * top_right    = texture_start + (s_index + 1)  + columns * t_index;
            Vec4 const * bottom_right = texture_start + (s_index + 1)  + columns * (t_index + 1);

            float u  = s_frac;
            float up = 1. - s_frac;
            float v  = t_frac;
            float vp = 1. - t_frac;

            Vec4 out  =  up * vp * *top_left;
            out       += up * v  * *bottom_left;
            out       += u  * vp * *top_right;
            out       += u  * v  * *bottom_right;

            return *reinterpret_cast<Sample*>(&out);
        }
    ''')

def texture_loop_template():
    lines = split_and_dedent_lines(r'''
        #include "Vec.hpp"
        #include <cmath>

        struct Sample {
            float R, G, B, A;
        };

        typedef Vec4 Position;

        struct MeshPoint {
            Position position;
            Sample sample;
        };

        Sample black = { 0.0, 0., 0., 1. };

        Vec4 const & cast(Sample const & sample) {
            return reinterpret_cast<Vec4 const &>(sample);
        }

        Sample const & cast(Vec4 const & vec) {
            return reinterpret_cast<Sample const &>(vec);
        }

        {SAMPLE_TEXTURE}

        Vec4 lower_left  (64, 64, 1, 1);
        Vec4 upper_left  (127,256, 1, 1);
        Vec4 lower_right (256, 127, 1, 1);
        Vec4 upper_right (496, 496, 1, 1);

        Position surface(float u, float v) {
            Vec4 low = (1 - u) * lower_left + u * lower_right,
                high = (1 - u) * upper_left + u * upper_right;
            return (1 - v) * low + v * high;
        }

        extern "C" {
            void generate_mesh(
                MeshPoint * mesh,
                int mesh_width, int mesh_height,
                Sample const * texture,
                int texture_width, int texture_height
            )
            {
                for (int j = 0; j < mesh_height; ++j) {
                    float t = static_cast<float>(j) / static_cast<float>(mesh_width - 1);

                    for (int i = 0; i < mesh_width; ++i) {
                        float s = static_cast<float>(i) / static_cast<float>(mesh_height - 1);

                        MeshPoint * out = mesh + j * mesh_width + i;

                        out->position = surface(s, t);

                        out->sample
                            = sample_texture(&cast(*texture), texture_width, texture_height, s, t);
                    }
                }
            }
        }
    ''')

    replacement_map = {
        'SAMPLE_TEXTURE' : sample_texture_template()
    }

    return transform_lines(lines, replacement_map)


@profile
def load_sampler_lib():
    from phillip.build import build_so
    import ctypes
    from ctypes import c_void_p, c_int

    source_path = '007/shader.cpp'

    with open(source_path, 'w') as out:
        render_indents(out, texture_loop_template())

    extension_args = {
        'include_dirs' : [ find_handsome_include_dir() ],
        'extra_compile_args' : [ '-std=c++11' ],
    }

    so_path = build_so(
        '__main__.shader', os.path.abspath('./007'), [ source_path ],
        extension_args = extension_args,
    )

    lib = ctypes.cdll.LoadLibrary(so_path)

    out = { }

    out['generate_mesh'] = lib['generate_mesh']
    out['generate_mesh'].argtypes = (c_void_p, c_int, c_int, c_void_p, c_int, c_int)

    return out


def find_handsome_include_dir():
    import handsome

    handsome_dir, _ = os.path.split(handsome.__file__)

    cpp_dir = os.path.join(handsome_dir, '..', 'src', 'cpp')
    cpp_dir = os.path.abspath(cpp_dir)

    return cpp_dir

if __name__ == '__main__':
    # load_sampler_lib()
    main()
