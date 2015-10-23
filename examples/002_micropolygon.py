from handsome.Line import Line
from handsome.MicropolygonMesh import MicropolygonMesh, Vertex
from handsome.Pixel import Pixel, FloatPixel, array_view, pixel_view
from handsome.Tile import Tile
from handsome.util import point, save_array_as_image, parse_color
import numpy as np

from handsome.capi import fill_micropolygon_mesh, generate_numpy_begin

def main():
    colors = {
        'red'   : '#f00',
        'white' : '#fff',
    }

    float_colors = { }

    for key, value in colors.items():
        color = parse_color(value)
        colors[key] = np.array([ color ], dtype=Pixel)
        float_colors[key] = np.array(tuple(c / 255. for c in color), dtype=FloatPixel)

    image = Tile((0, 0), (512, 512), sample_rate = 4, dtype=FloatPixel)
    image.buffer[:,:] = float_colors['white']

    tile_width, tile_height = image.buffer.shape

    mesh = MicropolygonMesh((1,1))
    mesh_width, mesh_height = mesh.buffer.shape

    buffer = np.array([
            [ (384, 496, 1, 1, 2 , 0, 0, 1), (496, 496, 1, 1, 0, 0, 0, 1) ],
            [ (16 , 16 , 1, 1, .5, 0, 0, 1), (128, 16 , 1, 1, 0, 0, 0, 1) ],
        ],
        dtype=np.float32
    )

    mesh.buffer.view(dtype=(np.float32, 8))[:] = buffer

    fill_micropolygon_mesh(
        mesh_width, mesh_height,
        generate_numpy_begin(mesh.buffer),
        tile_width, tile_height,
        generate_numpy_begin(image.coordinate_image),
        generate_numpy_begin(image.buffer)
    )

    buffer = array_view(image.downsample(1))
    buffer = np.clip(buffer, 0., 1.)
    buffer = (255. * buffer).astype(dtype=np.uint8)

    save_array_as_image(pixel_view(buffer), 'render/002_micropolygon.tiff', 'RGBA')

if __name__ == '__main__':
    main()
