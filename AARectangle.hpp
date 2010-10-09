#pragma once

#include "algorithm.hpp"
#include "Vec.hpp"
#include "Integer.hpp"

template <class T = float>
struct AARectangle {
	template <class> friend struct AARectangle;

	explicit AARectangle(
		T left = 0, T bottom = 0,
		T right = 0, T top = 0
	) :
		bounds_(left, bottom, right, top)
	{ }

	explicit AARectangle(Vec<4, T> const & bounds) : bounds_(bounds) { }

	template <class U>
	explicit AARectangle(AARectangle<U> const & right)
		: bounds_(right.bounds_)
	{ }

	T & get_left() { return bounds_[0]; }
	T const & get_left() const { return bounds_[0]; }

	T & get_bottom() { return bounds_[1]; }
	T const & get_bottom() const { return bounds_[1]; }

	T & get_right() { return bounds_[2]; }
	T const & get_right() const { return bounds_[2]; }

	T & get_top() { return bounds_[3]; }
	T const & get_top() const { return bounds_[3]; }

	T get_width() const { return get_right() - get_left(); }
	T get_height() const { return get_top() - get_bottom(); }

	Vec<4, T> & get_vec() { return bounds_; }
	Vec<4, T> const & get_vec() const { return bounds_; }

	AARectangle & operator *= (T const & right) {
		bounds_ *= right;
		return *this;
	}

	AARectangle operator * (T const & right) const {
		return AARectangle(bounds_ * right);
	}

	friend inline AARectangle operator * (T const & left, AARectangle const & right) {
		return AARectangle(left * right.bounds_);
	}

	AARectangle & operator /= (T const & right) {
		bounds_ /= right;
		return *this;
	}

	AARectangle operator / (T const & right) const {
		return AARectangle(bounds_ / right);
	}

	AARectangle & scale(T const & s) {
		bounds_ *= s;
		return *this;
	}

	void contract_div(T const & t) {
		bounds_[0] = cdiv(bounds_[0], t);
		bounds_[1] = cdiv(bounds_[1], t);
		bounds_[2] = fdiv(bounds_[2], t);
		bounds_[3] = fdiv(bounds_[3], t);
	}

	void expand_div(T const & t) {
		bounds_[0] = fdiv(bounds_[0], t);
		bounds_[1] = fdiv(bounds_[1], t);
		bounds_[2] = cdiv(bounds_[2], t);
		bounds_[3] = cdiv(bounds_[3], t);
	}

	AARectangle & shift(Vec<2, T> const & v) {
		bounds_ += Vec<4, T>(v.x(), v.y(), v.x(), v.y());
		return *this;
	}

	float get_area() const { return get_width() * get_height(); }

	template <class U>
	bool contains(Vec<2, U> const & pt) const {
		return get_left() <= pt.x() && pt.x() < get_right()
			&& get_bottom() <= pt.y() && pt.y() < get_top();
	}

	bool empty() const { return get_top() <= get_bottom() || get_right() <= get_left(); }

	private:
		Vec<4, T> bounds_;
};

template <class T>
inline AARectangle<T> intersection(AARectangle<T> const & lhs, AARectangle<T> const & rhs) {
	return AARectangle<T>(
		max(lhs.get_left(), rhs.get_left()),
		max(lhs.get_bottom(), rhs.get_bottom()),
		min(lhs.get_right(), rhs.get_right()),
		min(lhs.get_top(), rhs.get_top())
	);
}
