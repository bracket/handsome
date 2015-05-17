#include <Bezier.hpp>
#include <BilinearPatch.hpp>
#include <BitmapWriter.hpp>
#include <CoonsPatch.hpp>
#include <CurveSubdivider.hpp>
#include <Filter.hpp>
#include <Kernel.hpp>
#include <Line.hpp>
#include <Sample.hpp>
#include <SampleBuffer.hpp>
#include <shade.hpp>
#include <Shader.hpp>
#include <SurfaceSubdivider.hpp>
#include <TileCache.hpp>
#include <Vec.hpp>

#include <iostream>

struct Vertex {
	typedef float ScalarType;

	Vec4 rhw_position;
	Vec2 uv;
};

inline std::ostream & operator << (std::ostream & out, Vertex const & v) {
	out << v.rhw_position << std::endl;
	out << v.uv << std::endl;
	return out;
}

template <>
struct interpolate_impl<Vertex> {
	static inline Vertex call(
		float const & t,
		Vertex const & left,
		Vertex const & right
	)
	{
		return {
			interpolate(t, left.rhw_position, right.rhw_position),
			interpolate(t, left.uv, right.uv)
		};
	}
};

inline Vec4 rhw_position(Vertex const & vertex) {
	return vertex.rhw_position;
}

template <class OutputIterator>
struct splay_impl<OutputIterator, Vertex> {
	static inline void call(
		OutputIterator out,
		Vertex const & vertex,
		Vec4 const & v
	)
	{
		*out++ = Vertex({
			vertex.rhw_position - v,
			Vec2(vertex.uv.x(), 0.0)
		});

		*out++ = Vertex({
			vertex.rhw_position,
			Vec2(vertex.uv.x(), .5)
		});

		*out++ = Vertex({
			vertex.rhw_position + v,
			Vec2(vertex.uv.x(), 1.0)
		});
	}
};

template <class T>
inline T square(T const & t) { return t * t; }

inline float wrap(float f) { return f - floorf(f); }

struct Shader {
	void operator () (Sample & out, Fragment<Vertex> const & frag) const {
		float intensity = wrap(50.0f * (frag.vertex.uv.x() - frag.vertex.uv.y()));

		Vec4 c = interpolate(
			intensity,
			Vec4(255 / 255.0f, 152 / 255.0f, 6 / 255.0f, 1),
			Vec4(212 / 255.0f, 0 /255.0f, 4 / 255.0f, 1)
		);

		out.accumulate_color(c);
	}
};

int main() {
	TileCache cache(16, 4);

	typedef Bezier<Vertex> CurveType;
	typedef UniformCoonsPatchTraits<CurveType> TraitsType;
	typedef CoonsPatch<TraitsType> SurfaceType;

	CurveType left(
		{ Vec4(0, 0, 1, 1), Vec2(0, 0) },
		{ Vec4(0, 512, 1, 1), Vec2(0, 1.0 / 3) },
		{ Vec4(256, 768, 1, 1), Vec2(0, 2.0 / 3) },
		{ Vec4(512, 512, 1, 1), Vec2(0, 1) }
	);

	CurveType top(
		{ Vec4(512, 512, 1, 1), Vec2(0, 1) },
		{ Vec4(768, 512, 1, 1), Vec2(1.0 / 3, 1) },
		{ Vec4(768, 768, 1, 1), Vec2(2.0 / 3, 1) },
		{ Vec4(1024, 1024, 1, 1), Vec2(1, 1) }
	);

	CurveType bottom(
		{ Vec4(0, 0, 1, 1), Vec2(0, 0) },
		{ Vec4(256, 0, 1, 1), Vec2(1.0 / 3, 0) },
		{ Vec4(512, 256, 1, 1), Vec2(2.0 / 3, 0) },
		{ Vec4(768, 256, 1, 1), Vec2(1, 0) }
	);

	CurveType right(
		{ Vec4(768, 256, 1, 1), Vec2(1, 0) },
		{ Vec4(1024, 512, 1, 1), Vec2(1, 1.0 / 3) },
		{ Vec4(1024, 768, 1, 1), Vec2(1, 2.0 / 3) },
		{ Vec4(1024, 1024, 1, 1), Vec2(1, 1) }
	);

	SurfaceType surface(left, right, bottom, top);

	SurfaceSubdivider<SurfaceType> subdivider(surface);
	MicropolygonMesh<Vertex> * mesh = subdivider.get_mesh();
	shade(*mesh, cache, Shader());

	SampleBuffer kernel = make_box_kernel(
		cache.get_sample_rate(), cache.get_sample_rate(),
		square(1.0f / static_cast<float>(cache.get_sample_rate()))
	);

	SampleBuffer out(1024, 1024);
	convolve_into(out, cache, kernel, 1);
	write_bitmap("out.bmp", out);

	return 0;
}
