#pragma once

#include "Vec.hpp"

struct MicropolygonMesh;

struct Line {
	Line() { }

	explicit Line(Vec2 const & start, Vec2 const & end)
		: start_(start), end_(end) { }
	
	Vec2 & get_start() { return start_; }
	Vec2 const & get_start() const { return start_; }

	Vec2 & get_end() { return end_; }
	Vec2 const & get_end() const { return end_; }

	Vec2 get_direction() const { return get_end() - get_start(); }
	
	MicropolygonMesh * bust() const;

	private:
		Vec2 start_, end_;
};

inline float length_sq(Line const & l) { return length_sq(l.get_direction()); }
