"""
handsome: Rasterizer for 2D and 3D image primitives based off of NumPy
"""

from setuptools import setup, Extension

import os
import re

version_re = re.compile(r"^__version__ = ['\"](?P<version>[^'\"]*)['\"]", re.M)

def find_version(*file_paths):
    """Get version from python file."""

    path = os.path.join(os.path.dirname(__file__), *file_paths)
    with open(path) as version_file: contents = version_file.read()

    m = version_re.search(contents)
    if not m: raise RuntimeError("Unable to find version string.")

    return m.group('version')

HERE = os.path.abspath(os.path.dirname(__file__))

def fmt_here(string):
    return string.format(HERE=HERE)

capi = Extension(
    'handsome/_capi',

    include_dirs = [ fmt_here('{HERE}/src/cpp') ],

    sources = list(map(fmt_here, [
        '{HERE}/handsome/_capi.cpp',
        '{HERE}/src/cpp/RationalBilinearInverter.cpp',
    ])),
    
    extra_compile_args = [ '-std=c++11' ],
)

setup(
    name='handsome',
    version=find_version('handsome/__init__.py'),
    author='Stephen [Bracket] McCray',
    author_email='mcbracket@gmail.com',
    packages=['handsome'],
    classifiers=[
        'Development Status :: 4 - Beta'
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    ext_modules = [ capi ]
)
