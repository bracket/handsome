from handsome.Micropolygon import Micropolygon
from handsome.util import point
import numpy as np

def test_micropolygon():
    m = Micropolygon(
        point(0, 0),
        point(1, 0),
        point(1, 1),
        point(2, 1),
    )

    tests = [
        [ (.5, .5),   np.array([ 1, .5, 1  ]), ],
        [ (.25, .75), np.array([ 1, .75, 1 ]), ],
        [ (0., 0.),   np.array([ 0,   0, 1 ]), ],
        [ (1., 0.),   np.array([ 1,   0, 1 ]), ],
        [ (0., 1.),   np.array([ 1,   1, 1 ]), ],
        [ (1., 1.),   np.array([ 2,   1, 1 ]), ],
    ]

    for input, expected in tests:
        actual = m(*input)
        assert (expected == actual).all()
