#include "AARectangle.hpp"
#include "draw.hpp"
#include "Micropolygon.hpp"
#include "MicropolygonMesh.hpp"
#include "TileCache.hpp"
#include "Vec.hpp"
#include "Fragment.hpp"

#include <stdio.h>

namespace {
	struct Accumulate {
		Accumulate(TileCache & cache, Vec4 const & color)
			: cache_(&cache), color_(&color) { }

		void operator () (Fragment const & frag) {
			int tile_length = cache_->get_tile_length(),
				stride = cache_->get_tile_stride();

			Vec<2, int> pixel = fdiv(frag.sample_indices, frag.sample_rate),
				tile = fdiv(pixel, tile_length),
				offset = frag.sample_indices - stride * tile;

			SampleBuffer * buffer = cache_->get_tile(tile);
			(*buffer)(offset.x(), offset.y()).accumulate_color(*color_);
		}

		private:
			TileCache * cache_;
			Vec4 const * color_;
	};
}

void draw(
	MicropolygonMesh const & mesh,
	TileCache & cache,
	Vec4 const & color
)
{
	mesh.for_each_sample(cache.get_sample_rate(), Accumulate(cache, color));
}
