#pragma once

#include "Bezier.hpp"

class CoonsPatch {
	public:
		MicropolygonMesh * bust() const;

		Vec2 operator () (float u, float v) const {
			float up = 1.0f - u, vp = 1.0f - v;

			Vec2 a = up * left_(v) + u * right_(v),
				b = vp * bottom_(u) + v * top_(u);


			Vec2 c = vp * (up * bottom_[0] + u * bottom_[3])
				+ v * (up * top_[0] + u * top_[3]);

			return a + b - c;
		}

		Bezier & get_bottom() { return bottom_; }
		Bezier const & get_bottom() const { return bottom_; }

		Bezier & get_right() { return right_; }
		Bezier const & get_right() const { return right_; }

		Bezier & get_top() { return top_; }
		Bezier const & get_top() const { return top_; }

		Bezier & get_left() { return left_; }
		Bezier const & get_left() const { return left_; }

	private:
		Bezier bottom_, right_, top_, left_;
};
