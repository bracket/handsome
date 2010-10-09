#pragma once

#include <math.h>
#include <Integer.hpp>

template <bool, class T = void> struct enable_if { };
template <class T> struct enable_if<true, T> { typedef T type; };

template <int n, class T = float>
struct Vec {
	Vec() { clear(); }

	Vec(Vec const & right) {
		for (int i = 0; i < n; ++i) { values[i] = right[i]; }
	}

	template <class U>
	explicit Vec(Vec<n, U> const & right) {
		for (int i = 0; i < n; ++i) { values[i] = static_cast<T>(right[i]); }
	}

	template <class U>
	explicit Vec(U const (&array)[n]) {
		for (int i = 0; i < n; ++i) { values[i] = static_cast<T>(array[i]); }
	}

	template <class U>
	explicit Vec(U const & x,
		typename enable_if<(1 <= n), U>::type* = 0)
	{
		clear(); 
		values[0] = x;
	}

	template <class U>
	Vec(U const & x, U const & y,
		typename enable_if<(2 <= n), U>::type* = 0)
	{
		clear();
		values[0] = x;
		values[1] = y;
	}

	template <class U>
	Vec(U const & x, U const & y, U const & z,
		typename enable_if<(3 <= n), U>::type* = 0)
	{
		clear();
		values[0] = x;
		values[1] = y;
		values[2] = z;
	}

	template <class U>
	Vec(U const & x, U const & y,
		U const & z, U const & w,
		typename enable_if<(4 <= n), U>::type *  = 0)
	{
		clear();
		values[0] = x;
		values[1] = y;
		values[2] = z;
		values[3] = w;
	}

	T & operator [] (int i) { return values[i]; }
	T const & operator [] (int i) const { return values[i]; }

	T & x() { return values[0]; }
	T const & x() const { return values[0]; }

	T & y() { return values[1]; }
	T const & y() const { return values[1]; }

	T & z() { return values[2]; }
	T const & z() const { return values[2]; }

	T & w() { return values[3]; }
	T const & w() const { return values[3]; }

	bool operator == (Vec const & right) const {
		for (int i = 0; i < n; ++i) {
			if (values[i] != right[i]) { return false; }
		}
		return true;
	}

	bool operator != (Vec const & right) const {
		for (int i = 0; i < n; ++i) {
			if (values[i] == right[i]) { return false; }
		}
		return true;
	}

	Vec operator + (Vec const & right) const {
		Vec out;
		for (int i = 0; i < n; ++i) { out[i] = values[i] + right[i]; }
		return out;
	}

	Vec & operator += (Vec const & right) {
		for (int i = 0; i < n; ++i) { values[i] += right[i]; }
		return *this;
	}

	Vec operator - (Vec const & right) const {
		Vec out;
		for (int i = 0; i < n; ++i) { out[i] = values[i] - right[i]; }
		return out;
	}

	Vec & operator -= (Vec const & right) {
		for (int i = 0; i < n; ++i) { values[i] -= right[i]; }
		return *this;
	}

	Vec operator - () const {
		Vec out;
		for (int i = 0; i < n; ++i) { out[i] = -values[i]; }
		return out;
	}

	Vec operator * (T const & right) const {
		Vec out;
		for (int i = 0; i < n; ++i) { out[i] = values[i] * right; }

		return out;
	}

	friend inline Vec operator * (T const & left, Vec const & right) {
		Vec out;
		for (int i = 0; i < n; ++i) { out[i] = left * right[i]; }
		return out;
	}

	Vec & operator *= (T const & right) {
		for (int i = 0; i < n; ++i) { values[i] *= right; }
		return *this;
	}

	Vec operator / (T const & right) const {
		Vec out;
		for (int i = 0; i < n; ++i) { out[i] = values[i] / right; }
		return out;
	}

	Vec & operator /= (T const & right) {
		for (int i = 0; i < n; ++i) { values[i] /= right; }
		return *this;
	}

	Vec operator % (T const & right) const {
		Vec out;
		for (int i = 0; i < n; ++i) { out[i] = values[i] % right; }
		return out;
	}

	Vec & operator %= (T const & right) {
		for (int i = 0; i < n; ++i) { values[i] %= right; }
	}

	void clear() { for(int i = 0; i < n; ++i) { values[i] = 0; } }

	T values[n];
};

template <int n, class T>
inline T dot(Vec<n, T> const & left, Vec<n, T> const & right) {
	T out = 0;
	for (int i = 0; i < n; ++i) { out += left[i] * right[i]; }
	return out;
}

template <int n, class T>
inline T length_sq(Vec<n, T> const & v) {
	return dot(v, v);
}

template <int n, class T>
inline T length(Vec<n, T> const & v) {
	return sqrt(length_sq(v));
}

template <int n, class T>
inline T normalize(Vec<n, T> & v) {
	T l = length_sq(v);
	if (!l) { return l; }

	l = sqrt(l);
	v /= l;
	return l;
}

template <int n, class T>
inline T projection_ratio(Vec<n, T> const & v, Vec<n, T> const & onto) {
	return dot(v, onto) / length_sq(onto);
}

template <int n, class T>
inline Vec<n, T> proj_onto(Vec<n, T> const & v, Vec<n, T> const & onto) {
	return projection_ratio(v, onto) * onto;
}

template <int n, class T>
inline Vec<n, T> proj_ortho(Vec<n, T> const & v, Vec<n, T> const & offof) {
	return v - proj_onto(v, offof);
}

typedef Vec<2, float> Vec2;
typedef Vec<3, float> Vec3;
typedef Vec<4, float> Vec4;

template <class T>
inline Vec<2, T> rot_90(Vec<2, T> const & v) {
	return Vec<2, T>(-v.y(), v.x());
}

template <class T>
inline bool is_left_of(Vec<2, T> const & self, Vec<2, T> const & other) {
	return dot(self, rot_90(other)) > 0.0f;
}

template <class T>
inline bool is_left_of_or_on(Vec<2, T> const & self, Vec<2, T> const & other) {
	return dot(self, rot_90(other)) >= 0.0f;
}

template <class T>
inline Vec<3, T> cross(Vec<3, T> const & left, Vec<3, T> const & right) {
	return Vec<3, T>(
		left.y() * right.z() - left.z() * right.y(),
		- (left.x() * right.z() - left.z() * right.x()),
		left.x() * right.y() - left.y() * right.x()
	);
}

template <int n>
inline Vec<n, int> fdiv(Vec<n, int> const & left, int const & right) {
	Vec<n, int> out;
	for (int i = 0; i < n; ++i) { out[i] = fdiv(left[i], right); }
	return out;
}
