#pragma once

struct MicropolygonMesh;
struct TileCache;
template <int, class> struct Vec;

void draw(MicropolygonMesh const & polys, TileCache & cache, Vec<4, float> const & color);
