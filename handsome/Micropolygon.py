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
