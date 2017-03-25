#pragma once

#include "Vec.hpp"

#include <utility>

struct RationalBilinearInverter {
	typedef std::pair<float, Vec2> value_type;
	typedef unsigned int size_type;

	typedef value_type & reference;
	typedef value_type const & const_reference;

	typedef value_type * iterator;
	typedef value_type const * const_iterator;

	RationalBilinearInverter(
		Vec2 const & p,
		Vec4 const & p00, Vec4 const & p10,
		Vec4 const & p01, Vec4 const & p11
	) : size_(0)
	{ solve(p, p00, p10, p01, p11); }

	iterator begin() { return solutions_; }
	const_iterator begin() const { return solutions_; }

	reference front() { return solutions_[0]; }
	const_reference front() const { return solutions_[0]; }

	iterator end() { return solutions_ + size_; }
	const_iterator end() const { return solutions_ + size_; }

	reference back() { return solutions_[size_ - 1]; }
	const_reference back() const { return solutions_[size_ - 1]; }

	bool empty() const { return size_ == 0; }
	size_type size() const { return size_; }

	private:
		void solve(
			Vec2 const & p,
			Vec4 const & p00, Vec4 const & p10,
			Vec4 const & p01, Vec4 const & p11
		);

		value_type solutions_[2];
		size_type size_;
};
