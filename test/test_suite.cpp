#define BOOST_TEST_DYN_LINK
#define BOOST_TEST_MODULE RasterizerTestSuite
#include <boost/test/unit_test.hpp>

#include <BilinearPatch.hpp>
#include <QuadraticSolver.hpp>
#include <RationalBilinearInverter.hpp>
#include <Vec.hpp>

BOOST_AUTO_TEST_CASE(TEST_QUADRATIC_SOLVER) {
	QuadraticSolver<float> q(1.0f, 0.0f, -4.0f);
	BOOST_CHECK_EQUAL(q.size(), 2);
	BOOST_CHECK_EQUAL(q[0], -2.0f);
	BOOST_CHECK_EQUAL(q[1], 2.0f);
}

BOOST_AUTO_TEST_CASE(TEST_BILINEAR_PATCH) {
	BilinearPatch<Vec2> patch(
		Vec2(-1, -1), Vec2(1, -1),
		Vec2(-1, 1), Vec2(1, 1)
	);

	BOOST_CHECK_EQUAL(patch(0.5f, 0.0f), Vec2(0, -1));
}

BOOST_AUTO_TEST_CASE(TEST_RATIONAL_BILINEAR_INVERTER) {
	BilinearPatch<Vec4> patch(
		Vec4(0, 0, 1, 1),
		Vec4(1, 1, 1, 1),
		Vec4(0, 1, 1, 1),
		Vec4(1, 2, 1, 1)
	);

	for (int j = 0; j <= 64; ++j) {
		float v = static_cast<float>(j) / 64.0f;

		for (int i = 0; i <= 64; ++i) {
			float u = static_cast<float>(i) / 64.0f;

			Vec4 p4 = patch(u, v);
			Vec2 p2 = Vec2(p4.x(), p4.y()) / (p4.z() * p4.w());

			RationalBilinearInverter rbi(p2,
				patch[0], patch[1], patch[2], patch[3]
			);

			BOOST_REQUIRE(rbi.size() > 0);
			BOOST_CHECK_EQUAL(rbi.front().second, Vec2(u, v));
		}
	}
}
