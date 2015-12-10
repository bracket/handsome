#include "RationalBilinearInverter.hpp"

typedef Vec2 Coordinate;
typedef Vec4 Point;
typedef Vec4 Pixel;
typedef Vec4 BoundingBox;

struct Vertex {
  Point position;
  Pixel color;
};

struct Rectangle {
  float left, bottom, right, top;
};

inline std::ostream & operator << (std::ostream & out, Rectangle const & r) {
  out << "Rectangle(left=" << r.left
      << ", bottom= " << r.bottom
      << ", right= "  << r.right
      << ", top="     << r.top
      << ")";

  return out;
}

namespace {
  inline bool points_are_close(Vec4 const & left, Vec4 const & right) {
    float x = left.x() - right.x(),
          y = left.y() - right.y(),
          z = left.z() - right.z(),
          w = left.w() - right.w()
    ;

    return x * x + y * y + z * z + w * w < .01;
  }

  inline bool points_are_close(Vertex const & v, Vec4 const & p) {
    return points_are_close(v.position, p);
  }

  void _fill_micropolygon(
    Vertex const & lower_left,  Vertex const & upper_left,
    Vertex const & lower_right, Vertex const & upper_right,
    Vec4 const & bounding_box,
    int rows, int columns,
    Coordinate const * coordinates,
    Pixel * tile
  )
  {
    for (int i = 0; i < rows; ++i) {
      Vec2 const * coordinate_row = coordinates + i * columns;
      Pixel * image_row = tile + i * columns;

      for (int j = 0; j < columns; ++j) {
        Coordinate const & c = *(coordinate_row + j);

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

        *(image_row + j) = vp * bottom + v * top;
      }
    }
  }

  void _fill_micropolygon_mesh(
    int mesh_rows, int mesh_columns,
    Vertex const * mesh, BoundingBox const * bounds,
    int tile_rows, int tile_columns,
    Rectangle const & tile_bounds,
    Coordinate * coordinates,
    Pixel * tile
  )
  {
    int bounds_columns = mesh_columns - 1;

    for (int i = 1; i < mesh_rows; ++i) {
      Vertex const * lower_row = mesh + i * mesh_columns;
      BoundingBox const * bounds_row = bounds + (i - 1) * bounds_columns;

      for (int j = 1; j < mesh_columns; ++j) {
        Vertex const
          * lower_right = lower_row + j,
          * lower_left  = lower_right - 1,
          * upper_right = lower_right - mesh_columns,
          * upper_left  = lower_left - mesh_columns
        ;

        Vec4 const & poly_bounds = *(bounds_row + j - 1);

        bool skip =
          tile_bounds.right < poly_bounds.x()
            || poly_bounds.z() < tile_bounds.left
            || tile_bounds.top < poly_bounds.y()
            || poly_bounds.w() < tile_bounds.bottom
        ;

        if (skip) { continue; }

        _fill_micropolygon(
          *lower_left, *upper_left,
          *lower_right, *upper_right,
          poly_bounds,
          tile_rows, tile_columns,
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

  BoundingBox _fill_bounds_buffer(
    int mesh_rows, int mesh_columns,
    Vertex const * mesh,
    BoundingBox * bounds
  )
  {
    int bounds_rows = mesh_rows - 1,
      bounds_columns = mesh_columns - 1;

    Vec2 left = to_projection_plane(mesh->position),
      right(0, 0);

    BoundingBox total(left.x(), left.y(), left.x(), left.y());

    for (int j = 1; j < mesh_columns; ++j) {
      right = to_projection_plane((mesh + j)->position);
      *(bounds + j - 1) = make_bounding_box(left, right);
      total = combine_bounding_boxes(total, *(bounds + j - 1));
      left = right;
    }

    for(int i = 1; i < mesh_rows; ++i) {
      Vec4 * lower_bounds = bounds + i * bounds_columns,
           * upper_bounds = lower_bounds - bounds_columns;

      Vertex const * lower_row = mesh + i * mesh_columns;
      left = to_projection_plane(lower_row->position);

      for (int j = 1; j < mesh_columns; ++j) {
        right = to_projection_plane((lower_row + j)->position);

        Vec4 b = make_bounding_box(left, right);
        if (i < bounds_rows) { *lower_bounds = b; }
        *upper_bounds = combine_bounding_boxes(*upper_bounds, b);
        total = combine_bounding_boxes(total, *upper_bounds);

        ++lower_bounds;
        ++upper_bounds;
        left = right;
      }
    }
      }
    }

    return total;
  }
}

extern "C" {
  void fill_micropolygon_mesh(
    int mesh_rows, int mesh_columns,
    Vertex const * mesh, BoundingBox const * bounds,
    int tile_rows, int tile_columns,
    Rectangle tile_bounds,
    Coordinate * coordinates,
    Pixel * tile
  )
  {
    _fill_micropolygon_mesh(
      mesh_rows, mesh_columns,
      mesh, bounds,
      tile_rows, tile_columns,
      tile_bounds,
      coordinates, tile
    );
  }

  Rectangle fill_bounds_buffer(
    int mesh_rows, int mesh_columns,
    Vertex const * mesh,
    BoundingBox * bounds
  )
  {
    Rectangle out;

    BoundingBox b = _fill_bounds_buffer(
      mesh_rows,
      mesh_columns,
      mesh,
      bounds
    );

    out.left = b.x();
    out.bottom = b.y();
    out.right = b.z();
    out.top = b.w();

    return out;
  }
}
