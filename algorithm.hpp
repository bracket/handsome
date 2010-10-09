#pragma once

#include <math.h>

template <class T>
inline T min(T const & left, T const & right) {
	return right < left ? right : left;
};

template <class T>
inline T min(T const & t0, T const & t1, T const & t2) {
	return min(min(t0, t1), t2);
}

template <class T>
inline T max(T const & left, T const & right) {
	return right < left ? left : right;
}

template <class T>
inline T max(T const & t0, T const & t1, T const & t2) {
	return min(min(t0, t1), t2);
}

template <class T>
inline T clamp(T const & low, T const & high, T const & value) {
	return min(max(low, value), high);
}

template <class T>
inline T align_down(T t, T align) {
	return align * floor(t / align);
}

template <class T>
inline T align_up(T t, T align) {
	return align * ceil(t / align);
}
