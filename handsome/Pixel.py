__all__ = [ 'pixel_type', 'Pixel', 'FloatPixel' ]

import numpy as np

def pixel_type(dtype):
    return np.dtype(
        [
            ('R', dtype),
            ('G', dtype),
            ('B', dtype),
            ('A', dtype),
        ],
        align=True
    )


Pixel      = pixel_type(np.uint8)
FloatPixel = pixel_type(np.float32)
HalfPixel  = pixel_type(np.float16)
