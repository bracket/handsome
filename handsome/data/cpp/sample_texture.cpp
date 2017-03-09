// Color sample_texture(
//     Vec4 const * texture_start,
//     int columns, int rows,
//     float s, float t
// )

t = 1. - t;
std::swap(s, t);

if (true) {
    // Texture wrapping
    s = s - std::floor(s);
    t = t - std::floor(t);
}
/*
else {
    // Constant
    if (s < 0.) { return black; }
    if (1. <= s) { return black; }

    if (t < 0.) { return black; }
    if (1. <= t) { return black; }
}
*/

s = s * (texture_width - 1);
float s_index_f = std::floor(s);
float s_frac = s - s_index_f;
int s_index = static_cast<int>(s_index_f);

t = t * (texture_height - 1);
float t_index_f  = std::floor(t);
float t_frac = t - t_index_f;
int t_index = static_cast<int>(t_index_f);

Vec4 const * top_left = texture_start + t_index * texture_width + s_index,
    * bottom_left     = top_left + texture_width,
    * top_right       = top_left + 1,
    * bottom_right    = top_right + texture_width;

float u  = s_frac;
float up = 1. - s_frac;
float v  = t_frac;
float vp = 1. - t_frac;

Vec4 out  =  up * vp * *top_left;
out       += up * v  * *bottom_left;
out       += u  * vp * *top_right;
out       += u  * v  * *bottom_right;

return *reinterpret_cast<Color*>(&out);
