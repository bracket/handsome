__all__ = [ 'coordinate_type', 'Coordinate' ]

import numpy as np

def coordinate_type(dtype):
    return np.dtype(
        [
            ('x', dtype),
            ('y', dtype),
        ],
        align=True
    )


Coordinate = coordinate_type(np.float32)
# Coordinate = np.dtype((np.float32, 2))
