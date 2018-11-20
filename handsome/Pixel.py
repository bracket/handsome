__all__ = [ 'pixel_type', 'Pixel', 'FloatPixel', 'HalfPixel', 'array_view', 'pixel_view' ]

import numpy as np

pixel_to_array = { }
array_to_pixel = { }

def pixel_type(dtype):
    array_type = np.dtype((dtype, 4))

    pixel_type = np.dtype(
        [
            ('R', dtype),
            ('G', dtype),
            ('B', dtype),
            ('A', dtype),
        ],
        align=True
    )

    pixel_to_array[pixel_type] = array_type
    array_to_pixel[np.dtype(dtype)] = pixel_type

    return pixel_type


Pixel      = pixel_type(np.uint8)
FloatPixel = pixel_type(np.float32)
HalfPixel  = pixel_type(np.float16)


def array_view(pixels):
    return pixels.view(pixel_to_array[pixels.dtype])


def pixel_view(array):
    # TODO: Double check the shape
    out = array.view(dtype=array_to_pixel[array.dtype])
    return np.squeeze(out)
