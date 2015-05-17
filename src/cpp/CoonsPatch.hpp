#pragma once

#include <BilinearPatch.hpp>
#include <boost/optional.hpp>
#include <ScalarType.hpp>

template <class VertexType> struct Bezier;

template <class CurveType>
struct UniformCoonsPatchTraits {
	typedef typename VertexType<CurveType>::type VertexType;
	typedef CurveType LeftCurveType;
	typedef CurveType RightCurveType;
	typedef CurveType BottomCurveType;
	typedef CurveType TopCurveType;
};

template <class Traits>
struct CoonsPatch {
	typedef typename Traits::VertexType VertexType;
	typedef typename ScalarType<VertexType>::type ScalarType;

	typedef typename Traits::LeftCurveType LeftCurveType;
	typedef typename Traits::RightCurveType RightCurveType;
	typedef typename Traits::BottomCurveType BottomCurveType;
	typedef typename Traits::TopCurveType TopCurveType;

	CoonsPatch() { }

	template <class L, class R, class B, class T>
	CoonsPatch(L const & left, R const & right, B const & bottom, T const & top)
		: left_(left), right_(right), bottom_(bottom), top_(top) { }

	VertexType operator () (ScalarType u, ScalarType v) const {
		VertexType a = interpolate(u, left_(v), right_(v)),
			b = interpolate(v, bottom_(u), top_(u)),
			c = get_patch_value(u, v);

		return interpolate(.5,
			interpolate(-1, a, c),
			interpolate(-1, b, c)
		);
	}

	LeftCurveType & get_left() { return left_; }
	LeftCurveType const & get_left() const { return left_; }

	RightCurveType & get_right() { return right_; }
	RightCurveType const & get_right() const { return right_; }

	BottomCurveType & get_bottom() { return bottom_; }
	BottomCurveType const & get_bottom() const { return bottom_; }

	TopCurveType & get_top() { return top_; }
	TopCurveType const & get_top() const { return top_; }

	private:
		void init_patch() const {
			if (bilinear_patch_) { return; }

			bilinear_patch_.reset(
				BilinearPatch<VertexType>(
					bottom_(static_cast<ScalarType>(0.0)), bottom_(static_cast<ScalarType>(1.0)),
					top_(static_cast<ScalarType>(0.0)), top_(static_cast<ScalarType>(1.0))
				)
			);
		}

		VertexType get_patch_value(ScalarType u, ScalarType v) const {
			init_patch();
			return (*bilinear_patch_)(u, v);
		}

		LeftCurveType left_;
		RightCurveType right_;
		BottomCurveType bottom_;
		TopCurveType top_;

		mutable boost::optional<BilinearPatch<VertexType> > bilinear_patch_;
};
