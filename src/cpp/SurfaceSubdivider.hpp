#pragma once

#include <boost/utility.hpp>
#include <MicropolygonMesh.hpp>
#include <vector>
#include <VertexType.hpp>

template <class SurfaceType>
struct SurfaceSubdivider : boost::noncopyable {
	typedef typename VertexType<SurfaceType>::type VertexType;
	typedef typename ScalarType<VertexType>::type ScalarType;

	private:
		struct NodeType {
			VertexType vertex_;

			ScalarType u_, v_;
			Vec4 rhw_;
			Vec2 projected_position_;

			NodeType(SurfaceType const & surface, ScalarType const & u, ScalarType const & v)
				: vertex_(surface(u, v)), u_(u), v_(v),
					rhw_(rhw_position(vertex_)), projected_position_(rhw_.x(), rhw_.y())
			{
				projected_position_ /= (rhw_.z() * rhw_.w());
			}
		};

		typedef std::vector<NodeType> NodeBuffer;
	
	public:
		SurfaceSubdivider(SurfaceType const & surface)
			: surface_(surface), u_length_(2), v_length_(2)
		{
			ScalarType const zero = static_cast<ScalarType>(0.0),
				one = static_cast<ScalarType>(1.0);

			ping_.push_back(NodeType(surface_, zero, zero));
			ping_.push_back(NodeType(surface_, one, zero));
			ping_.push_back(NodeType(surface_, zero, one));
			ping_.push_back(NodeType(surface_, one, one));

			max_u_tol_ = (std::max)(
				tolerance_metric(ping_[0], ping_[1]),
				tolerance_metric(ping_[2], ping_[3])
			);

			max_v_tol_ = (std::max)(
				tolerance_metric(ping_[0], ping_[2]),
				tolerance_metric(ping_[1], ping_[3])
			);

			subdivide();
		}

		MicropolygonMesh<VertexType> * get_mesh() const {
			MicropolygonMesh<VertexType> * mesh = new MicropolygonMesh<VertexType>(u_length_, v_length_);

			for (int j = 0; j < v_length_; ++j) {
				for (int i = 0; i < u_length_; ++i) {
					(*mesh)(i, j) = ping_[j * u_length_ + i].vertex_;
				}
			}

			return mesh;
		}

	private:
		NodeType split(
			NodeType const & left, NodeType const & right
		) const
		{
			ScalarType u = .5 * left.u_ + .5 * right.u_,
				v = .5 * left.v_ + .5 * right.v_;

			return NodeType(surface_, u, v);
		}

		float tolerance_metric(NodeType const & left, NodeType const & right) const {
			return dist_sq(left.projected_position_, right.projected_position_);
		}

		void split_u() {
			for (int j = 0; j < v_length_; ++j) {
				auto left = ping_.begin() + (j * u_length_);
				pong_.push_back(*left);

				for (int i = 1; i < u_length_; ++i) {
					auto right = ping_.begin() + (j * u_length_ + i);

					pong_.push_back(split(*left, *right));
					pong_.push_back(*right);

					left = right;
				}
			}

			u_length_ += (u_length_ - 1);
		}

		void split_v() {
			int last_row = 0;

			for (int i = 0; i < u_length_; ++i)
				{ pong_.push_back(ping_[i]); }

			for (int j = 1; j < v_length_; ++j) {
				int next_row = j * u_length_;

				for (int i = 0; i < u_length_; ++i) {
					pong_.push_back(split(ping_[last_row + i], ping_[next_row + i]));
				}

				for (int i = 0; i < u_length_; ++i) {
					pong_.push_back(ping_[next_row + i]);
				}

				last_row = next_row;
			}

			v_length_ += (v_length_ - 1);
		}

		void calc_max_u_tol() {
			max_u_tol_ = 0;

			for (int j = 0; j < v_length_; ++j) {
				auto left = pong_.begin() + j * u_length_;
				for (int i = 1; i < u_length_; ++i) {
					auto right = pong_.begin() + j * u_length_ + i;
					max_u_tol_ = (std::max)(max_u_tol_, tolerance_metric(*left, *right));
					left = right;
				}
			}
		}

		void calc_max_v_tol() {
			max_v_tol_ = 0;

			auto last = pong_.begin();

			for (int j = 1; j < v_length_; ++j) {
				auto next = pong_.begin() + j * u_length_;
				auto b = last, t = next;

				for (; b < next; ++b, ++t) {
					max_v_tol_ = (std::max)(max_v_tol_, tolerance_metric(*b, *t));
				}

				last = next;
			}
		}

		void subdivide() {
			const float tolerance = 1.0f;

			while (max_u_tol_ >= tolerance || max_v_tol_ >= tolerance) {
				if (max_u_tol_ >= max_v_tol_) { split_u(); calc_max_u_tol(); }
				else { split_v(); calc_max_v_tol(); }

				ping_.swap(pong_);
				pong_.clear();
			}
		}

		SurfaceType const & surface_;
		NodeBuffer ping_, pong_;

		int u_length_, v_length_;
		float max_u_tol_, max_v_tol_;
};
