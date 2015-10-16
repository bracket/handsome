#include "QuadraticSolver.hpp"
#include "RationalBilinearInverter.hpp"

#include <cmath>
#include <iostream>

namespace {
	template <class T, int n>
	inline void swap(T (&a)[n], T (&b)[n]) {
		T *ai = a, *bi = b, *end = a + n;
		for (; ai != end; ++ai, ++bi) {
			T t = *ai;
			*ai = *bi;
			*bi = t;
		}
	}

	template <class T>
	inline void normalize_front(T * begin, T * end) {
		T t = static_cast<T>(1.0 / *begin);
		*begin++ = static_cast<T>(1.0);
		for (; begin != end; ++begin) { *begin *= t; }
	}

	template <class T>
	inline void scale_and_subtract_row(T * out_begin, T * out_end, T scale, T const * in_begin) {
		scale = -scale;
		for (; out_begin < out_end; ++out_begin, ++in_begin)
			{ *out_begin += scale * *in_begin; }
	}

	template <class T, int m, int n>
	void print_matrix(T (&M)[m][n]) {
		for (int j = 0; j < m; ++j) {
			for (int i = 0; i < n; ++i) {
				if (i) { std::cout << " "; }
				std::cout << M[j][i];
			}
			std::cout << std::endl;
		}

		std::cout << std::endl;
	}
}

void RationalBilinearInverter::solve(
	Vec2 const & p,
	Vec4 const & p00, Vec4 const & p10,
	Vec4 const & p01, Vec4 const & p11
)
{
	double m[4][6] = {
		{ p00.x(), p10.x(), p01.x(), -p.x(), 0, -p11.x() },
		{ p00.y(), p10.y(), p01.y(), -p.y(), 0, -p11.y() },
		{ p00.z(), p10.z(), p01.z(),     -1, 0, -p11.z() },
		{ p00.w(), p10.w(), p01.w(),      0, 1, -p11.w() }
	};

	for (int j = 0; j < 4; ++j) {
		double a = 0.0;

		std::for_each(m[j], m[j + 1], [&] (double & f) { a = (std::max)(a, fabs(f)); });
		std::for_each(m[j], m[j + 1], [&] (double & f) { f /= a; });
	}

	for (int j = 0; j < 4; ++j) {
		int pivot_row = j; double pivot_value = fabsf(m[j][j]);

		for (int k = j + 1; k < 4; ++k) {
			auto t = fabsf(m[k][j]);
			if (t > pivot_value) {
				pivot_value = t;
				pivot_row = k;
			}
		}

		if (pivot_row != j) { swap(m[j], m[pivot_row]); }

		double * row = m[j] + j, * end = m[j + 1];
		normalize_front(row, end);

		for (int k = j + 1; k < 4; ++k) {
			scale_and_subtract_row(m[k] + j, m[k + 1], m[k][j], row);
		}
	}

	for (int i = 3; i > 0; --i) {
		for (int j = i - 1; j >= 0; --j) {
			scale_and_subtract_row(m[j] + i, m[j + 1], m[j][i], m[i] + i);
		}
	}

    double quad_a = m[0][5] - m[1][5] * m[2][5],
           quad_b = m[0][4] - m[1][4] * m[2][5] - m[1][5] * m[2][4],
           quad_c = - m[1][4] * m[2][4];

    if (-1e-3 < quad_a && quad_a < 1e-3) { quad_a = 0.; }
    if (-1e-3 < quad_b && quad_b < 1e-3) { quad_b = 0.; }
    if (-1e-3 < quad_c && quad_c < 1e-3) { quad_c = 0.; }

	QuadraticSolver<double> q(quad_a, quad_b, quad_c);

	for (auto it = q.begin(); it != q.end(); ++it) {
		double D = *it,
			alpha = m[3][4] + m[3][5] * D;

		if (alpha < 1.0 - 1e-3) { continue; }

		double A = m[0][4] + m[0][5] * D,
			B = m[1][4] + m[1][5] * D,
			C = m[2][4] + m[2][5] * D,
			d = A + B + C + D;
		
		if (!d || d != d) { continue; }

		double r = 1.0 / d,
			u = (B + D) * r,
			v = (C + D) * r;

		if (u < -1e-3 || u >= 1.0-1e-3) { continue; }
		if (v < -1e-3 || v >= 1.0-1e-3) { continue; }

		solutions_[size_++] = std::make_pair(alpha, Vec2(u, v));
	}
	
	if (size_ == 2 && solutions_[0].first > solutions_[1].first)
		{ std::swap(solutions_[0], solutions_[1]); }
}
