import os

os.environ['PYOPENCL_CTX'] = '0:0'
os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'

def _test_build_program():
    from handsome import opencl_api
    program = opencl_api.build_cl_program()

    assert program
