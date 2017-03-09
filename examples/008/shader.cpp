#include "Vec.hpp"
#include <vector>
#include <cmath>

struct Sample {
    float R, G, B, A;
};

typedef Vec4 Position;

struct MeshPoint {
    Position position;
    Sample sample;
};

Sample black = { 0.0, 0., 0., 1. };

Vec4 const & cast(Sample const & sample) {
    return reinterpret_cast<Vec4 const &>(sample);
}

Sample const & cast(Vec4 const & vec) {
    return reinterpret_cast<Sample const &>(vec);
}

Sample sample_texture(
    Vec4 const * texture_start,
    int columns, int rows,
    float s, float t
)
{
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

Vec4 lower_left  (64, 64, 1, 1);
Vec4 upper_left  (127,256, 1, 1);
Vec4 lower_right (256, 127, 1, 1);
Vec4 upper_right (496, 496, 1, 1);

Position surface(float u, float v) {
    Vec4 low = (1 - u) * lower_left + u * lower_right,
        high = (1 - u) * upper_left + u * upper_right;
    return (1 - v) * low + v * high;
}

extern "C" {
    float shader_time;

    void set_time(float t) {
        shader_time = t;
    }


    void generate_mesh(
        MeshPoint * mesh,
        int mesh_width, int mesh_height,
        Sample const * texture,
        int texture_width, int texture_height
    )
    {
        float i_div = 1.f / static_cast<float>(mesh_width - 1),
            j_div = 1.f / static_cast<float>(mesh_height - 1)
        ;

        for (int j = 0; j < mesh_height; ++j) {
            float t = static_cast<float>(j) * j_div;

            for (int i = 0; i < mesh_width; ++i) {
                float s = static_cast<float>(i) *i_div;

                MeshPoint * out = mesh + j * mesh_width + i;
                out->position = surface(s, t);
            }
        }

        std::vector<Vec2> texture_coords(mesh_width * mesh_height);

        for (int j = 1; j < mesh_height; ++j) {
            for (int i = 1; i < mesh_width; ++i) {
                MeshPoint * lower_left = mesh + (j - 1) * mesh_width + (i - 1),
                    * lower_right = lower_left + 1,
                    * upper_left = lower_left + mesh_width
                ;

                float delta_s = length(lower_right->position - lower_left->position),
                    delta_t = length(upper_left->position - lower_left->position)
                ;

                Vec2 * t_lower_left = &texture_coords[(j - 1) * mesh_width + i - 1],
                    * t_lower_right = t_lower_left + 1,
                    * t_upper_left  = t_lower_left + mesh_width
                ;

                t_lower_right->x() = t_lower_left->x() + delta_s;
                t_upper_left->y()  = t_lower_left->y() + delta_t;
            }
        }

        float shader_time_inverse = 1.f - shader_time,
            scale_factor = 1/256.f
        ;

        for (int j = 0; j < mesh_height; ++j) {
            float t = static_cast<float>(j) * j_div;

            for (int i = 0; i < mesh_width; ++i) {
                float s = static_cast<float>(i) * i_div;

                Vec2 start(s, t);
                Vec2 & end = texture_coords[j * mesh_width + i];

                end = shader_time * start + (shader_time_inverse * scale_factor) * end;
            }
        }


        for (int j = 0; j < mesh_height; ++j) {
            for (int i = 0; i < mesh_width; ++i) {
                Vec2 const & st = texture_coords[j * mesh_width + i];
                MeshPoint * out = mesh + j * mesh_width + i;

                out->sample
                    = sample_texture(&cast(*texture), texture_width, texture_height, st.x(), st.y());
            }
        }
    }
}
