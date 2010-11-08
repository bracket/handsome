#pragma once

#include "Micropolygon.hpp"

struct MicropolygonMesh {
	MicropolygonMesh(int width, int height) :
		width_(width), height_(height),
		vertices_(new Vec2[width_ * height_])
	{ }

	~MicropolygonMesh() { delete [] vertices_; }

	Vec2 & operator () (int i, int j) { return *(vertices_ + j * width_ + i); }
	Vec2 const & operator () (int i, int j) const { return *(vertices_ + j * width_ + i); }

	Vec2 * get_vertices() { return vertices_; }

	int get_width() const { return width_; }
	int get_height() const { return height_; }

	template <class F>
	void for_each_sample(int sample_rate, F f) const {
		int h = height_ - 1, w = width_ - 1;

		for (int j = 0; j < h; ++j) {
			Vec2 * v = vertices_ + j * width_, *vp = v + 1;

			for (int i = 0; i < w; ++i) {
				Micropolygon poly(*v, *vp, *(vp + width_), *(v + width_));
				poly.for_each_sample(sample_rate, f);
				++v; ++vp;
			}
		}
	}

	private:
		MicropolygonMesh(MicropolygonMesh const &); // no copying

		int width_, height_;
		Vec2 * vertices_;
};
