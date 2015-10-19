from handsome.Line import Line
from handsome.Micropolygon import Micropolygon
from handsome.Pixel import Pixel, FloatPixel, array_view, pixel_view
from handsome.Tile import Tile
from handsome.util import point, save_array_as_image, parse_color
import numpy as np

from handsome.capi import fill_float, generate_numpy_begin

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


    buffer = image.buffer
    coordinate_image = image.coordinate_image

    width, height = buffer.shape

    polygons = [
         Micropolygon(
            point(16,   16),
            point(128, 16),
            point(512 - 128, 512 - 16),
            point(512 - 16, 512 - 16),
        ),
         Micropolygon(
            point(512 - 128, 16),
            point(512 - 16, 16),
            point(16, 512 - 16),
            point(128, 512 - 16),
        )
    ]


    for p in polygons:
        fill_float(
            generate_numpy_begin(p.points[0][0]),
            generate_numpy_begin(p.points[0][1]),
            generate_numpy_begin(p.points[1][0]),
            generate_numpy_begin(p.points[1][1]),
            width, height,
            generate_numpy_begin(coordinate_image),
            generate_numpy_begin(image.buffer)
        )

    buffer = array_view(image.downsample(1))
    buffer = np.clip(buffer, 0., 1.)
    buffer = (255. * buffer).astype(dtype=np.uint8)

    save_array_as_image(pixel_view(buffer), 'render/002_micropolygon.tiff', 'RGBA')

if __name__ == '__main__':
    main()
