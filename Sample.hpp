#pragma once

#include "Vec.hpp"
#include "algorithm.hpp"

struct Sample {
	explicit Sample(
		float red = 0.0f, float green = 0.0f,
		float blue = 0.0f, float alpha = 0.0f
	) :
		color_(red, green, blue, alpha)
	{ }

	explicit Sample(Vec<4, float> const & color)
		: color_(color) { }

	Vec4 & get_color() { return color_; }
	Vec4 const & get_color() const { return color_; }

	Vec4 & accumulate_color(Vec4 const & c) { color_ += c; return color_; }

	float & get_red() { return color_[0]; }
	float const & get_red() const { return color_[0]; }

	float & get_green() { return color_[1]; }
	float const & get_green() const { return color_[1]; }

	float & get_blue() { return color_[2]; }
	float const & get_blue() const { return color_[2]; }

	float & get_alpha() { return color_[3]; }
	float const & get_alpha() const { return color_[3]; }

	Sample operator + (Sample const & right) const {
		return Sample(color_ + right.color_);
	}

	Sample & operator += (Sample const & right) {
		color_ += right.color_;
		return *this;
	}

	Sample operator / (float const & right) const {
		return Sample(color_ / right);
	}

	Sample & operator /= (float const & right) {
		color_ /= right;
		return *this;
	}

	Sample operator * (float const & right) const {
		return Sample(color_ * right);
	}

	friend inline Sample operator * (float const & left, Sample const & right) {
		return Sample(left * right.color_);
	}

	Sample & operator *= (float const & right) {
		color_ *= right;
		return *this;
	}

	uint32 to_uint32() {
		return to_uint8(color_[3]) << 24
			| to_uint8(color_[0]) << 16
			| to_uint8(color_[1]) << 8
			| to_uint8(color_[2]);
	}

	private:
		uint8 to_uint8(float const & f) {
			return static_cast<uint8>(clamp(0u, 255u, static_cast<uint32>(255.0f * f)));
		}

		Vec4 color_;
};
