__all__ = [ 'Interval' ]

class Interval(object):
    '''Interval - Arbitrary half-closed interval of the form [start, end)'''

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __call__(self, value):
        return (1. - value) * self.start + value * self.end

    def __str__(self):
        return 'Interval({self.start}, {self.end})'.format(self=self)

    def __repr__(self):
        return 'Interval({self.start}, {self.end})'.format(self=self)

    def __eq__(self, right):
        return self.start == right.start and self.end == right.end

    def contains(self, value):
        return self.start <= value < self.end

    def __intersection(self, right):
        return (
            max(self.start, right.start),
            min(self.end, right.end)
        )

    def overlaps(self, other):
        start, end = self.__intersection(other)
        return start < end

    def intersection(self, other):
        start, end = self.__intersection(other)

        if start < end: return Interval(start, end)
        else: return None
