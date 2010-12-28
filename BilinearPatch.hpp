#pragma once

#include <VertexType.hpp>

template <class VertexType_>
struct BilinearPatch {
	typedef VertexType_ VertexType;

	BilinearPatch(
		VertexType const & p00, VertexType const & p10,
		VertexType const & p01, VertexType const & p11
	)
	{
		corners_ = { p00, p10, p01, p11 };
	}

	VertexType operator () (float u, float v) const {
		VertexType b = interpolate(u, corners_[0], corners_[1]),
			t = interpolate(u, corners_[2], corners_[3]);
		return interpolate(v, b, t);
	}

	VertexType & operator [] (int i) { return corners_[i]; }
	VertexType const & operator [] (int i) const { return corners_[i]; }

	private:
		VertexType corners_[4];
};
