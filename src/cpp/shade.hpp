#pragma once

#include <Fragment.hpp>
#include <MicropolygonMesh.hpp>
#include <TileCache.hpp>
#include <Vec.hpp>

template <class VertexType, class ShaderType>
void shade(
	MicropolygonMesh<VertexType> const & mesh,
	TileCache & cache,
	ShaderType const & shader
)
{
	mesh.for_each_sample(
		cache.get_sample_rate(),
		[&cache, &shader] (Fragment<VertexType> const & frag) {
			int tile_length = cache.get_tile_length(),
				stride = cache.get_tile_stride();

			Vec<2, int> pixel = fdiv(frag.sample_indices, frag.sample_rate),
				tile = fdiv(pixel, tile_length),
				offset = frag.sample_indices - stride * tile;

			SampleBuffer * buffer = cache.get_tile(tile);
			shader((*buffer)(offset.x(), offset.y()), frag);
		}
	);
}
