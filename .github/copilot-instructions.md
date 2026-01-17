# Copilot Instructions for Handsome

## Project Overview

Handsome is a "two and a half" dimensional rasterizer for 2D and 3D image primitives, built with Python, C++, and OpenCL. It implements a REYES-inspired rendering algorithm (similar to Pixar's RenderMan) using micropolygon meshes for efficient rasterization.

**Key architectural components:**
- **Python frontend**: Core API using NumPy for vectorized operations and data management
- **C++ backend**: Performance-critical rendering routines compiled on-the-fly via ctypes
- **OpenCL implementation**: GPU-accelerated sample implementation (partially tested)
- **Git submodules**: phillip (C++ build system) and sweatervest (scene graph language)

## Repository Structure

```
handsome/
├── handsome/              # Main Python package
│   ├── __init__.py       # Package exports
│   ├── Micropolygon.py   # Single bilinear quad primitive
│   ├── MicropolygonMesh.py  # Grid of micropolygons
│   ├── Tile.py           # Image tile management
│   ├── TileCache.py      # Tile caching system
│   ├── capi.py           # ctypes interface to C++ backend
│   ├── _capi.cpp         # C wrapper for C++ functions
│   ├── opencl_api.py     # OpenCL interface
│   ├── Scene/            # Scene graph implementation (uses sweatervest)
│   ├── cpp_src/          # C++ source files
│   │   ├── RationalBilinearInverter.cpp/.hpp  # Core sampling algorithm
│   │   ├── Micropolygon.hpp
│   │   ├── MicropolygonMesh.hpp
│   │   └── [other C++ headers and sources]
│   └── opencl_src/
│       └── opencl_api.cl # OpenCL kernel implementation
├── examples/             # Working example scripts (001-010)
├── tests/                # Test suite
├── external/             # Git submodules
│   ├── phillip/          # C++ on-the-fly compilation system
│   └── sweatervest/      # JSON/YAML scene graph language
├── setup.py              # Package installation
└── requirements.txt      # Python dependencies
```

## Multi-Language Architecture

### Python Layer
- Uses NumPy extensively for array operations and memory management
- Defines structured dtypes for vertices (Position, Vertex, FloatPixel)
- Main entry point for users via classes like `Tile`, `TileCache`, `MicropolygonMesh`
- Handles high-level rendering pipeline and compositing

### C++ Backend Integration
- C++ code is compiled **on-the-fly** at first import using the phillip submodule
- Integration via ctypes: `handsome/capi.py` loads compiled shared library
- C++ functions are wrapped with extern "C" in `_capi.cpp`
- Phillip generates extension arguments and builds .so/.dll files dynamically
- C++ handles performance-critical operations: rational bilinear inversion, sample buffer filling

**Key ctypes pattern in capi.py:**
```python
@memoize
def build_capi_lib():
    from phillip.build import build_so, generate_extension_args, load_library
    sources = [here / '_capi.cpp', here / 'cpp_src' / 'RationalBilinearInverter.cpp']
    extension_args = generate_extension_args(DLL_FUNCS)
    so_path = build_so('handsome_capi', str(here), sources, extension_args)
    return load_library(so_path)
```

### OpenCL Implementation
- Located in `handsome/opencl_src/opencl_api.cl`
- Implements `fill_micropolygon_mesh` kernel for GPU acceleration
- Partially tested; not required for basic functionality
- Uses float4 types for vertices, positions, and pixels

## Core Concepts

### Micropolygons
A micropolygon is a bilinearly-interpolated quadrilateral in 4D projective space (x, y, z, w) with arbitrary vertex attributes (color, texture coordinates, etc.). Each micropolygon:
- Has 4 vertices defining corners in projective space
- Supports bilinear interpolation: P(u,v) = lerp in u, then lerp in v
- Can be inverted: given (x, y), solve for (u, v) using rational bilinear inversion
- Typical size: approximately 1 pixel after projection

### Rational Bilinear Inversion
The core algorithm in `RationalBilinearInverter.cpp` solves the inverse problem:
- Given: Point p(x, y) and bilinear patch corners in projective space
- Find: Parametric coordinates (u, v) such that the patch evaluates to p
- Method: Reduces to solving a quadratic equation after projective division
- Returns 0-2 solutions (quadrilateral may have 0, 1, or 2 intersections with a point)

### REYES-Inspired Pipeline
1. **Subdivision**: Complex surfaces subdivided into micropolygon meshes
2. **Projection**: Micropolygons transformed to screen space
3. **Sampling**: For each sample point in tile, find covering micropolygons using inversion
4. **Shading**: Interpolate attributes at sample points
5. **Filtering**: Downsample to final pixels

## Working with Git Submodules

### phillip (C++ Build System)
- Located in `external/phillip/`
- Provides `build_so()`, `generate_extension_args()`, `load_library()` functions
- Handles cross-platform compilation (Linux, macOS, Windows)
- **Do not modify phillip directly**; treat as external dependency
- Changes to C++ source files will trigger recompilation on next import

### sweatervest (Scene Graph)
- Located in `external/sweatervest/`
- JSON/YAML-based scene description language
- Used by `handsome/Scene/__init__.py` for scene rendering
- Example scene files in `examples/data/*.yaml`
- **Do not modify sweatervest directly**; treat as external dependency

### Initializing Submodules
Always initialize submodules after cloning:
```bash
git submodule update --init --recursive
```

## Development Workflow

### Setup and Installation
```bash
# Clone with submodules
git clone --recursive https://github.com/bracket/handsome.git

# Or initialize submodules if already cloned
git submodule update --init --recursive

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### Building and Testing
```bash
# C++ compilation happens automatically on first import
python3 -c "import handsome"

# Run tests (if test framework available)
python3 -m pytest tests/

# Run examples
python3 examples/001_tile.py
```

### Making Changes

**Python changes:**
- Edit Python files directly
- Follow NumPy structured dtype conventions for vertices
- Use existing Pixel types: `Pixel`, `FloatPixel`
- Maintain compatibility with ctypes interface

**C++ changes:**
1. Edit files in `handsome/cpp_src/`
2. Update function signatures in `_capi.cpp` if needed
3. Update `DLL_FUNCS` in `capi.py` if adding new functions
4. Delete cached compiled libraries to force rebuild: remove `*.so`/`*.dll` files
5. Test by importing handsome: `python3 -c "import handsome"`

**OpenCL changes:**
- Edit `handsome/opencl_src/opencl_api.cl`
- Update `opencl_api.py` if kernel signatures change
- Test with `examples/009_open_cl.py` (if functional)

## Common Patterns

### NumPy Structured Arrays
```python
# Vertex type definition
Position = np.dtype([
    ('x', np.float32), ('y', np.float32),
    ('z', np.float32), ('w', np.float32)
], align=True)

Vertex = np.dtype([
    ('position', Position),
    ('color', FloatPixel)
], align=True)

# Creating mesh buffer
mesh_buffer = np.zeros(shape=(rows, cols), dtype=Vertex)
```

### Passing NumPy Arrays to C++
```python
# Use generate_numpy_begin() to get pointer
ptr = generate_numpy_begin(numpy_array)
c_function(ptr, rows, cols)
```

### Working with Tiles
```python
from handsome import Tile, Pixel
tile = Tile((0, 0), (width, height), dtype=Pixel)
tile.buffer[:, :] = color_value  # NumPy array indexing
```

## Anti-Patterns to Avoid

1. **Don't modify submodule contents** - phillip and sweatervest are external dependencies
2. **Don't bypass ctypes interface** - always use capi.py functions, not direct C++ calls
3. **Don't ignore alignment** - use `align=True` in NumPy dtypes for C++ compatibility
4. **Don't assume cached builds** - C++ changes require clearing cached .so/.dll files
5. **Don't mix pixel types** - use consistent Pixel or FloatPixel throughout a pipeline
6. **Don't modify files in `one-times/`** - these are deprecated test scripts

## Testing and Validation

- Test suite located in `tests/` directory
- Working examples in `examples/` (001-010) serve as integration tests
- Example 009 tests OpenCL functionality (may not be fully functional)
- After changes, run relevant example scripts to verify rendering output
- Check generated images in `examples/render/` directory

## Conventions

- **Import style**: Import from handsome package root: `from handsome import Tile, Micropolygon`
- **Coordinate systems**: Screen space uses NumPy convention (row, column) = (y, x)
- **Projective space**: 4D homogeneous coordinates (x, y, z, w) throughout
- **C++ standard**: C++11 on Linux/macOS, C++14 on Windows
- **File extensions**: Use `.hpp` for C++ headers, `.cpp` for implementation
- **Example naming**: Numbered examples with descriptive names (e.g., `003_circle.py`)

## Additional Notes

- The `one-times/` directory contains non-functional historical test scripts - ignore these
- Examples 006, 007, 008 have subdirectories with additional files
- Victor project (GUI tool) is mentioned but not yet implemented
- OpenCL implementation is experimental and not required for core functionality
