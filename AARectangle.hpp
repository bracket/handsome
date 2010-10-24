#pragma once

#include "algorithm.hpp"
#include "Integer.hpp"
#include "Interval.hpp"

template <class T = float>
struct AARectangle {
	template <class> friend struct AARectangle;
	typedef Vec<2, T> Offset;

	explicit AARectangle(
		T left = 0, T bottom = 0,
		T right = 0, T top = 0
	) :
		horizontal_(left, right),
		vertical_(bottom, top)
	{ }

	explicit AARectangle(Vec<4, T> const & bounds) :
		horizontal_(bounds[0], bounds[2]),
		vertical_(bounds[1], bounds[3])
	{ }

	AARectangle(Interval<T> const & horizontal, Interval<T> const & vertical)
		: horizontal_(horizontal), vertical_(vertical) { }

	template <class U>
	explicit AARectangle(AARectangle<U> const & right)
		: horizontal_(right.horizontal_), vertical_(right.vertical_)
	{ }

	T & get_left() { return horizontal_.get_begin(); }
	T const & get_left() const { return horizontal_.get_begin(); }

	T & get_bottom() { return vertical_.get_begin(); }
	T const & get_bottom() const { return vertical_.get_begin(); }

	T & get_right() { return horizontal_.get_end(); }
	T const & get_right() const { return horizontal_.get_end(); }

	T & get_top() { return vertical_.get_end(); }
	T const & get_top() const { return vertical_.get_end(); }

	Interval<T> & get_horizontal() { return horizontal_; }
	Interval<T> const & get_horizontal() const { return horizontal_; }

	Interval<T> & get_vertical() { return vertical_; }
	Interval<T> const & get_vertical() const { return vertical_; }

	T get_width() const { return horizontal_.get_length(); }
	T get_height() const { return vertical_.get_length(); }

	Vec<4, T> get_vec() { return Vec<4, T>(get_left(), get_bottom(), get_right(), get_top()); }

	AARectangle && operator += (Offset const & right) {
		horizontal_ += right.x();
		vertical_ += right.y();
		return *this;
	} 

	AARectangle operator + (Offset const & right) const {
		return AARectangle(horizontal_ + right.x(), vertical_ + right.y());
	}

	friend AARectangle operator + (Offset const & left, AARectangle const & right) {
		return AARectangle(left.x() + right.horizontal_, left.y()  + right.vertical_);
	};

	AARectangle && operator -= (Offset const & right) {
		horizontal_ -= right.x();
		vertical_ -= right.y();
		return *this;
	}

	AARectangle operator - (Offset const & right) const {
		return AARectangle(horizontal_ - right.x(), vertical_ - right.y());
	}

	AARectangle & operator *= (T const & right) {
		horizontal_ *= right;
		vertical_ *= right;
		return *this;
	}

	AARectangle operator * (T const & right) const {
		return AARectangle(horizontal_ * right, vertical_ * right);
	}

	friend inline AARectangle operator * (T const & left, AARectangle const & right) {
		return AARectangle(left * right.horizontal_, left * right.vertical_);
	}

	AARectangle & operator /= (T const & right) {
		horizontal_ /= right;
		vertical_ /= right;
		return *this;
	}

	AARectangle operator / (T const & right) const {
		return AARectangle(horizontal_ / right, vertical_ / right);
	}

	AARectangle && contract(T const & amount) {
		horizontal_.contract(amount);
		vertical_.contract(amount);
		return *this;
	}

	AARectangle && expand(T const & amount) {
		horizontal_.expand(amount);
		vertical_.expand(amount);
		return *this;
	}

	AARectangle && contract_div(T const & t) {
		horizontal_.contract_div(t);
		vertical_.contract_div(t);
		return *this;
	}

	AARectangle && expand_div(T const & t) {
		horizontal_.expand_div(t);
		vertical_.expand_div(t);
		return *this;
	}

	float get_area() const { return get_width() * get_height(); }

	template <class U>
	bool contains(Vec<2, U> const & pt) const {
		return horizontal_.contains(pt.x()) && vertical_.contains(pt.y());
	}

	bool empty() const { return horizontal_.empty() || vertical_.empty(); }

	private:
		Interval<T> horizontal_, vertical_;
};

template <class T>
inline AARectangle<T> intersection(AARectangle<T> const & lhs, AARectangle<T> const & rhs) {
	return AARectangle<T>(
		intersection(lhs.get_horizontal(), rhs.get_horizontal()),
		intersection(lhs.get_vertical(), rhs.get_vertical())
	);
}

/*
template <class T>
inline AARectangle<T> contract_div(AARectangle<T> left, T const & right) {
	left.contract_div(right);
	return left;
}

template <class T>
inline AARectangle<T> expand_div(AARectangle<T> left, T const & right) {
	left.expand_div(right);
	return left;
}
*/
