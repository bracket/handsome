#pragma once

#include <VertexType.hpp>
#include <ScalarType.hpp>
#include <Vec.hpp>
#include <algorithm>

template <class> struct MicropolygonMesh;

template <class VertexType_>
struct Bezier {
	typedef VertexType_ VertexType;
	typedef typename ScalarType<VertexType>::type ScalarType;

	Bezier() { }

	Bezier(VertexType const & p0, VertexType const & p1, VertexType const & p2, VertexType const & p3) {
		control_points_ = { p0, p1, p2, p3 };
	}

	MicropolygonMesh<VertexType> * bust() const;

	VertexType & operator [] (int i) { return control_points_[i]; }
	VertexType const & operator [] (int i) const { return control_points_[i]; }

	VertexType operator () (ScalarType u) const {
		VertexType p[] = {
			interpolate(u, control_points_[0], control_points_[1]),
			interpolate(u, control_points_[1], control_points_[2]),
			interpolate(u, control_points_[2], control_points_[3])
		};

		VertexType * begin = p, * end = p + 3;

		for (; begin != end; --end) {
			VertexType * prev = begin, * next = begin + 1;
			for (; next != end; ++prev, ++next) {
				*prev = interpolate(u, *prev, *next);
			}
		}

		return p[0];
	}

	private:
		VertexType control_points_[4];
};
