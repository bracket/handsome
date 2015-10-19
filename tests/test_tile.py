from handsome.Coordinate import Coordinate
from handsome.Interval import Interval
from handsome.Tile import Tile
from handsome.Pixel import FloatPixel, array_view

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

def test_coordinate_image_sample_rate():
    tile = Tile((0, 0), (3, 2), sample_rate = 2)
    actual = tile.coordinate_image

    expected = np.array([
        [ (0., 1.5), (.5, 1.5), (1., 1.5), (1.5, 1.5), (2., 1.5), (2.5, 1.5), ],
        [ (0., 1.) , (.5, 1.) , (1., 1.) , (1.5, 1.) , (2., 1.) , (2.5, 1.) , ],
        [ (0., .5) , (.5, .5) , (1., .5) , (1.5, .5) , (2., .5) , (2.5, .5) , ],
        [ (0., 0.) , (.5, 0.) , (1., 0.) , (1.5, 0.) , (2., 0.) , (2.5, 0.) , ],
    ], dtype=Coordinate).T

    np.testing.assert_array_equal(expected, actual)

def test_downsample():
    tile = Tile((0, 0), (2,2), dtype=FloatPixel, sample_rate=2)

    tile.buffer[:,:]['R'] = tile.coordinate_image['x']
    tile.buffer[:,:]['G'] = tile.coordinate_image['y']

    expected = np.array(
        [
            [ (.25, 1.25, 0, 0.), (1.25, 1.25, 0., 0.) ],
            [ (.25, .25 , 0, 0.), (1.25, .25 , 0., 0.) ],
        ],
        dtype=np.float32
    ).transpose((1, 0, 2))

    actual = tile.downsample(1)
    np.testing.assert_array_equal(expected, array_view(actual))
