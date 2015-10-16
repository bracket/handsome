from handsome.Coordinate import Coordinate
from handsome.Interval import Interval
from handsome.Tile import Tile

import numpy as np

def test_tile():
    tile = Tile((0, 0), (100, 200))

    assert tile.origin == (0, 0)
    assert tile.shape == (100, 200)
    assert tile.horizontal == Interval(0, 100)
    assert tile.vertical == Interval(0, 200)

    tile.set_origin((25, 50))

    assert tile.origin == (25, 50)
    assert tile.shape == (100, 200)
    assert tile.horizontal == Interval(25, 125)
    assert tile.vertical == Interval(50, 250)

def test_coordinate_image():
    tile = Tile((1, 2), (2, 3))
    actual = tile.coordinate_image

    expected = np.array([
        [ (1, 4), (2, 4) ],
        [ (1, 3), (2, 3) ],
        [ (1, 2), (2, 2) ],
    ], dtype=Coordinate).T

    np.testing.assert_array_equal(expected, actual)
