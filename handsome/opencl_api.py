__all__ = [
    'fill_micropolygon_mesh'
]


from pathlib import Path
from .util import memoize

import numpy as np
import pyopencl as cl


def fill_micropolygon_mesh(mesh, tile):
    from .capi import generate_numpy_begin, print_vertices

    rows, columns = mesh.buffer.shape
    buffer_ptr = generate_numpy_begin(mesh.buffer)

    print_vertices(buffer_ptr, rows * columns)

    
    mf = cl.mem_flags

    context = cl_context()
    queue = cl_queue()

    mesh_buffer_g = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=mesh.buffer)
    mesh_bounds_g = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=mesh.bounds)
    coordinate_g  = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=tile.coordinate_image)

    tile_g = cl.Buffer(context, mf.WRITE_ONLY, tile.buffer.nbytes)

    program = cl_program()

    mesh_rows, mesh_columns = mesh.buffer.shape

    kernel = program.fill_micropolygon_mesh
    kernel.set_scalar_arg_dtypes([ None, None, np.int32, np.int32, None, None ])

    kernel(queue, tile.buffer.shape, None,
       mesh_buffer_g, mesh_bounds_g,
       mesh_rows, mesh_columns,
       coordinate_g, tile_g
    );

    cl.enqueue_copy(queue, tile.buffer, tile_g)


@memoize
def cl_context():
    return cl.create_some_context()


@memoize
def cl_queue():
    return cl.CommandQueue(cl_context())


@memoize
def cl_program():
    here = Path(__file__).parent

    source_path = here / 'opencl_src'  / 'opencl_api.cl'
    with source_path.open() as fd:
        source = fd.read()

    program = cl.Program(cl_context(), source).build()

    return program
