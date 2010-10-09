env = Environment();

env['CXX'] = '/opt/local/bin/g++-mp-4.4';

env.AppendUnique(CPPPATH = ['.']);
env.AppendUnique(CPPFLAGS = ['-std=c++0x']);
#env.AppendUnique(CPPFLAGS = ['-g']);
env.AppendUnique(CPPFLAGS = ['-O3']);

#sources = ['main.cpp', 'draw.cpp', 'pixel.cpp'];
sources = ['main.cpp', 'Line.cpp', 'draw.cpp', 'BitmapWriter.cpp'];

env.Program('weasel', sources);
