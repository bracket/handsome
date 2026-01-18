# Handsome

**A "two and a half" dimensional rasterizer for 2D and 3D image primitives based on NumPy**

Handsome is a Python-based rendering system implementing a REYES-inspired architecture (similar to Pixar's RenderMan) using micropolygon meshes for efficient rasterization. It combines Python's NumPy for high-level operations with C++ for performance-critical rendering routines, all compiled on-the-fly for seamless integration.

## Features

- **Micropolygon rendering**: Bilinearly-interpolated quadrilaterals in projective space
- **REYES-inspired pipeline**: Subdivision, projection, sampling, shading, and filtering
- **Multi-language architecture**: Python frontend with C++ backend for performance
- **On-the-fly compilation**: C++ code compiled dynamically via the phillip system
- **Scene graph support**: JSON/YAML scene descriptions via sweatervest
- **OpenCL acceleration**: Experimental GPU-accelerated rendering (partially tested)
- **Flexible attribute interpolation**: Arbitrary vertex attributes (color, texture, normals, etc.)

## What is the REYES Architecture?

REYES (Renders Everything You Ever Saw) is a rendering architecture developed by Pixar for RenderMan. The key innovation is breaking complex surfaces into tiny "micropolygons" (roughly pixel-sized quadrilaterals) that are simple to render but collectively produce high-quality images.

**Handsome's REYES-inspired pipeline:**

1. **Subdivision**: Complex surfaces are subdivided into grids of micropolygons
2. **Projection**: Micropolygons transformed from object space to screen space
3. **Sampling**: For each sample point in image tiles, determine which micropolygons cover it
4. **Shading**: Interpolate vertex attributes at sample points
5. **Filtering**: Downsample oversampled tiles to final pixel values

This approach excels at:
- Rendering complex curved surfaces efficiently
- Handling motion blur and depth of field naturally
- Providing predictable memory usage through tiling
- Supporting arbitrary surface attributes

## Technical Overview

### Micropolygons

A **micropolygon** is the fundamental primitive in Handsome. Each micropolygon is:
- A bilinearly-interpolated quadrilateral in 4D projective space (x, y, z, w)
- Defined by 4 corner vertices with positions and arbitrary attributes
- Small enough to be approximately planar (roughly pixel-sized after projection)
- Rendered by sampling rather than explicit rasterization

**Bilinear interpolation formula:**
```
P(u, v) = (1-u)(1-v)P₀₀ + u(1-v)P₁₀ + (1-u)vP₀₁ + uvP₁₁
```

Where P₀₀, P₁₀, P₀₁, P₁₁ are the four corner vertices, and (u, v) ∈ [0,1]² are parametric coordinates.

### Rational Bilinear Inversion

The core algorithm enabling efficient micropolygon sampling is **rational bilinear inversion**, implemented in `handsome/cpp_src/RationalBilinearInverter.cpp`.

**The problem:** Given a point p(x, y) in screen space and a bilinear patch in projective space, find the parametric coordinates (u, v) where the patch evaluates to p.

**Why "rational"?** In projective space, we must perform perspective division (divide by w) before comparing 2D positions:
```
screen_x = x/w,  screen_y = y/w
```

This transforms the bilinear interpolation into a rational function, making inversion non-trivial.

**The solution:** The algorithm reduces the inversion to solving a quadratic equation, yielding 0-2 solutions per micropolygon. This allows efficient point-in-micropolygon testing for sampling.

**Applications:**
- Determine which micropolygons cover each sample point
- Enable oversampling for antialiasing
- Support transparent layering and depth sorting

### Architecture Components

**Python Layer** (`handsome/`)
- `Micropolygon.py`: Single bilinear quadrilateral primitive
- `MicropolygonMesh.py`: Grid of connected micropolygons with vertex attributes
- `Tile.py`: Image tile for memory-efficient rendering
- `TileCache.py`: Manages multiple tiles with compositing
- `Scene/`: Scene graph implementation using sweatervest

**C++ Backend** (`handsome/cpp_src/`)
- `RationalBilinearInverter.cpp/.hpp`: Core sampling algorithm
- `Micropolygon.hpp`, `MicropolygonMesh.hpp`: C++ representations
- Compiled on-the-fly using the phillip build system
- Loaded into Python via ctypes in `capi.py`

**OpenCL Implementation** (`handsome/opencl_src/`)
- `opencl_api.cl`: GPU kernel for micropolygon sampling
- Experimental implementation, not required for core functionality

## Installation

### Prerequisites

- Python 3.x
- NumPy >= 1.9.2
- Pillow >= 2.9.0 (for image I/O)
- C++ compiler (gcc/clang on Linux/macOS, MSVC on Windows)

### Clone with Submodules

Handsome uses git submodules for external dependencies. Clone with:

```bash
git clone --recursive https://github.com/bracket/handsome.git
```

Or if you've already cloned the repository:

```bash
cd handsome
git submodule update --init --recursive
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Handsome

```bash
pip install -e .
```

On first import, the C++ backend will be compiled automatically. This may take a minute.

## Git Submodules

Handsome includes two external packages as git submodules in the `external/` directory:

### phillip (`external/phillip/`)

**Purpose:** C++ on-the-fly compilation and loading system

Phillip provides the infrastructure for compiling C++ source files dynamically when handsome is imported, then loading the compiled shared library via ctypes. This eliminates the need for users to manually compile C++ code.

**Key functions:**
- `build_so()`: Compiles source files into a shared library
- `generate_extension_args()`: Generates compiler flags and arguments
- `load_library()`: Loads compiled library for use with ctypes

**Usage in handsome:** See `handsome/capi.py` for integration example.

### sweatervest (`external/sweatervest/`)

**Purpose:** Scene graph language in JSON/YAML format

Sweatervest provides a declarative way to describe scenes with primitives, transformations, and hierarchical grouping. Scene files can be saved, loaded, and manipulated programmatically.

**Key features:**
- JSON/YAML scene serialization
- Transformation stacks
- Group nodes with children
- Primitive types: MicropolygonMesh, Circle, etc.

**Usage in handsome:** See `handsome/Scene/__init__.py` and `examples/005_scene.py`.

### Updating Submodules

To update submodules to the latest version:

```bash
git submodule update --remote --merge
```

## Usage

### Basic Example: Rendering a Colored Tile

```python
from handsome import Tile
from handsome.Pixel import Pixel
from handsome.util import save_array_as_image
import numpy as np

# Create a 100x100 pixel tile
tile = Tile((0, 0), (100, 100), dtype=Pixel)

# Fill with white background
white = np.array([(255, 255, 255, 255)], dtype=Pixel)
tile.buffer[:, :] = white

# Paint quadrants with different colors
red = np.array([(255, 0, 0, 255)], dtype=Pixel)
tile.buffer[:50, :50] = red

green = np.array([(0, 255, 0, 255)], dtype=Pixel)
tile.buffer[50:, :50] = green

# Save to image
save_array_as_image(tile.buffer, 'output.tiff', 'RGBA')
```

### Rendering a Micropolygon

```python
from handsome import Micropolygon, MicropolygonMesh, TileCache
from handsome.util import render_mesh, point
import numpy as np

# Create a 2x2 micropolygon mesh
mesh = MicropolygonMesh(shape=(2, 2))

# Define vertex positions (in projective space: x, y, z, w)
mesh.buffer['position'][0, 0] = point(10, 10)
mesh.buffer['position'][0, 1] = point(50, 10)
mesh.buffer['position'][1, 0] = point(10, 50)
mesh.buffer['position'][1, 1] = point(50, 50)

# Set vertex colors (RGBA floats)
mesh.buffer['color'][0, 0] = (1.0, 0.0, 0.0, 1.0)  # Red
mesh.buffer['color'][0, 1] = (0.0, 1.0, 0.0, 1.0)  # Green
mesh.buffer['color'][1, 0] = (0.0, 0.0, 1.0, 1.0)  # Blue
mesh.buffer['color'][1, 1] = (1.0, 1.0, 0.0, 1.0)  # Yellow

# Render with oversampling (4x4 samples per pixel)
cache = render_mesh(mesh, sample_rate=4)

# Composite and save
from handsome.util import save_array_as_image
save_array_as_image(cache.tiles[0].buffer, 'micropolygon.tiff', 'RGBA')
```

### Loading and Rendering a Scene

```python
import sweatervest
from handsome.Scene import render_scene
from handsome.util import save_array_as_image

# Load scene from YAML file
scene = sweatervest.load('examples/data/005_scene.yaml')

# Render scene with 4x oversampling
canvas = render_scene(scene, sample_rate=4)

# Save result
save_array_as_image(canvas.buffer, 'scene.tiff', 'RGBA')
```

## Examples

The `examples/` directory contains working demonstrations:

| Example | Description |
|---------|-------------|
| `001_tile.py` | Basic tile creation and pixel manipulation |
| `002_micropolygon.py` | Single micropolygon rendering |
| `003_circle.py` | Circular primitive using micropolygon subdivision |
| `004_star.py` | Star shape rendering |
| `005_scene.py` | Scene graph loading and rendering with sweatervest |
| `006_texture.py` | Texture mapping onto micropolygons |
| `007_subdivider.py` | Surface subdivision demonstrations |
| `008_integrative.py` | Complex scene with multiple primitives |
| `009_open_cl.py` | OpenCL GPU-accelerated rendering (experimental) |
| `010_stipple_texture.py` | Stipple texture effects |

Run examples from the repository root:

```bash
python3 examples/001_tile.py
```

Rendered images are saved to `examples/render/`.

## Project Structure

```
handsome/
├── handsome/                 # Main Python package
│   ├── __init__.py          # Package exports and version
│   ├── Micropolygon.py      # Single bilinear quadrilateral
│   ├── MicropolygonMesh.py  # Grid of micropolygons
│   ├── Tile.py              # Image tile with sample buffer
│   ├── TileCache.py         # Multi-tile management
│   ├── Pixel.py             # Pixel data types (uint8, float)
│   ├── capi.py              # ctypes interface to C++ backend
│   ├── _capi.cpp            # C wrapper for C++ functions
│   ├── opencl_api.py        # OpenCL kernel interface
│   ├── util.py              # Helper functions (save_image, colors, etc.)
│   ├── TransformStack.py    # Transformation matrix stack
│   ├── Scene/               # Scene graph implementation
│   │   └── __init__.py      # Scene rendering and mesh extraction
│   ├── cpp_src/             # C++ backend source
│   │   ├── RationalBilinearInverter.cpp/.hpp  # Core inversion algorithm
│   │   ├── Micropolygon.hpp # C++ micropolygon representation
│   │   ├── MicropolygonMesh.hpp
│   │   ├── Vec.hpp          # Vector math utilities
│   │   ├── Filter.cpp/.hpp  # Sampling filters
│   │   └── [other headers]
│   └── opencl_src/
│       └── opencl_api.cl    # OpenCL kernel implementation
├── examples/                 # Working example scripts
│   ├── 001_tile.py → 010_stipple_texture.py
│   ├── data/                # Scene files and assets
│   │   ├── 005_scene.yaml
│   │   └── blank_scene.yaml
│   └── render/              # Output directory for examples
├── tests/                    # Test suite
│   ├── test_micropolygon.py
│   ├── test_tile.py
│   ├── test_opencl.py
│   └── [other tests]
├── external/                 # Git submodules
│   ├── phillip/             # C++ build system
│   └── sweatervest/         # Scene graph language
├── setup.py                  # Package installation
├── setup.cfg                 # Package configuration
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## How It Works: The C++ Integration

Handsome uses a unique approach to integrate C++ performance with Python convenience:

1. **On first import**, `handsome/capi.py` calls the phillip build system
2. **phillip compiles** the C++ sources (`_capi.cpp`, `RationalBilinearInverter.cpp`) into a shared library
3. **The library is loaded** via ctypes, making C++ functions callable from Python
4. **NumPy arrays** are passed to C++ using memory pointers
5. **C++ processes** the performance-critical sampling and interpolation
6. **Results** are written back to NumPy arrays for Python to use

This design allows:
- No manual build step for users
- Portable across platforms (Linux, macOS, Windows)
- Fast C++ execution with Python's ease of use
- Easy debugging (modify C++ source, reimport to recompile)

## Performance Notes

- **Sampling is CPU-bound**: Rational bilinear inversion is compute-intensive
- **Oversampling multiplies cost**: 4x sample rate = 16x more samples (4² in 2D)
- **C++ provides ~10-100x speedup** over pure Python for sampling
- **OpenCL experimental**: GPU acceleration not yet fully optimized
- **Memory tiling**: Tile-based rendering keeps memory usage predictable

## Future Goals

- **Victor GUI**: Drawing tool with vi keybindings for interactive scene creation
- **OpenCL optimization**: Full GPU pipeline for high-performance rendering
- **Advanced shading**: Programmable shaders and material system
- **More primitives**: Bezier patches, Coons patches, subdivision surfaces
- **Animation**: Keyframe interpolation and motion blur
- **Documentation**: API reference and tutorial series

## Contributing

Contributions are welcome! When contributing:

1. Follow existing code style and conventions
2. Add tests for new features
3. Update documentation as needed
4. Ensure examples still run correctly
5. Test across Python 3.x versions if possible

## Development

### Running Tests

```bash
python3 -m pytest tests/
```

### Rebuilding C++ Code

C++ code is rebuilt automatically on import if source files change. To force a rebuild, delete the cached shared library:

```bash
rm handsome/*.so        # Linux/macOS
rm handsome/*.dll       # Windows
```

### Modifying C++ Backend

1. Edit files in `handsome/cpp_src/`
2. Update `_capi.cpp` if adding new exported functions
3. Update `DLL_FUNCS` in `capi.py` for ctypes signatures
4. Reimport handsome to trigger recompilation

## License

See the `COPYING` file for license information.

## Authors

- **Stephen [Bracket] McCray** (mcbracket@gmail.com)

## Acknowledgments

- Inspired by Pixar's RenderMan REYES architecture
- Built on NumPy for efficient numerical operations
- Uses PIL/Pillow for image I/O

---

**Handsome** - Beautiful rendering through micropolygon meshes
