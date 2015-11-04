#include "RationalBilinearInverter.hpp"

typedef Vec2 Coordinate;
typedef Vec4 Point;
typedef Vec4 Pixel;
typedef Vec4 BoundingBox;

struct Vertex {
  Point position;
  Pixel color;
};


namespace {
  void _fill_micropolygon(
    Vertex const & lower_left,  Vertex const & upper_left,
    Vertex const & lower_right, Vertex const & upper_right,
    Vec4 const & bounding_box,
    int width, int height,
    Coordinate const * coordinates,
    Pixel * tile
  )
  {
    for (int j = 0; j < height; ++j) {
      Vec2 const * coordinate_row = coordinates + j * width;
      Pixel * image_row = tile + j * width;

      for (int i = 0; i < width; ++i) {
        Coordinate const & c = *(coordinate_row + i);

        bool skip =
          c.x() < bounding_box.x() || bounding_box.z() < c.x()
            || c.y() < bounding_box.y() || bounding_box.w() < c.y();

        if (skip) { continue; }

        RationalBilinearInverter rbi(
          c,
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
    Vertex const * mesh, BoundingBox const * bounds,
    int tile_width, int tile_height,
    Coordinate * coordinates,
    Pixel * tile
  )
  {
    int bounds_width = mesh_width - 1;

    for (int j = 1; j < mesh_height; ++j) {
      Vertex const * lower_row = mesh + j * mesh_width;
      BoundingBox const * bounds_row = bounds + (j - 1) * bounds_width;

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
          *(bounds_row + i - 1),
          tile_width, tile_height,
          coordinates, tile
        );
      }
    }
  }

  inline Vec2 to_projection_plane(Vec4 const & point) {
    return Vec2(point.x() / point.z(), point.y() / point.z());
  }

  inline Vec4 make_bounding_box(Vec2 const & left, Vec2 const & right) {
    Vec4 out(
      left.x(), left.y(),
      right.x(), right.y()
    );

    if (out.z() < out.x()) { std::swap(out.x(), out.z()); }
    if (out.w() < out.y()) { std::swap(out.y(), out.w()); }

    return out;
  }

  inline Vec4 combine_bounding_boxes(Vec4 const & left, Vec4 const & right) {
    return Vec4(
      (std::min)(left.x(), right.x()),
      (std::min)(left.y(), right.y()),
      (std::max)(left.z(), right.z()),
      (std::max)(left.w(), right.w())
    );
  }

  void _fill_bounds_buffer(
    int mesh_width, int mesh_height,
    Vertex const * mesh,
    BoundingBox * bounds
  )
  {
    int bounds_width = mesh_width - 1,
      bounds_height = mesh_height - 1;

    Vec2 left = to_projection_plane(mesh->position),
      right(0, 0);

    for (int i = 1; i < mesh_width; ++i) {
      right = to_projection_plane((mesh + i)->position);
      *(bounds + i - 1) = make_bounding_box(left, right);
      left = right;
    }

    for(int j = 1; j < mesh_height; ++j) {
      Vec4 * lower_bounds = bounds + j * bounds_width,
           * upper_bounds = lower_bounds - bounds_width;

      Vertex const * lower_row = mesh + j * mesh_width;
      left = to_projection_plane(lower_row->position);

      for (int i = 1; i < mesh_width; ++i) {
        right = to_projection_plane((lower_row + i)->position);

        Vec4 b = make_bounding_box(left, right);
        if (j < bounds_height) { *lower_bounds = b; }
        *upper_bounds = combine_bounding_boxes(*upper_bounds, b);

        ++lower_bounds;
        ++upper_bounds;
      }
    }
  }
}

extern "C" {
  void fill_micropolygon_mesh(
    int mesh_width, int mesh_height,
    Vertex const * mesh, BoundingBox const * bounds,
    int tile_width, int tile_height,
    Coordinate * coordinates,
    Pixel * tile
  )
  {
    _fill_micropolygon_mesh(
      mesh_width, mesh_height,
      mesh, bounds,
      tile_width, tile_height,
      coordinates, tile
    );
  }

  void fill_bounds_buffer(
    int mesh_width, int mesh_height,
    Vertex const * mesh,
    BoundingBox * bounds
  )
  {
    _fill_bounds_buffer(
      mesh_width,
      mesh_height,
      mesh,
      bounds
    );
  }
}
