__all__ = [
    'fill_micropolygon_mesh',
    'fill_bounds_buffer',
    'generate_numpy_begin',
    'generate_numpy_span',
    'Rectangle',
]

import os
import ctypes

def load_library():
    dir_path = os.path.dirname(__file__)

    for ext in ('so', 'dll', 'pyd', 'dylib'):
        try:
            full_path = os.path.join(dir_path, '_capi.' + ext)
            lib = ctypes.cdll.LoadLibrary(full_path)
            return lib
        except OSError as e:
            continue

class c_void_p(ctypes.c_void_p):
    pass

NULL_PTR = ctypes.c_void_p(0)

def generate_numpy_begin(array):
    return c_void_p(array.ctypes.data)

def generate_numpy_span(array):
    begin = generate_numpy_begin(array)
    byte_length = len(array) * array.itemsize
    end = c_void_p(begin.value + byte_length)
    return begin, end

class Rectangle(ctypes.Structure):
    _fields_ = [
        ('left'  , ctypes.c_float),
        ('bottom', ctypes.c_float),
        ('right' , ctypes.c_float),
        ('top'   , ctypes.c_float),
    ]

    def __unicode__(self):
        return 'Rectangle(left={}, bottom={}, right={}, top={})'.format(
            self.left, self.bottom, self.right, self.top
        )

    def __repr__(self):
        return 'Rectangle(left={}, bottom={}, right={}, top={})'.format(
            self.left, self.bottom, self.right, self.top
        )


DLL_FUNCS = [
    'fill_micropolygon_mesh',
    'fill_bounds_buffer',
]

def update_globals():
    lib = load_library()

    functions = {
        name : lib[name] for name in DLL_FUNCS
    }

    functions['fill_bounds_buffer'].restype = Rectangle

    globals().update(functions)

update_globals()
