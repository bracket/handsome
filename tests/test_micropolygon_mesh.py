from handsome.MicropolygonMesh import MicropolygonMesh, Position
import numpy as np

def generate_test_mesh():
    margin = 16
    width = 128
    right  = 512
    top    = 512

    buffer = np.array(
        [
            [
                (right - margin - width, top - margin, 1, 2 ),
                (right - margin        , top - margin, 2, 1 )
            ],
            [
                (margin        , margin, 2, 3, ),
                (margin + width, margin, 2, 2, )
            ],
        ],
        dtype=Position
    )

    mesh = MicropolygonMesh((1,1))
    mesh.buffer[:,:]['position'] = buffer

    return mesh


#TODO: Finish this test
def test_bounds():
    mesh = MicropolygonMesh((1, 2))

    mesh.buffer[:,:]['position'] = np.array(
        [
            [
                (2, 2, 1, 1),
                (3, 2, 1, 1),
                (4, 2, 1, 1)
            ],
            [
                (1, 1, 1, 1),
                (2, 1, 1, 1),
                (3, 1, 1, 1),
            ]
        ],
        dtype=Position
    )

    assert mesh.bounds is not None

    print(mesh.bounds)
