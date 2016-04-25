#include "Vec.hpp"
#include <cmath>

struct Sample {
  float R, G, B, A;
};

typedef Vec4 Position;

struct MeshPoint {
  Position position;
  Sample sample;
};


Sample black = { 0., 0., 0., 1. };

Vec4 const & cast(Sample const & sample) {
  return reinterpret_cast<Vec4 const &>(sample);
}

Sample const & cast(Vec4 const & vec) {
  return reinterpret_cast<Sample const &>(vec);
}

extern "C" {
  Sample sample_texture(Vec4 const * texture_start, Vec4 const * texture_end, int columns, int rows, float s, float t) {
    t = 1. - t;

    if (s < 0.) { return black; }
    if (1. <= s) { return black; }

    if (t < 0.) { return black; }
    if (1. <= t) { return black; }

    s = s * (columns - 1);
    float s_index_f = std::floor(s);
    float s_frac = s - s_index_f;
    int s_index = static_cast<int>(s_index_f);

    t = t * (rows - 1);
    float t_index_f  = std::floor(t);
    float t_frac = t - t_index_f;
    int t_index = static_cast<int>(t_index_f);

    Vec4 const * top_left     = texture_start + s_index        + columns * t_index;
    Vec4 const * bottom_left  = texture_start + s_index        + columns * (t_index + 1);
    Vec4 const * top_right    = texture_start + (s_index + 1)  + columns * t_index;
    Vec4 const * bottom_right = texture_start + (s_index + 1)  + columns * (t_index + 1);

    float u  = s_frac;
    float up = 1. - s_frac;
    float v  = t_frac;
    float vp = 1. - t_frac;

    Vec4 out  =  up * vp * *top_left;
    out       += up * v  * *bottom_left;
    out       += u  * vp * *top_right;
    out       += u  * v  * *bottom_right;

    return *reinterpret_cast<Sample*>(&out);
  }

  void sample_texture_to_mesh(
    MeshPoint * mesh, int mesh_width, int mesh_height,
    Sample const * texture,  int texture_width, int texture_height
  ) {
    Sample const * texture_start = texture,
      * texture_end = texture + texture_width * texture_height;
    
    for (int j = 0; j < mesh_height; ++j) {
      float t = static_cast<float>(j) / static_cast<float>(mesh_width - 1);

      for (int i = 0; i < mesh_width; ++i) {
        float s = static_cast<float>(i) / static_cast<float>(mesh_height - 1);

        (mesh + j * mesh_width + i)->sample
          = sample_texture(&cast(*texture_start), &cast(*texture_end), texture_width, texture_height, s, t);
      }
    }
  }
}
