#include "algorithm.hpp"
#include "Filter.hpp"
#include "Interval.hpp"
#include "SampleBuffer.hpp"
#include "TileCache.hpp"
#include "Vec.hpp"

void convolve_into(
	SampleBuffer & out,
	SampleBuffer const & in,
	SampleBuffer const & kernel,
	Vec<2, int> const & out_offset,
	Vec<2, int> const & in_offset,
	int out_sample_rate,
	int in_sample_rate
)
{
	typedef AARectangle<int> rect;
	typedef Interval<int> interval;

	auto out_bounds_o = rect(0, 0, out.get_width(), out.get_height()) + out_offset,
		in_bounds_i = rect(0, 0, in.get_width(), in.get_height()) + in_offset,
		out_bounds_i = (out_bounds_o * in_sample_rate).contract_div(out_sample_rate).expand(kernel.get_width()),
		in_bounds_o = (in_bounds_i * out_sample_rate).expand_div(in_sample_rate),
		r_o = intersection(in_bounds_o, out_bounds_o);
	
	if (r_o.empty()) { return; }
	auto r_i = intersection(in_bounds_i, out_bounds_i);

	interval j = r_o.get_vertical();

	for (; !j.empty(); j.contract_begin()) {
		int dy = fdiv(j.get_begin() * in_sample_rate, out_sample_rate);
		interval ky(0, kernel.get_height()),
			y = intersection(ky + dy, in_bounds_i.get_vertical());

		interval i = r_o.get_horizontal();

		for (; !i.empty(); i.contract_begin()) {
			int dx = fdiv(i.get_begin() * in_sample_rate, out_sample_rate);
			interval kx(0, kernel.get_width()),
				x = intersection(kx + dx, in_bounds_i.get_horizontal());

			Sample & s = out(Vec<2, int>(i.get_begin(), j.get_begin()) - out_offset);

			for (int v = y.get_begin(), kv = y.get_begin() - dy; v < y.get_end(); ++v, ++kv) {
				for (int u = x.get_begin(), ku = x.get_begin() - dx; u < x.get_end(); ++u, ++ku) {
					s += kernel(ku, kv) * in(u - in_offset.x(), v - in_offset.y());
				}
			}
		}
	}
}

namespace {
	struct ConvolveTile {
		ConvolveTile(
			SampleBuffer & out_buffer,
			SampleBuffer const & kernel,
			int out_sample_rate
		) :
			out_buffer_(&out_buffer),
			kernel_(&kernel),
			out_sample_rate_(out_sample_rate)
		{ }

		void operator () (
			TileCache const & cache,
			Vec<2, int> const & key,
			SampleBuffer const & buffer) const
		{
			Vec<2, int> in_offset = cache.get_tile_length() * cache.get_sample_rate() * key;

			convolve_into(*out_buffer_, buffer, *kernel_,
				Vec<2, int>(0, 0), in_offset,
				out_sample_rate_, cache.get_sample_rate()
			);
		}

		SampleBuffer * out_buffer_;
		SampleBuffer const * kernel_;
		int out_sample_rate_;
	};
}

void convolve_into(
	SampleBuffer & out,
	TileCache const & cache,
	SampleBuffer const & kernel,
	int out_sample_rate
)
{
	cache.for_each_tile(ConvolveTile(out, kernel, out_sample_rate));
}
