#include "RationalBilinearInverter.hpp"

typedef Vec2 Coordinate;
typedef Vec4 Point;
typedef Vec4 Pixel;

struct Vertex {
  Point position;
  Pixel color;
};

namespace {
  void _fill_micropolygon(
    Vertex const & lower_left,  Vertex const & upper_left,
    Vertex const & lower_right, Vertex const & upper_right,
    int width, int height,
    Coordinate const * coordinates,
    Pixel * tile
  )
  {
    for (int j = 0; j < height; ++j) {
      Vec2 const * coordinate_row = coordinates + j * width;
      Pixel * image_row = tile + j * width;

      for (int i = 0; i < width; ++i) {
        RationalBilinearInverter rbi(
          *(coordinate_row + i),
          lower_left.position, lower_right.position,
          upper_left.position, upper_right.position
        );

        if (rbi.empty()) { continue; }

        Vec2 const & uv = rbi.front().second;

        float u = uv.x(),
              v = uv.y(),
              up = (1.f - u),
              vp = (1.f - v)
        ;

        Vec4 bottom = up * lower_left.color + u * lower_right.color,
             top    = up * upper_left.color + u * upper_right.color
        ;

        *(image_row + i) = vp * bottom + v * top;
      }
    }
  }

  void _fill_micropolygon_mesh(
    int mesh_width, int mesh_height,
    Vertex const * mesh,
    int tile_width, int tile_height,
    Coordinate * coordinates,
    Pixel * tile
  )
  {
    for (int j = 1; j < mesh_height; ++j) {
      Vertex const * lower_row = mesh + j * mesh_width;

      for (int i = 1; i < mesh_width; ++i) {
        Vertex const
          * lower_right = lower_row + i,
          * lower_left  = lower_right - 1,
          * upper_right = lower_right - mesh_width,
          * upper_left  = lower_left - mesh_width
        ;

        _fill_micropolygon(
          *lower_left, *upper_left,
          *lower_right, *upper_right,
          tile_width, tile_height,
          coordinates, tile
        );
      }
    }
  }
}

extern "C" {
  void fill_micropolygon_mesh(
    int mesh_width, int mesh_height,
    Vertex const * mesh,
    int tile_width, int tile_height,
    Coordinate * coordinates,
    Pixel * tile
  )
  {
    _fill_micropolygon_mesh(
      mesh_width, mesh_height,
      mesh,
      tile_width, tile_height,
      coordinates, tile
    );
  }
}
