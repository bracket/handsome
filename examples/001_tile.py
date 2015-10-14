from handsome.Pixel import Pixel
from handsome.Tile import Tile
from handsome.util import save_array_as_image
import numpy as np

def main():
    colors = {
        'white'  : (255 , 255 , 255 , 255), 
        'red'    : (255 , 0   , 0   , 255), 
        'green'  : (0   , 255 , 0   , 255), 
        'blue'   : (0   , 0   , 255 , 255), 
        'yellow' : (255 , 255 , 000 , 255), 
    }

    for key, value in colors.items():
        colors[key] = np.array([value], dtype=Pixel)


    image = Tile((0, 0), (100, 100), dtype=Pixel)
    image.buffer[:,:] = colors['white']

    image.buffer[:50,:50] = colors['red']    # upper left
    image.buffer[50:,:50] = colors['green']  # upper right
    image.buffer[:50,50:] = colors['blue']   # lower left
    image.buffer[50:,50:] = colors['yellow'] # lower right

    save_array_as_image(image.buffer, 'render/001_tile.tiff', 'RGBA')


if __name__ == '__main__':
    main()
