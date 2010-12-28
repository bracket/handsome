#pragma once

#include <boost/utility.hpp>
#include <iterator>
#include <MicropolygonMesh.hpp>
#include <vector>
#include <VertexType.hpp>

template <class CurveType>
struct CurveSubdivider {
	typedef typename VertexType<CurveType>::type VertexType;
	typedef typename ScalarType<VertexType>::type ScalarType;

	private:
		struct NodeType {
			VertexType vertex_;

			Vec4 rhw_;
			Vec2 projected_position_;

			ScalarType u_;

			NodeType(CurveType const & curve, ScalarType const & u)
				: vertex_(curve(u)), rhw_(rhw_position(vertex_)),
					projected_position_(rhw_.x(), rhw_.y()), u_(u)
			{
				projected_position_ /= (rhw_.z() * rhw_.w());
			}
		};

		typedef std::vector<NodeType> NodeBuffer;

		struct TransposeIterator_ {
			typedef typename MicropolygonMesh<VertexType>::iterator base_iterator;

			TransposeIterator_(base_iterator begin, base_iterator end, int stride)
				: begin_(begin), it_(begin), end_(end), stride_(stride) { }

			void accumulate(VertexType const & vertex) {
				*it_ = vertex;
				it_ += stride_;
				if (it_ >= end_) { it_ = ++begin_; }
			}

			private:
				base_iterator begin_, it_, end_;
				int stride_;
		};

		struct TransposeIterator {
			TransposeIterator (TransposeIterator_ & base)
				: base_(base) { }

			TransposeIterator & operator * () { return *this; }

			TransposeIterator operator ++ (int) { return *this; }

			TransposeIterator & operator ++ () { return *this; }

			TransposeIterator & operator = (VertexType const & vertex) {
				base_.accumulate(vertex);
			}

			private:
				TransposeIterator_ & base_;
		};

	public:
		CurveSubdivider(CurveType const & curve, float width = 1.0f)
			: curve_(curve), half_width_(width / 2.0f)
		{
			ping_ = {
				NodeType(curve_, static_cast<ScalarType>(0.0)),
				NodeType(curve_, static_cast<ScalarType>(1.0))
			};

			calc_max_tol();
			subdivide();
		}

		MicropolygonMesh<VertexType> * get_mesh() const {
			MicropolygonMesh<VertexType> * mesh = new MicropolygonMesh<VertexType>(ping_.size(), 3);

			TransposeIterator_ out_(mesh->begin(), mesh->end(), ping_.size());
			TransposeIterator out(out_);

			auto right = ping_.begin(), left = right++;
			auto rhw_left = rhw_position(left->vertex_);
			auto proj_left = Vec2(rhw_left.x(), rhw_left.y()) / (rhw_left.z() * rhw_left.w());

			Vec2 ortho(0, 0);

			for (; right != ping_.end(); ++left, ++right) {
				auto rhw_right = rhw_position(right->vertex_);
				auto proj_right = Vec2(rhw_right.x(), rhw_right.y()) / (rhw_right.z() * rhw_right.w());

				ortho = rot_90(proj_right - proj_left);
				scale_length_to(ortho, half_width_);

				splay(out, left->vertex_, Vec4(ortho.x(), ortho.y(), 0.0f, 0.0f));

				rhw_left = rhw_right;
				proj_left = proj_right;
			}

			splay(out, left->vertex_, Vec4(ortho.x(), ortho.y(), 0.0f, 0.0f));

			return mesh;
		}

	private:
		NodeType split(NodeType const & left, NodeType const & right) const {
			ScalarType u = .5 * left.u_ + .5 * right.u_;
			return NodeType(curve_, u);
		}

		float tolerance_metric(NodeType const & left, NodeType const & right) const {
			return dist_sq(left.projected_position_, right.projected_position_);
		}

		void calc_max_tol() {
			max_tol_ = 0.0f;

			auto next = ping_.begin(), prev = next++;
			for (; next != ping_.end(); ++prev, ++next) {
				max_tol_ = (std::max)(max_tol_, tolerance_metric(*prev, *next));
			}
		}

		void subdivide() {
			float const tolerance = 1.0f;

			while (max_tol_ >= tolerance) {
				auto left = ping_.begin();

				pong_.push_back(*left);

				for (auto right = left + 1; right != ping_.end(); ++right) {
					pong_.push_back(split(*left, *right));
					pong_.push_back(*right);
					left = right;
				}

				ping_.swap(pong_);
				pong_.clear();
				calc_max_tol();
			}
		}

		CurveType const & curve_;
		NodeBuffer ping_, pong_;

		float max_tol_, half_width_;
};
