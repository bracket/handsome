#pragma once

#include <Sample.hpp>
#include <Fragment.hpp>

struct SolidShader {
	SolidShader(Sample const & color) : color_(color) { }

	template <class VertexType>
	void operator () (Sample & out, Fragment<VertexType> const & frag) const {
		out = color_;
	}

	private:
		Sample color_;
};
