#pragma once

#include <ScalarType.hpp>

template <int n, class T> struct Vec;
template <class VertexType> struct interpolate_impl;

template <class T, class VertexType>
inline VertexType interpolate(
	T const & t, VertexType const & left, VertexType const & right
)
{
	return interpolate_impl<VertexType>::call(t, left, right);
}

template <class VertexType>
Vec<4, float> rhw_position(VertexType const &);

template <class VertexType>
inline typename ScalarType<VertexType>::type
dist_sq(VertexType const & left, VertexType const & right);

template <class T>
struct VertexType {
	typedef typename T::VertexType type;
};

template <class OutputIterator, class VertexType> struct splay_impl;

template <class OutputIterator, class VertexType>
inline void splay(OutputIterator out, VertexType const & vertex, Vec<4, float> const & v) {
	return splay_impl<OutputIterator, VertexType>::call(out, vertex, v);
}
