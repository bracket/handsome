#include "RationalBilinearInverter.hpp"

struct coordinate {
  float x, y;
  
  operator Vec2() const { return Vec2(x, y); }
};

struct point {
  float x, y, z, w;

  operator Vec4() const { return Vec4(x, y, z, w); }
};

struct Pixel {
  uint8_t R, G, B, A;
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
}
