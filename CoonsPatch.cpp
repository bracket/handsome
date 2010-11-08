#include "CoonsPatch.hpp"
#include "Vec.hpp"
#include "MicropolygonMesh.hpp"

#include <algorithm>
#include <vector>

namespace {
	inline Vec2 split(Vec2 const & left, Vec2 const & right) {
		return .5f * left + .5f * right;
	}

	struct CoonsPatchBuster {
		struct PatchNode {
			PatchNode(CoonsPatch const & patch, Vec2 const & param) :
				param(param), loc(patch(param.x(), param.y()))
			{ }

			Vec2 param, loc;
		};

		typedef std::vector<PatchNode> NodeBuffer;

		CoonsPatchBuster(CoonsPatch const & patch) :
			patch(patch),
			x_length(2), y_length(2)
		{
			ping = {
				PatchNode(patch, Vec2(0, 0)),
				PatchNode(patch, Vec2(1, 0)),
				PatchNode(patch, Vec2(0, 1)),
				PatchNode(patch, Vec2(1, 1))
			};
			
			max_x_sq = max(dist_sq(ping[1].loc, ping[0].loc), dist_sq(ping[3].loc, ping[2].loc));
			max_y_sq = max(dist_sq(ping[2].loc, ping[0].loc), dist_sq(ping[3].loc, ping[1].loc));
		}

		int split_x() {
			for (int j = 0; j < y_length; ++j) {
				int row_start = j * x_length;
				pong.insert(pong.end(), ping[row_start]);
				for (int i = 1; i < x_length; ++i) {
					pong.emplace(pong.end(),
						PatchNode(patch, split(ping[row_start + i - 1].param, ping[row_start + i].param))
					);

					pong.insert(pong.end(), ping[row_start + i]);
				}
			}

			return 2 * x_length - 1;
		}

		int split_y() {
			for (int i = 0; i < x_length; ++i) { pong.insert(pong.end(), ping[i]); }

			for (int j = 1; j < y_length; ++j) {
				int last_row = (j-1) * x_length, this_row = j * x_length;
				for (int i = 0; i < x_length; ++i) {
					pong.emplace(pong.end(),
						PatchNode(patch, split(ping[last_row + i].param, ping[this_row + i].param))
					);
				}

				for (int i = 0; i < x_length; ++i)
					{ pong.insert(pong.end(), ping[this_row + i]); }
			}

			return 2 * y_length - 1;
		}

		float calc_max(NodeBuffer const & buffer) {
			max_x_sq = max_y_sq = 0.0f;

			for (int i = 1; i < x_length; ++i) {
				max_x_sq = max(max_x_sq, dist_sq(buffer[i - 1].loc, buffer[i].loc));
			}

			int this_row = 0;

			for (int j = 1; j < y_length; ++j) {
				int last_row = this_row;
				this_row = last_row + x_length;

				max_x_sq = max(max_x_sq, dist_sq(buffer[this_row].loc, buffer[this_row + 1].loc));
				max_y_sq = max(max_y_sq, dist_sq(buffer[last_row].loc, buffer[this_row].loc));

				for (int i = 1; i < x_length; ++i) {
					max_x_sq = max(max_x_sq, dist_sq(buffer[this_row + i - 1].loc, buffer[this_row + i].loc));
					max_y_sq = max(max_y_sq, dist_sq(buffer[last_row + i].loc, buffer[this_row + i].loc));
				}
			}
		}

		void bust(float max_edge_length = .95f) {
			float threshold = max_edge_length * max_edge_length;

			while (max_x_sq >= threshold && max_y_sq >= threshold) {
				pong.clear();

				if (max_x_sq >= max_y_sq) { x_length = split_x(); }
				else { y_length = split_y(); }

				calc_max(pong);
				ping.swap(pong);
			}
		}

		MicropolygonMesh * make_mesh() {
			MicropolygonMesh * mesh = new MicropolygonMesh(x_length, y_length);
			std::transform(ping.begin(), ping.end(), mesh->get_vertices(),
				[] (PatchNode const & p) { return p.loc; }
			);

			return mesh;
		}

		CoonsPatch const & patch;
		NodeBuffer ping, pong;
		int x_length, y_length;
		float max_x_sq, max_y_sq;
	};
}

MicropolygonMesh * CoonsPatch::bust() const {
	CoonsPatchBuster buster(*this);
	buster.bust(10.0f);
	return buster.make_mesh();
}
