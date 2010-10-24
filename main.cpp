#include "Vec.hpp"
#include "Line.hpp"
#include "Micropolygon.hpp"
#include "MicropolygonMesh.hpp"
#include "draw.hpp"
#include "BitmapWriter.hpp"
#include "Bezier.hpp"
#include "Interval.hpp"
#include "Filter.hpp"
#include "Kernel.hpp"

#include <iostream>

template <class T>
std::ostream & operator << (std::ostream & out, Vec<2, T> const & v) {
	out << v.x() << " " << v.y();
	return out;
}

template <class T>
inline T square(T const & t) { return t * t; }

int main() {
	TileCache cache(16, 4);
	Line line(Vec2(0, 0), Vec2(1024, 1024));

	Vec4 color(1, 1, 1, 1);

	MicropolygonMesh * mesh = line.bust();

	SampleBuffer kernel = make_box_kernel(
		cache.get_sample_rate(), cache.get_sample_rate(),
		square(1.0f / static_cast<float>(cache.get_sample_rate()))
	);

	SampleBuffer out(1024, 1024);
	draw(*mesh, cache, color);
	convolve_into(out, cache, kernel, 1);
	write_bitmap("out.bmp", out);
}
