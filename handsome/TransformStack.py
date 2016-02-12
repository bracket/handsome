import contextlib
import numpy as np

class TransformStack(object):
    def __init__(self):
        self.stack = [ np.eye(4, 4, dtype=np.float32) ]


    @contextlib.contextmanager
    def __call__(self, xform):
        self.push(xform)
        yield self
        self.pop()


    def push(self, xform):
        stack = self.stack

        if xform is None:
            stack.append(stack[-1])
        else:
            stack.append(stack[-1].dot(xform))


    def pop(self):
        self.stack.pop()


    def dot(self, A):
        return self.stack[-1].dot(A)
