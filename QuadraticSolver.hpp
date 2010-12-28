#pragma once

#include <algorithm>
#include <cmath>

template <class T>
struct QuadraticSolver {
	typedef T value_type;
	typedef unsigned int size_type;

	typedef T * iterator;
	typedef T const * const_iterator;

	QuadraticSolver(T a, T b, T c) : size_(0) { solve(a, b, c); };

	QuadraticSolver(QuadraticSolver const & right) : size_(right.size_)
		{ std::copy(right.begin(), right.end(), begin()); }

	iterator begin() { return solutions_; }
	const_iterator begin() const { return solutions_; }

	iterator end() { return solutions_ + size_; }
	const_iterator end() const { return solutions_ + size_; }

	T const & operator [] (int i) const { return solutions_[i]; }

	bool empty() const { return size_ == 0; }
	size_type size() const { return size_; }

	private:
		void solve(T a , T b, T c) {
			if (a == 0) { solve_linear(b, c); }
			else { solve_quadratic(a, b, c); }
		}

		void solve_linear(T b, T c) {
			if (b == 0) { return; }

			solutions_[0] = -c / b;
			size_ = 1;
		}

		void solve_quadratic(T a, T b, T c) {
			T d = b * b - 4 * a * c;
			if (d < 0) { return; }
			a = 2 * a;
			b = -b;

			if (d == 0) {
				solutions_[0] = b / a;
				size_  = 1;
			}
			else {
				d = std::sqrt(d);
				solutions_[0] = (b - d) / a;
				solutions_[1] = (b + d) / a;

				if (solutions_[0] > solutions_[1])
					{ std::swap(solutions_[0], solutions_[1]); }
				
				size_ = 2;
			}
		}

		value_type solutions_[2];
		size_type size_;
};
