env = Environment();

env['CXX'] = '/opt/local/bin/g++-mp-4.5';

env.AppendUnique(CPPPATH = ['.']);
env.AppendUnique(CPPFLAGS = ['-std=c++0x']);
#env.AppendUnique(CPPFLAGS = ['-g']);
env.AppendUnique(CPPFLAGS = ['-O3']);

sources = [
	'main.cpp',
	'Line.cpp',
	'draw.cpp',
	'BitmapWriter.cpp',
	'Bezier.cpp',
	'Filter.cpp',
	'CoonsPatch.cpp',
];

env.Program('weasel', sources);
