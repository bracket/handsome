#pragma once

#include "Integer.hpp"
#include "AARectangle.hpp"
#include "Sample.hpp"
#include "Vec.hpp"
#include <stdio.h>

struct SampleBuffer {
	SampleBuffer(int width, int height) :
		width_(width), height_(height),
		samples_(new Sample[width * height])
	{ }

	explicit SampleBuffer(int length) :
		width_(length), height_(length),
		samples_(new Sample[length * length])
	{ }

	~SampleBuffer() { delete [] samples_; }

	Sample & operator () (int i, int j)  { return *(samples_ + j * width_ + i); }
	Sample const & operator () (int i, int j) const { return *(samples_ + j * width_ + i); }

	int get_width() const { return width_; } 
	int get_height() const { return height_; }
	int get_size()  const { return width_ * height_; }

	void write_bitmap(FILE * fd) const {
		Sample * end = samples_ + get_size();
		for (Sample * it = samples_; it != end; ++it) {
			uint32 p = it->to_uint32();
			fwrite(&p, sizeof(p), 1, fd);
		}
	}

	/*
	template <class F>
	void for_each_sample(int left, int bottom, F f) {
		Sample * s = samples_;

		Vec2 r(left, bottom);
		for (int j = 0; j < length_; ++j) {
			Vec2 pt = r;
			for (int i = 0; i < length_; ++i) {
				f(pt, *s++);
				pt.x() += delta_;
			}

			r.y() += delta_;
		}
	}

	template <class F>
	void for_each_sample(AARectangle<float> rect, int left, int bottom, F f) {
		rect = intersection(rect, 
			AARectangle<float>(left, bottom, left + length_, bottom + length_)
		);

		rect.scale(stride_);
		AARectangle<int> bounds(rect);

		Sample * row = samples_ + bottom * stride_ + left;
		Vec2 r(left, bottom);
		r *= delta_;

		for (int j = 0; j < length_; ++j) {
			Sample * s = row;
			Vec2 pt = r;

			for (int i = 0; i < length_; ++i) {
				f(pt, *s++);
				pt.x() += delta_;
			}

			row += stride_;
			r.y() += delta_;
		}
	}
	*/

	private:
		SampleBuffer(SampleBuffer const &); // no copying

		int width_, height_;
		Sample * samples_;
};