#include "Bezier.hpp"
#include "MicropolygonMesh.hpp"
#include "Vec.hpp"

#include <math.h>

namespace {
	// NOTE: tolerance is essentially an upper bound on the area of b's control polygon.
	bool is_small_or_lineish(Bezier const & b, float tolerance) {
		Vec2 cross_edges[] = { b[2] - b[0], b[3] - b[1] };

		if (fabsf(cross(b[1] - b[0], cross_edges[0])) > tolerance) { return false; }
		if (fabsf(cross(b[2] - b[1], cross_edges[1])) > tolerance) { return false; }
		if (fabsf(cross(b[3] - b[2], cross_edges[0])) > tolerance) { return false; }
		if (fabsf(cross(b[0] - b[3], cross_edges[1])) > tolerance) { return false; }
		return true;
	}

	struct BezierBuster {
		private:
			struct ListNode {
				ListNode() : next(0) { }

				ListNode * get_last() {
					ListNode * n = this;
					for (; n->next; n = n->next) { }
					return n;
				}

				ListNode * append(ListNode * node) {
					ListNode * n = get_last();
					n->next = node;
					return n;
				}

				Vec2 values[3];
				ListNode * next;
			};

		public:
			BezierBuster(Bezier const & curve) :
				curve_(curve), list_(0), last_(0)
			{ }

			~BezierBuster() {
				for (ListNode * prev = 0, *next = list_; next; prev = next, next = next->next)
					{ delete prev; }
			}

			MicropolygonMesh * operator () () {
				bust_();

				int size = 0;
				for (ListNode * n = list_; n; n = n->next) { ++size; }
				if (!size) { return 0; }

				MicropolygonMesh * mesh = new MicropolygonMesh(size, 3);
				int i = 0;
				for (ListNode * n = list_; n; n = n->next, ++i) {
					for (int j = 0; j < 3; ++j) { (*mesh)(i, j) = n->values[j]; }
				}

				return mesh;
			}

		private:
			BezierBuster(BezierBuster const &); // no copying

			void bust_() {
				if (is_small_or_lineish(curve_, .5f)) {
					Vec2 y = rot_90(curve_[3] - curve_[0]);
					if (!normalize(y)) { return; }

					if (!list_) {
						list_ = last_ = new ListNode();
						list_->values[0] = curve_[0] - y;
						list_->values[1] = curve_[0];
						list_->values[2] = curve_[0] + y;
					}

					ListNode * next = new ListNode();
					next->values[0] = curve_[3] - y;
					next->values[1] = curve_[3];
					next->values[2] = curve_[3] + y;

					last_ = last_->append(next);

					return;
				}

				Bezier right = curve_.split_off_right(.5f);
				bust_();

				curve_ = right;
				bust_();
			}

			Bezier curve_;
			ListNode *list_, *last_;
	};
}

MicropolygonMesh * Bezier::bust() const {
	BezierBuster buster(*this);
	return buster();
}
