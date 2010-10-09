#include "Line.hpp"
#include "Micropolygon.hpp"
#include "Vec.hpp"
#include "MicropolygonMesh.hpp"

namespace {
	const float width = 2.0f;
}

MicropolygonMesh * Line::bust() const {
	Vec2 x = get_end() - get_start();
	float l = normalize(x);
	Vec2 y = rot_90(x);

	float w = width / 2.0f,
		h = w / 2.0f;

	Vec2 points[] = {
		get_start() - h * x - width * y,
		get_end() + h * x - width * y,
		get_end() + h * x + width * y,
		get_start() - h * x + width * y
	};

	int x_steps = static_cast<int>(ceil(l)),
		y_steps = static_cast<int>(ceil(width));
	
	MicropolygonMesh * out = new MicropolygonMesh(x_steps, y_steps);

	for (int j = 0; j < y_steps; ++j) {
		float jt = static_cast<float>(j) / y_steps;
		Vec2 s = (1.0f - jt) * points[0] + jt * points[3],
			e = (1.0f - jt) * points[1] + jt * points[2];

		for (int i = 0; i < x_steps; ++i) {
			float it = static_cast<float>(i) / x_steps;
			Vec2 pt = (1.0f - it) * s + it * e;

			(*out)(i, j) = pt;
		}
	}

	return out;
}
