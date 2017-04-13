import numpy as np
import pyopencl as cl

from handsome.Pixel import FloatPixel, array_view, pixel_view
from handsome.TileCache import TileCache
from handsome.Tile import Tile
from handsome.MicropolygonMesh import MicropolygonMesh, Vertex
from handsome.util import point


def main():
    from handsome.opencl_api import fill_micropolygon_mesh
    from handsome.util import save_array_as_image, parse_color

    mesh = generate_mesh()
    tile = Tile((0, 0), (512, 512), 4, dtype=FloatPixel)

    fill_micropolygon_mesh(mesh, tile)

    buffer = array_view(tile.downsample(1))
    # buffer = array_view(tile.buffer)
    buffer = np.clip(buffer, 0., 1.)
    buffer = (255 * buffer).astype(np.uint8)

    save_array_as_image(pixel_view(buffer), 'render/009_opencl.tiff', 'RGBA')


def generate_mesh():
    mesh = MicropolygonMesh((1, 1))

    half = 512 / 2

    center = point(half, half, 1, 1)
    right  = point((1/2) * half, (1/6) * half, 0., 0)
    up     = point(0, 3/4 * half, 0, 0)


    points = [
        [ point(5, 10, 1, 1),  point(20, 20, 1, 1) ],
        [ point(0, 0, 1, 1),   point(10, 0,  1, 1) ],
    ]

    points = [
        [ point(80, 160, 1, 1),  point(320, 320, 1, 1) ],
        [ point(0, 0, 1, 1),     point(160, 0,  1, 1) ],
    ]

    points = [
        [ center + up - right,   center + (up + right) ],
        [ center - (up + right), center - up + 1.5 * right ],
    ]

    colors = [
        [ point(1, 0, 0, 1), point(1, 0, 1, 1) ],
        [ point(0, 0, 0, 1), point(0, 0, 1, 1) ]
    ]

    mesh.buffer[:,:]['position'] = points
    mesh.buffer[:,:]['color']    = colors

    return mesh


def test_open_cl():
    from handsome.util import save_array_as_image, parse_color
    from handsome.Scene import make_canvas

    canvas = make_canvas({
        'extents' : (640, 480),
        'color'   : '#fff',
    })

    context = cl.create_some_context()
    queue = cl.CommandQueue(context)

    mf = cl.mem_flags

    source = r'''
        __kernel void shade_square(
            __global float4 * result_g
        )
        {
            int y = get_global_id(0),
                height = get_global_size(0);

            int x = get_global_id(1),
                width = get_global_size(1);

            int index = y * width + x;

            const float2  center = (float2)(width / 2, height / 2),
                dimensions = (float2)(height) / 2,
                upper_left = center - dimensions / 2;

            float x_blend = ((float)x - upper_left.x) / dimensions.x,
                y_blend = ((float)y - upper_left.y) / dimensions.y
            ;
            
            float4 upper_left_c = (float4)(1, 1, 1, 1),
                upper_right_c = (float4)(1, 0, 0, 1),
                lower_left_c = (float4)(0, 0, 1, 1),
                lower_right_c = (float4)(0, 0, 0, 1)
            ;

            if (0. <= x_blend && x_blend <= 1. && 0. <= y_blend && y_blend <= 1.) {
                result_g[index]
                    = (1 - x_blend) * (1 - y_blend) * upper_left_c
                    + x_blend * (1 - y_blend)  * upper_right_c
                    + (1 - x_blend) * y_blend * lower_left_c
                    + x_blend * y_blend * lower_right_c
                ;
            }
            else{
                result_g[index] = (float4)(0, 0, 0, 1);
            }
        }
    '''

    program = cl.Program(context, source).build()

    result = cl.Buffer(context, mf.WRITE_ONLY, canvas.buffer.nbytes)
    program.shade_square(queue, canvas.buffer.shape, None, result)

    cl.enqueue_copy(queue, array_view(canvas.buffer), result)

    buffer = array_view(canvas.downsample(1))
    buffer = np.clip(buffer, 0., 1.)
    buffer = (255 * buffer).astype(np.uint8)

    save_array_as_image(pixel_view(buffer), 'render/009_opencl.tiff', 'RGBA')


if __name__ == '__main__':
    main()
