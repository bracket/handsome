import numpy as np
import os

from handsome.MicropolygonMesh import MicropolygonMesh, Vertex, Position
from handsome.Pixel import FloatPixel, array_view, pixel_view
from handsome.Tile import Tile
from handsome.TileCache import TileCache
from handsome.util import render_mesh
from handsome.TransformStack import TransformStack

import sweatervest
from sweatervest import parse_scene


def main():
    import sys

    scene_path = sys.argv[1]
    render_path = sys.argv[2]

    render_image(scene_path, render_path)


def render_image(scene_path, out_path):
    from handsome.util import render_mesh, save_array_as_image

    scene = parse_scene(scene_path)
    canvas = render_scene(scene)

    buffer = array_view(canvas.downsample(1))
    buffer = np.clip(buffer, 0., 1.)
    buffer = (255. * buffer).astype(dtype=np.uint8)

    save_array_as_image(pixel_view(buffer), out_path, 'RGBA')


def make_canvas(canvas, sample_rate=4):
    from handsome.util import parse_color

    extents = canvas['extents']

    color = canvas.get('color', None)

    if color is None:
        color = np.array([1, 1, 1, 1], dtype=np.float32).view(dtype=FloatPixel)
    elif isinstance(color, str):
        color = [ c / 255. for c in parse_color(color) ]
        color = np.array(color, dtype=np.float32).view(dtype=FloatPixel)
    elif isinstance(color, (tuple, list)):
        color = [ c / 255. if isinstance(c, int) else c for c in color ]
        color = np.array(color, dtype=np.float32).view(dtype=FloatPixel)

    out = Tile((0, 0), extents, sample_rate, dtype=FloatPixel)
    out.buffer[:,:] = color

    return out


mesh_extractors = { }

current_xform = TransformStack()

def extract_meshes(obj):
    return mesh_extractors[type(obj)](obj)


def render_scene(scene):
    canvas = make_canvas(scene.data['canvas'])
    meshes = extract_meshes(scene.data['top'])

    for mesh in meshes:
        cache = render_mesh(mesh)
        cache.composite_into(canvas)

    return canvas


def extract_meshes_from_group(group_data):
    with current_xform(group_data.xform):
        for child in group_data.children:
            yield from extract_meshes(child)


def extract_meshes_from_micropolygon_mesh(mesh_data):
    shape = tuple(d - 1 for d in mesh_data.vertices.shape[:-1])
    mesh = MicropolygonMesh(shape)

    shape = mesh.buffer.shape
    mesh.buffer[:] = np.squeeze(mesh_data.vertices.view(Vertex))

    buffer = mesh.buffer

    array_dtype = np.dtype((np.float32, 4))

    positions = np.ravel(buffer['position']).view(array_dtype)
    positions = current_xform.dot(positions.T).T
    positions = np.ravel(positions).astype(np.float32).reshape(shape + (4,))
    positions = np.squeeze(positions.view(Position))

    buffer['position'] = positions

    yield mesh


mesh_extractors[sweatervest.MicropolygonMesh] = extract_meshes_from_micropolygon_mesh
mesh_extractors[sweatervest.Group] = extract_meshes_from_group


if __name__ == '__main__':
    main()
