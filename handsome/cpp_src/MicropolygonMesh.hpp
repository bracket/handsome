#pragma once

#include <Micropolygon.hpp>
#include <vector>
#include <VertexType.hpp>

template <class VertexType_>
struct MicropolygonMesh {
	typedef VertexType_ VertexType;

	typedef std::vector<VertexType> ContainerType;

	typedef typename ContainerType::iterator iterator;
	typedef typename ContainerType::const_iterator const_iterator;
	typedef typename ContainerType::size_type size_type;

	MicropolygonMesh(int width, int height) :
		width_(width), height_(height)
	{
		vertices_.resize(width * height);
	}

	VertexType & operator () (int i, int j) { return vertices_[j * width_ + i]; }
	VertexType const & operator () (int i, int j) const { return vertices_[j * width_ + i]; }

	VertexType * get_vertices() { return &vertices_.front(); }

	int get_width() const { return width_; }
	int get_height() const { return height_; }

	template <class F>
	void for_each_sample(int sample_rate, F f) const {
		int h = height_ - 1, w = width_ - 1;

		for (int j = 0; j < h; ++j) {
			auto v = vertices_.begin() + j * width_, vp = v + 1;

			for (int i = 0; i < w; ++i) {
				Micropolygon<VertexType> poly(*v, *vp, *(vp + width_), *(v + width_));
				poly.for_each_sample(sample_rate, f);
				++v; ++vp;
			}
		}
	}

	iterator begin() { return vertices_.begin(); }
	const_iterator begin() const { return vertices_.begin(); }

	iterator end() { return vertices_.end(); }
	const_iterator end() const { return vertices_.end(); }

	size_type size() const { return vertices_.size(); }
	bool empty() const { return vertices_.empty(); }

	private:
		MicropolygonMesh(MicropolygonMesh const &); // no copying

		int width_, height_;
		ContainerType vertices_;
};
