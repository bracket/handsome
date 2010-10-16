#include "Vec.hpp"
#include "Line.hpp"
#include "Micropolygon.hpp"
#include "MicropolygonMesh.hpp"
#include "draw.hpp"
#include "BitmapWriter.hpp"
#include "Bezier.hpp"
#include "Interval.hpp"

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

TileCache * draw_one_bezier(float d, Vec4 const & color) {
	Vec2 axis = Vec2(1.0f, -1.0f);
	normalize(axis);

	Bezier b;
	b[0] = Vec2(0.0f, 0.0f);
	b[1] = Vec2(512.0f, 512.0f) - d * axis;
	b[2] = Vec2(512.0f, 512.0f) + d * axis;
	b[3] = Vec2(1024.0f, 1024.0f);

	MicropolygonMesh * mesh = b.bust();

	TileCache * cache = new TileCache(16, 4);
	draw(*mesh, *cache, color);

	delete mesh;
	return cache;
}

int main() {
	SampleBuffer buffer(1024, 1024);

	Vec4 start_color(255.0f, 138.0f, 0.0f, 255.0f),
		end_color(219.0f, 58.0f, 26.0f, 255.0f);
	
	start_color /= 255.0f;
	end_color /= 255.0f;

	float min_axis = 256.0f,
		max_axis = 1024.0f;

	for (int i = 0; i <= 9; ++i) {
		float t = static_cast<float>(i) / 9.0f;
		float d = (1.0f - t) * min_axis + t * max_axis;
		Vec4 color = (1.0f - t) * start_color + t * end_color;
		TileCache * cache = draw_one_bezier(d, color);
		aggregate_cache(buffer, AARectangle<int>(0, 0, 1024, 1024), 1, *cache);
		delete cache;
	}


	write_bitmap("out.bmp", buffer);
}
