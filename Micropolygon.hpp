#pragma once

#include "AARectangle.hpp"
#include "Fragment.hpp"
#include "Integer.hpp"
#include "TileCache.hpp"
#include "Vec.hpp"

#include <math.h>
#include <stdio.h>

struct Micropolygon {
	explicit Micropolygon(
		Vec2 const & v0 = Vec2(),
		Vec2 const & v1 = Vec2(),
		Vec2 const & v2 = Vec2(),
		Vec2 const & v3 = Vec2()
	) {
		points_[0] = v0;
		points_[1] = v1;
		points_[2] = v2;
		points_[3] = v3;
	}

	float get_signed_area() const {
		// 	return bottom_edge.x() * left_edge.y() - bottom_edge.y() * left_edge.x();
	}
	
	float get_signed_area(Vec2 const & a, Vec2 const & b) const {
		return a.x() * b.y() - a.y() * b.x();
	}

	// float get_area() const { return fabsf(get_signed_area()); }

	AARectangle<float> get_bounds() const {
		AARectangle<float> r(points_->x(), points_->y(), points_->x(), points_->y());

		for (Vec2 const * p = points_ + 1; p != points_ + 4; ++p) {
			if (p->y() > r.get_top()) { r.get_top() = p->y(); }
			else if (p->y() < r.get_bottom()) { r.get_bottom() = p->y(); }

			if (p->x() < r.get_left()) { r.get_left() = p->x(); }
			else if (p->x() > r.get_right()) { r.get_right() = p->x(); }
		}

		return r;
	}

	float signed_contains_origin(Vec2 const & a, Vec2 const & b, Vec2 const & c) const {
		bool ab = is_left_of_or_on(-a, b - a),
			bc = is_left_of_or_on(-b, c - b);
		
		if (ab != bc) { return 0.0f; }
		bool ca = is_left_of_or_on(-c, a - c);

		return ca ? (ab ? 1.0f : 0.0f) : (!ab ? -1.0f : 0.0f);
	}

	bool contains(Vec2 const & pt) const {
		float s = signed_contains_origin(points_[0] - pt, points_[1] - pt, points_[2] - pt);
		if (s < 0.0f) { return false; }

		float t = signed_contains_origin(points_[0] - pt, points_[2] - pt, points_[3] - pt);
		if (t < 0.0f) { return false; }

		return s > 0.0f || t > 0.0f;
	}

	template <class F>
	void for_each_sample(int sample_rate, F f) const {
		float isr = 1.0f / sample_rate;

		Vec4 fbounds = get_bounds().get_vec();
		Vec<4, int> bounds = Vec<4, int>(
				floor(fbounds[0]), floor(fbounds[1]),
				ceil(fbounds[2]), ceil(fbounds[3])
			) * sample_rate;

		for (int sample_y = bounds[1]; sample_y < bounds[3]; ++sample_y) {
			float y = static_cast<float>(sample_y) * isr;
			for (int sample_x = bounds[0]; sample_x < bounds[2]; ++sample_x) {
				Vec2 pt(static_cast<float>(sample_x) * isr, y);
				if (!contains(pt)) { continue; }

				Fragment frag = {
					pt, Vec2(),
					Vec<2, int>(sample_x, sample_y), sample_rate
				};

				f(frag);
			}
		}
	}

	private:
		Vec2 points_[4];
};
