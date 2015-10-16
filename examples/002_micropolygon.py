from handsome.Line import Line
from handsome.Micropolygon import Micropolygon
from handsome.Pixel import Pixel, FloatPixel
from handsome.Tile import Tile
from handsome.util import point, save_array_as_image, parse_color
import numpy as np

from handsome.capi import fill, generate_numpy_begin

def main():
    colors = {
        'red'   : '#f00',
        'white' : '#fff',
    }

    for key, value in colors.items():
        colors[key] = np.array([ parse_color(value) ], dtype=Pixel)

    image = Tile((0, 0), (512, 512), dtype=Pixel)
    image.buffer[:,:]    = colors['white']

    m = Micropolygon(
        point(16,   16),
        point(128, 16),
        point(512 - 128, 512 - 16),
        point(512 - 16, 512 - 16),
    )

    buffer = image.buffer
    coordinate_image = image.coordinate_image

    blue = parse_color('#00f')

    width, height = image.shape
    for i in range(width):
        for j in range(height):
            coordinate = coordinate_image[i, j]
            if m.inverse_solve(coordinate['x'], coordinate['y']):
                buffer[i,j] = blue

    fill(
        generate_numpy_begin(m.points[0][0]),
        generate_numpy_begin(m.points[0][1]),
        generate_numpy_begin(m.points[1][0]),
        generate_numpy_begin(m.points[1][1]),
        width, height,
        generate_numpy_begin(coordinate_image),
        generate_numpy_begin(image.buffer)
    )

    save_array_as_image(image.buffer, 'render/002_micropolygon.tiff', 'RGBA')

if __name__ == '__main__':
    main()
