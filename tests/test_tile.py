from handsome.Tile import Tile
from handsome.Interval import Interval

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
