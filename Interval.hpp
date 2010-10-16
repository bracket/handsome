#pragma once

#include "algorithm.hpp"
#include "Vec.hpp"

template <class T>
struct Interval {
	template <class> friend struct Interval;

	explicit Interval(T const & begin = 0, T const & end = 0)
		: extents_(begin, end) { }

	template <class U>
	explicit Interval(Interval<U> const & right)
		: extents_(right.extents_) { }
	
	explicit Interval(Vec<2, T> const & v) : extents_(v) { }

	T & get_begin() { return extents_[0]; }
	T const & get_begin() const { return extents_[0]; }

	T & get_end() { return extents_[1]; }
	T const & get_end() const { return extents_[1]; }

	bool empty() const { return get_end() <= get_begin(); }
	T get_length() const { return get_end() - get_begin(); }

	void contract_left(T const & amount = 1) { extents_[0] += amount; }
	void contract_right(T const & amount = 1) { extents_[1] -= amount; }

	void expand_left(T const & amount = 1) { extents_[0] -= amount; }
	void expand_right(T const & amount = 1) { extents_[1] += amount; }

	bool contains(T const & t) const { return extents_[0] <= t && t < extents_[1]; }

	void contract_div(T const & right) {
		extents_[0] = cdiv(extents_[0], right);
		extents_[1] = fdiv(extents_[1], right);
	}

	void expand_div(T const & right) {
		extents_[0] = fdiv(extents_[0], right);
		extents_[1] = cdiv(extents_[1], right);
	}

	Interval operator + (T const & t) const
		{ return Interval(extents_ + t); }

	friend Interval operator + (T const & t, Interval const & i)
		{ return Interval(t + i.extents_); }
	
	Interval & operator += (T const & t) {
		extents_ += t;
		return *this;
	}

	Interval operator - (T const & t) const
		{ return Interval(extents_ - t); }

	Interval & operator -= (T const & t) {
		extents_ -= t; 
		return *this;
	}

	Interval operator * (T const & t) const
		{ return Interval(extents_ * t); }

	friend Interval operator * (T const & t, Interval const & i)
		{ return Interval(t * i.extents_); }
	
	Interval & operator *= (T const & t) {
		extents_ *= t; 
		return *this;
	}

	Interval operator / (T const & t) const
		{ return Interval(extents_ / t); }
	
	Interval operator /= (T const & t) {
		extents_ /= t;
		return *this;
	}

	private:
		Vec<2, T> extents_;
};

template <class T>
inline Interval<T> intersection(Interval<T> const & left, Interval<T> const & right) {
	return Interval<T>(
		max(left.get_begin(), right.get_begin()),
		min(left.get_end(), right.get_end())
	);
}

template <class T>
inline Interval<T> contract_div(Interval<T> left, T const & right) {
	left.contract_div(right);
	return left;
}

template <class T>
inline Interval<T> expand_div(Interval<T> left, T const & right) {
	left.expand_div(right);
	return left;
}
