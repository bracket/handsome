from handsome.Line import Line
import numpy as np

def test_line():
    test_inputs  = [ 0.0, .25, .5, .75, 1., 1.25 ]

    test_lines = [
       [ Line(1, 3),  [ 1, 1.5, 2, 2.5, 3, 3.5 ] ],
       [ Line(
            np.array([1., 1.]),
            np.array([2., 3.]),
         ),
         list(map(np.array, [
            [ 1.,   1.  ],
            [ 1.25, 1.5 ],
            [ 1.5,  2,  ],
            [ 1.75, 2.5 ],
         ]))
       ]
    ]

    for line, expecteds in test_lines:
        for input, expected in zip(test_inputs, expecteds):
            if isinstance(expected, np.ndarray):
                assert (line(input) == expected).all()
            else:
                assert line(input) == expected
