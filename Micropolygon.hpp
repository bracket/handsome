#pragma once

#include <AARectangle.hpp>
#include <Fragment.hpp>
#include <Integer.hpp>
#include <RationalBilinearInverter.hpp>
#include <TileCache.hpp>
#include <Vec.hpp>
#include <VertexType.hpp>

#include <algorithm>
#include <math.h>

template <class VertexType>
struct Micropolygon {
	explicit Micropolygon(
		VertexType const & p00,
		VertexType const & p10,
		VertexType const & p11,
		VertexType const & p01
	)
	{
		vertices_ = { &p00, &p10, &p01, &p11 };

		Vec4 p[] = {
			rhw_position(p00), rhw_position(p10),
			rhw_position(p01), rhw_position(p11)
		};

		projected_ = {
			Vec2(p[0].x(), p[0].y()) / (p[0].z() * p[0].w()),
			Vec2(p[1].x(), p[1].y()) / (p[1].z() * p[1].w()),
			Vec2(p[2].x(), p[2].y()) / (p[2].z() * p[2].w()),
			Vec2(p[3].x(), p[3].y()) / (p[3].z() * p[3].w())
		};
	}

	bool triangle_contains(Vec2 const & A, Vec2 const & B, Vec2 const & C, Vec2 const & x) const {
		return cross(B - A, x - A) >= 0.0f
			&& cross(C - B, x - B) >= 0.0f
			&& cross(A - C, x - C) >= 0.0f
		;
	}

	AARectangle<float> get_bounds() const {
		AARectangle<float> r(projected_[0].x(), projected_[0].y(), projected_[0].x(), projected_[0].y());

		for (Vec2 const * p = projected_ + 1; p != projected_ + 4; ++p) {
			if (p->y() > r.get_top()) { r.get_top() = p->y(); }
			else if (p->y() < r.get_bottom()) { r.get_bottom() = p->y(); }

			if (p->x() < r.get_left()) { r.get_left() = p->x(); }
			else if (p->x() > r.get_right()) { r.get_right() = p->x(); }
		}

		return r;
	}

	bool contains(Vec2 const & pt) const {
		return triangle_contains(projected_[0], projected_[1], projected_[3], pt)
			|| triangle_contains(projected_[0], projected_[3], projected_[2], pt);
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
				//if (!contains(pt)) { continue; }

				RationalBilinearInverter rbi(pt,
					rhw_position(*vertices_[0]), rhw_position(*vertices_[1]),
					rhw_position(*vertices_[2]), rhw_position(*vertices_[3])
				);

				if (rbi.empty()) { continue; }

				Vec2 const & v = rbi.front().second;

				VertexType b = interpolate(v.x(), *vertices_[0], *vertices_[1]),
					t = interpolate(v.x(), *vertices_[2], *vertices_[3]),
					p = interpolate(v.y(), b, t);

				Fragment<VertexType> frag(p, Vec<2, int>(sample_x, sample_y), sample_rate);

				f(frag);
			}
		}
	}

	private:
		VertexType const * vertices_[4];
		Vec2 projected_[4];
};
