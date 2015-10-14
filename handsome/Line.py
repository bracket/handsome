__all__ =  [ 'Line' ]

class Line:
    def __init__(self, start, end):
        self.start = start
        self.end   = end

    def __call__(self, value):
        return (1. - value) * self.start + value * self.end

    @property
    def direction(self):
        return self.end - self.start

    def __repr__(self):
        return 'Line(start={}, end={})'.format(self.start, self.end)
