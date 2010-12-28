#pragma once

#include <Vec.hpp>

template <class VertexType>
struct Fragment {
	Fragment(
		VertexType const & vertex,
		Vec<2, int> const & sample_indices,
		int sample_rate
	) :
		vertex(vertex),
		sample_indices(sample_indices),
		sample_rate(sample_rate)
	{ }

	VertexType vertex;
	Vec<2, int> sample_indices;
	int sample_rate;
};
