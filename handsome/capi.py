__all__ = [
    'downsample_tile',
    'fill_micropolygon_mesh',
    'fill_bounds_buffer',
    'generate_numpy_begin',
    'generate_numpy_span',
    'Rectangle',
    'print_coordinates',
    'print_vertices',
]

import os
import ctypes
import functools
import sys

from pathlib import Path

memoize = functools.lru_cache()

@memoize
def build_capi_lib():
    from phillip.build import build_so, generate_extension_args, load_library

    here = Path(__file__).parent

    sources = list(map(str, [
        here / '_capi.cpp',
        here / 'cpp_src' / 'RationalBilinearInverter.cpp',
    ]))

    extension_args = generate_extension_args(DLL_FUNCS)

    if sys.platform in ('linux', 'linux2', 'darwin'):
        extension_args['extra_compile_args'] = [ '-std=c++11' ]
    elif sys.platform in ('win32'):
        extension_args['extra_compile_args'] = [ '/std:c++14' ]

    extension_args['include_dirs'] = [ str(here / 'cpp_src') ]

    so_path = build_so(
        'handsome_capi', str(here),
        sources, extension_args
    )

    return load_library(so_path)


class c_void_p(ctypes.c_void_p):
    pass

NULL_PTR = ctypes.c_void_p(0)

def generate_numpy_begin(array):
    return c_void_p(array.ctypes.data)

def generate_numpy_span(array):
    from functools import reduce
    from operator import mul

    begin = generate_numpy_begin(array)
    item_length = reduce(mul, array.shape)

    byte_length = item_length * array.itemsize
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
    'downsample_tile',
    'fill_micropolygon_mesh',
    'fill_bounds_buffer',
    'print_coordinates',
    'print_vertices',
]

def update_globals():
    lib = build_capi_lib()

    functions = {
        name : lib[name] for name in DLL_FUNCS
    }

    functions['fill_bounds_buffer'].restype = Rectangle

    globals().update(functions)

update_globals()
