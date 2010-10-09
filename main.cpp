#include "Vec.hpp"
#include "Line.hpp"
#include "Micropolygon.hpp"
#include "MicropolygonMesh.hpp"
#include "draw.hpp"
#include "BitmapWriter.hpp"

#include <stdio.h>

namespace {
	struct AggregateTile {
		AggregateTile(
			SampleBuffer & out_buffer,
			AARectangle<int> const & out_bounds,
			int out_sample_rate
		) :
			out_buffer_(&out_buffer),
			out_bounds_(out_bounds),
			out_sample_bounds_(out_sample_rate * out_bounds),
			out_sample_rate_(out_sample_rate)
		{ }

		void operator () (
			TileCache const & cache,
			Vec<2, int> const & key,
			SampleBuffer const & buffer) const
		{
			int in_sample_rate = cache.get_sample_rate(),
				tile_stride = cache.get_tile_stride();

			AARectangle<int>
				tile_bounds(key.x(), key.y(), key.x() + 1, key.y() + 1),
				tile_in_bounds = tile_bounds * tile_stride,
				tile_out_bounds = (tile_in_bounds * out_sample_rate_);

			tile_out_bounds.expand_div(in_sample_rate);
			AARectangle<int> r = intersection(tile_out_bounds, out_sample_bounds_);

			float d = static_cast<float>(out_sample_rate_) / static_cast<float>(in_sample_rate);
			d *= d;

			for (int j = r.get_bottom(); j < r.get_top(); ++j) {
				int low_y = j * in_sample_rate, high_y = low_y + in_sample_rate;
				low_y = max(cdiv(low_y, out_sample_rate_) - tile_in_bounds.get_bottom(), 0);
				high_y = min(fdiv(high_y, out_sample_rate_) - tile_in_bounds.get_bottom(), tile_stride);

				for (int i = r.get_left(); i < r.get_right(); ++i) {
					int low_x = i * in_sample_rate, high_x = low_x + in_sample_rate;
					low_x = max(cdiv(low_x, out_sample_rate_) - tile_in_bounds.get_left(), 0);
					high_x = min(fdiv(high_x, out_sample_rate_) - tile_in_bounds.get_left(), tile_stride);

					Sample & s = (*out_buffer_)(i, j);

					for (int m = low_y; m < high_y; ++m) {
						for (int n = low_x; n < high_x; ++n) {
							s += (buffer(n, m) * d);
						}
					}

				}
			}
		}

		SampleBuffer * out_buffer_;
		AARectangle<int> out_bounds_, out_sample_bounds_;
		int out_sample_rate_;
	};
}

void aggregate_cache(SampleBuffer & buffer, AARectangle<int> const & bounds, int sample_rate,
	TileCache const & cache)
{
	cache.for_each_tile(
		AggregateTile(
			buffer, bounds, sample_rate
		)
	);
}

MicropolygonMesh * test_mesh() {
	MicropolygonMesh * mesh = new MicropolygonMesh(2, 2);
	(*mesh)(0, 0) = 3.0f * Vec2(8.0f, 0.0f);
	(*mesh)(1, 0) = 3.0f * Vec2(16.0f, 8.0f);
	(*mesh)(0, 1) = 3.0f * Vec2(0.0f, 8.0f);
	(*mesh)(1, 1) = 3.0f * Vec2(8.0f, 16.0f);
	return mesh;
}

struct Output {
	void operator () (TileCache const & cache, Vec<2, int> const & key, SampleBuffer const & buffer) const {
		printf("%i %i\n", key.x(), key.y());
	}
};

int main() {
	Line l(Vec2(0, 0), Vec2(1024, 1024));
	/*
	Micropolygon poly(
		Vec2(8.0f, 0.0f),
		Vec2(16.0f, 8.0f),
		Vec2(8.0f, 16.0f),
		Vec2(0.0f, 8.0f)
	);

	printf("%i\n", poly.contains(Vec2(8.0f, 8.0f)));
	*/

	MicropolygonMesh * mesh = l.bust();
	// MicropolygonMesh * mesh = test_mesh();

	TileCache tile_cache(16, 4);
	draw(*mesh, tile_cache, Vec4(0, 1, 1, 1));

	// tile_cache.for_each_tile(Output());

	SampleBuffer buffer(1024, 1024);
	aggregate_cache(buffer, AARectangle<int>(0, 0, 1024, 1024), 1, tile_cache);

	//SampleBuffer buffer(16, 16);
	//aggregate_cache(buffer, AARectangle<int>(0, 0, 16, 16), 1, tile_cache);
	
	 write_bitmap("out.bmp", buffer);
	 // write_bitmap("out.bmp", *tile_cache.get_tile(Vec<2, int>(1, 1)));
}
