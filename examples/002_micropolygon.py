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
        # value = tuple(c / 255. for  c in parse_color(value))
        # colors[key] = np.array([ value ], dtype=FloatPixel)
        colors[key] = np.array([ parse_color(value) ], dtype=Pixel)

    image = Tile((0, 0), (512, 512), dtype=Pixel)
    image.buffer[:,:]    = colors['white']
    # image.buffer[128:,:] = colors['red']

    m = Micropolygon(
        point(0,   0),
        point(0, 256),
        point(512, 256),
        point(512, 512),
    )

    # abscissae = [ (0, 0), (1, 0), (1, 1), (0, 1), ]
    # ordinates = [ m(*p) for p in abscissae ]

    # lines =  [ Line(start, end) for start, end in zip(ordinates, ordinates[1:]) ]
    # lines.append(Line(ordinates[-1], ordinates[0]))

    # for line in lines:
    #     print(line)

    # for p in image.coordinate_image:
    #     print(p)

    width, height = image.shape

    fill(
        generate_numpy_begin(m.points[0][0]),
        generate_numpy_begin(m.points[0][1]),
        generate_numpy_begin(m.points[1][0]),
        generate_numpy_begin(m.points[1][1]),
        width, height,
        generate_numpy_begin(image.coordinate_image),
        generate_numpy_begin(image.buffer)
    )

    save_array_as_image(image.buffer, 'render/002_micropolygon.tiff', 'RGBA')

if __name__ == '__main__':
    main()
