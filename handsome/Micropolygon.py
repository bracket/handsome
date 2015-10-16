import numpy as np

class Micropolygon:
    def __init__(self, bottom_left, bottom_right, upper_left, upper_right):
        self.points = [
            [ bottom_left,  upper_left  ],
            [ bottom_right, upper_right ],
        ]

    def __call__(self, u, v):
        u_inverse = (1. - u)

        bottom = u_inverse * self.points[0][0] + u * self.points[1][0]
        top    = u_inverse * self.points[0][1] + u * self.points[1][1]

        return (1. - v) * bottom + v * top

    def inverse_solve(self, x, y, dtype=np.float32):
        points = self.points

        A = np.array([
            points[0][0],
            points[1][0],
            points[0][1],
            [ -x, -y, -1, 0 ],
        ], dtype=dtype).T

        b = np.array([
            [ 0, 0, 0, 1],
            -points[1][1],
        ], dtype=dtype).T

        x = np.linalg.solve(A, b)

        polynomial = [
            x[0,1] - x[1,1] * x[2,1],
            x[0,0] - x[1,0] * x[2,0] - x[1,1] * x[2,0],
            x[1,0] * x[2,0]
        ]

        roots = np.roots(polynomial)
        out = [ ]

        for D in roots:
            A, B, C, alpha = [ x[i][0] + x[i][1] * D for i in range(4) ]
            if alpha < 1.0: continue

            d = A + B + C + D


            u = (B + D) / d
            v = (C + D) / d

            if (u < 0. or 1. < u): continue
            if (v < 0. or 1. < v): continue
            out += [ (u, v) ]

        return out
