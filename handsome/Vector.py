from numpy import dtype, array, int32, float32;

__all__ = [
    'Vec2i', 'vec2i',
    'Vec3i', 'vec3i',
    'Vec4i', 'vec4i',
    'Vec2f', 'vec2f',
    'Vec3f', 'vec3f',
    'Vec4f', 'vec4f',
];

# atts  = ['x', 'y', 'z', 'w']
# types = [('i', 'int32'), ('f', 'float32')]
# 
# for suffix, type in types:
#     for i in range(2, 5):
#         type_list = [ "('{}', {})".format(atts[j], type) for j in range(i) ];
#         print 'Vec{i}{suffix} = dtype([{type_list}], align=True)'.format(i=i, suffix=suffix, type_list=', '.join(type_list))
#         print
# 
#         arg_list  = ', '.join([ atts[j] for j in range(i) ])
#         cast_list = ', '.join([ '{type}({att})'.format(type=type, att=atts[j]) for j in range(i) ])
#         print 'def vec{i}{suffix}({arg_list}):'.format(i=i, suffix=suffix, arg_list=arg_list)
#         # print '   return Vec{i}{suffix}.type(({cast_list}))'.format(i=i, suffix=suffix, cast_list=cast_list)
#         print '   return array([({arg_list})], dtype=Vec{i}{suffix})[0]'.format(i=i, suffix=suffix, arg_list=arg_list)
#         print
#         print

Vec2i = dtype([('x', int32), ('y', int32)], align=True)

def vec2i(x, y):
   return array([(x, y)], dtype=Vec2i)[0]


Vec3i = dtype([('x', int32), ('y', int32), ('z', int32)], align=True)

def vec3i(x, y, z):
   return array([(x, y, z)], dtype=Vec3i)[0]


Vec4i = dtype([('x', int32), ('y', int32), ('z', int32), ('w', int32)], align=True)

def vec4i(x, y, z, w):
   return array([(x, y, z, w)], dtype=Vec4i)[0]


Vec2f = dtype([('x', float32), ('y', float32)], align=True)

def vec2f(x, y):
   return array([(x, y)], dtype=Vec2f)[0]


Vec3f = dtype([('x', float32), ('y', float32), ('z', float32)], align=True)

def vec3f(x, y, z):
   return array([(x, y, z)], dtype=Vec3f)[0]


Vec4f = dtype([('x', float32), ('y', float32), ('z', float32), ('w', float32)], align=True)

def vec4f(x, y, z, w):
   return array([(x, y, z, w)], dtype=Vec4f)[0]
