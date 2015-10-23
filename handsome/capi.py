__all__ = [
    'fill_micropolygon_mesh',
    'generate_numpy_begin',
    'generate_numpy_span',
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

DLL_FUNCS = [
    'fill_micropolygon_mesh',
]

def update_globals():
    lib = load_library()
    globals().update({ name : lib[name] for name in DLL_FUNCS })

update_globals()
