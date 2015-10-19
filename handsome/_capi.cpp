#include "RationalBilinearInverter.hpp"
#include <iostream>

struct coordinate {
  float x, y;
  
  operator Vec2() const { return Vec2(x, y); }

  friend std::ostream & operator << (std::ostream & out, coordinate const & c) {
    out << "(" << c.x << ", " << c.y << ")";
    return out;
  }
};

struct point {
  float x, y, z, w;

  operator Vec4() const { return Vec4(x, y, z, w); }

  friend std::ostream & operator << (std::ostream & out, point const & p) {
    out << "(" << p.x << ", " << p.y << ", " << p.z << ", " << p.w << ")";
    return out;
  }
};

struct Pixel {
  uint8_t R, G, B, A;
};

struct FloatPixel {
  float R, G, B, A;
};

namespace {
  void _fill(
    point const * lower_left, point const * upper_left,
    point const * lower_right, point const * upper_right,
    int width, int height,
    coordinate * coordinates,
    Pixel * image
  )
  {
    Pixel red = { 127, 0, 0, 255 };

    for (int j = 0; j < height; ++j) {
      coordinate const * coordinate_row = coordinates + j * width;
      Pixel * image_row = image + j * width;

      for (int i = 0; i < width; ++i) {
        RationalBilinearInverter rbi(
          *(coordinate_row + i),
          *lower_left, *lower_right,
          *upper_left, *upper_right
        );

        if (rbi.empty()) { continue; }

        *(image_row + i) = red;
      }
    }
  }

  void _fill_float(
    point const * lower_left, point const * upper_left,
    point const * lower_right, point const * upper_right,
    int width, int height,
    coordinate * coordinates,
    FloatPixel * image
  )
  {
    FloatPixel red = { .5, 0, 0, 1. };

    for (int j = 0; j < height; ++j) {
      coordinate const * coordinate_row = coordinates + j * width;
      FloatPixel * image_row = image + j * width;

      for (int i = 0; i < width; ++i) {
        RationalBilinearInverter rbi(
          *(coordinate_row + i),
          *lower_left, *lower_right,
          *upper_left, *upper_right
        );

        if (rbi.empty()) { continue; }

        *(image_row + i) = red;
      }
    }
  }
}

extern "C" {
  void fill(
    point const * lower_left, point const * upper_left,
    point const * lower_right, point const * upper_right,
    int width, int height,
    coordinate * coordinates,
    Pixel * image
  )
  {
    _fill(
      lower_left,
      upper_left,
      lower_right,
      upper_right,
      width, height,
      coordinates,
      image
    );
  }

  void fill_float(
    point const * lower_left, point const * upper_left,
    point const * lower_right, point const * upper_right,
    int width, int height,
    coordinate * coordinates,
    FloatPixel * image
  )
  {
    _fill_float(
      lower_left,
      upper_left,
      lower_right,
      upper_right,
      width, height,
      coordinates,
      image
    );
  }
}
