#pragma once

#include <ScalarType.hpp>

template <class VertexType_>
struct Line {
	typedef VertexType_ VertexType;
	typedef typename ScalarType<VertexType>::type ScalarType;

	Line(VertexType const & start, VertexType const & end)
		: start_(start), end_(end)
	{ }

	VertexType operator () (ScalarType u) const {
		return interpolate(u, start_, end_);
	}

	private:
		VertexType start_, end_;
};
