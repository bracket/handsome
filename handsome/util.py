import math
import numpy as np

def save_array_as_image(array, path, mode):
    from PIL import Image
    image = Image.frombuffer(mode, array.shape, np.ascontiguousarray(array.T).data, 'raw', mode, 0, 1)
    image.save(path)


def point(x, y, z=1, w=1):
    return np.array([x, y, z, w], dtype=np.float32).T


def rotate_left(p):
    return point(-p[1], p[0], 0)


def normalize(vector):
    return vector / math.sqrt(sum(vector * vector))


def make_color_grammar():
    import re

    g = { }
    
    g['digit']      = r'[0-9a-fA-F]'
    g['ddigit']     = r'(?:{digit}{{2}})'.format(**g)
    g['hex_color']  = r'^#?(?:(?P<double>{ddigit}{{3,4}})|(?P<single>{digit}{{3,4}}))$'.format(**g)

    for key, value in g.items():
        g[key] = re.compile(value)

    return g

color_grammar = make_color_grammar()

def parse_color(string):
    g = color_grammar

    m = g['hex_color'].match(string)
    if m is None: return None

    single = m.group('single')
    if single is not None:
        R, G, B = single[0], single[1], single[2]
        A = 'f' if len(single) == 3 else single[3]
        return tuple(int(2*v, 16) for v in (R, G, B, A))

    double = m.group('double')
    if double is not None:
        R, G, B = double[0:2], double[2:4], double[4:6]
        A = 'ff' if len(double) == 6 else double[6:8]
        return tuple(int(v, 16) for v in (R, G, B, A))
