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

	SampleBuffer(SampleBuffer const & right) :
		width_(right.width_), height_(right.height_),
		samples_(new Sample[width_ * height_])
	{
		Sample * end = right.samples_ + right.width_ * right.height_,
			* in = right.samples_,
			* out = samples_;

		for (; in != end; ++in, ++out) { *in = *out; }
	}

	SampleBuffer(SampleBuffer && right) :
		width_(right.width_), height_(right.height_),
		samples_(right.samples_)
	{ right.samples_ = 0; }

	~SampleBuffer() { delete [] samples_; }

	Sample & operator () (int i, int j)  { return *(samples_ + j * width_ + i); }
	Sample const & operator () (int i, int j) const { return *(samples_ + j * width_ + i); }

	Sample & operator () (Vec<2, int> const & v)
		{ return *(samples_ + v.y() * width_ + v.x()); }

	Sample const & operator () (Vec<2, int> const & v) const
		{ return *(samples_ + v.y() * width_ + v.x()); }

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

	private:
		int width_, height_;
		Sample * samples_;
};
