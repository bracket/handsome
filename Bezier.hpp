#pragma once

#include "Vec.hpp"

#include <stdio.h>

struct MicropolygonMesh;

struct Bezier {
	Bezier() { }

	Bezier(Vec2 const & p0, Vec2 const & p1, Vec2 const & p2, Vec2 const & p3) {
		control_points_[0] = p0;
		control_points_[1] = p1;
		control_points_[2] = p2;
		control_points_[3] = p3;
	}

	MicropolygonMesh * bust() const;

	Vec2 & operator [] (int i) { return control_points_[i]; }
	Vec2 const & operator [] (int i) const { return control_points_[i]; }

	Vec2 operator () (float t) const {
		Bezier b = *this;
		float tp = 1.0f - t;

		for  (int end = 3; end > 0; --end) {
			for (int i = 0; i < end; ++i)
				{ b[i] = tp * b[i] + t * b[i+1]; }
		}

		return b[0];
	}

	Bezier split_off_right(float at) {
		Bezier right;
		float atp = 1.0f - at;

		right[3] = control_points_[3];

		for (int start = 1; start < 4; ++start) {
			for (int i = 3; i >= start; --i) {
				control_points_[i] = atp * control_points_[i-1] + at * control_points_[i];
			}
			right[3 - start] = control_points_[3];
		}

		return right;
	}

	private:
		Vec2 control_points_[4];
};
