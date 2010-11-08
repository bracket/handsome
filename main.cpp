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
#include "CoonsPatch.hpp"

template <class T>
inline T square(T const & t) { return t * t; }

int main() {
	CoonsPatch patch;
	patch.get_bottom() = Bezier(Vec2(0, 0), Vec2(100, 100), Vec2(900, 100), Vec2(1000, 0));
	patch.get_right()  = Bezier(Vec2(1000, 0), Vec2(900, 100), Vec2(900, 900), Vec2(1000, 1000));
	patch.get_left()   = Bezier(Vec2(0, 0), Vec2(100, 100), Vec2(100, 900), Vec2(0, 1000));
	patch.get_top()    = Bezier(Vec2(0, 1000), Vec2(100, 900), Vec2(900, 900), Vec2(1000, 1000));

	TileCache cache(16, 4);
	Vec4 color(1, 1, 1, 1);

	MicropolygonMesh * mesh = patch.bust();

	/*
	for (int j = 0; j < mesh->get_height(); ++j) {
		for (int i = 0; i < mesh->get_width(); ++i) {
			std::cout << i << ", " << j << " = " << (*mesh)(i, j) << std::endl;
		}
	}

	return 0;
	*/

	SampleBuffer kernel = make_box_kernel(
		cache.get_sample_rate(), cache.get_sample_rate(),
		square(1.0f / static_cast<float>(cache.get_sample_rate()))
	);

	SampleBuffer out(1000, 1000);
	draw(*mesh, cache, color);
	convolve_into(out, cache, kernel, 1);
	write_bitmap("out.bmp", out);
}
