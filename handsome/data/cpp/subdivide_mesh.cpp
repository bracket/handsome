// bool subdivide_mesh(
//      Vertex * out_mesh, int out_rows, int out_cols
//      Vertex const * in_mesh, int in_rows, int in_cols
// )

if (out_rows % in_rows != 0) { return false; }
if (out_cols % in_cols != 0) { return false; }

int row_stride = out_rows / in_rows;
int col_stride = out_cols / in_cols;

float row_step = 1.f / static_cast<float>(row_stride);
float col_step = 1.f / static_cast<float>(col_stride);

for (int in_j = 0; in_j < in_rows; ++in_j) {
    for (int in_i = 0; in_i < in_cols; ++in_i) {
        Vertex const
            * upper_left = in_mesh + in_j * (in_cols + 1) + in_i,
            * lower_left = upper_left + (in_cols + 1),
            * upper_right = upper_left + 1,
            * lower_right = lower_left + 1;

        for (int out_j = in_j * row_stride; out_j < in_j * row_stride + row_stride; ++out_j) {
            float v = (out_j % row_stride) * row_step,
                vp = 1.f - v;

            Vertex * out_row = out_mesh + out_j * (out_cols + 1);

            for (int out_i = in_i * col_stride; out_i < in_i * col_stride + col_stride; ++out_i) {
                float u = (out_i % col_stride) * col_step,
                    up = 1.f - u;

                Vec4 low_position = up * cast_vec(lower_left->position) + u * cast_vec(lower_right->position),
                    high_position = up * cast_vec(upper_left->position) + u * cast_vec(upper_right->position),
                    position = vp * high_position + v * low_position;

                Vec4 low_color = up * cast_vec(lower_left->color) + u * cast_vec(lower_right->color),
                    high_color = up * cast_vec(upper_left->color) + u * cast_vec(upper_right->color),
                    color = vp * high_color + v * low_color;

                Vertex * out = out_row + out_i;
                out->position = cast_position(position);
                out->color = cast_color(color);
            }
        }
    }
}

for (int in_j = 0; in_j < in_rows; ++in_j) {
    Vertex const * upper = in_mesh + in_j * (in_cols + 1) + in_cols,
        * lower = upper + (in_cols + 1);

    for (int out_j = in_j * row_stride; out_j < in_j * row_stride + row_stride; ++out_j) {
        float v = (out_j % row_stride) * row_step,
            vp = 1.f - v;

        Vertex * out = out_mesh + out_j * (out_cols + 1) + out_cols;

        Vec4 position = vp * cast_vec(upper->position) + v * cast_vec(lower->position),
            color = vp * cast_vec(upper->position) + v * cast_vec(lower->position);

        out->position = cast_position(position);
        out->color = cast_color(color);
    }
}

for (int in_i = 0; in_i < in_cols; ++in_i) {
    Vertex const * left = in_mesh + in_rows * (in_cols + 1) + in_i,
        * right = left + 1;

    for (int out_i = 0; out_i < out_cols; ++out_i) {
        float u = (out_i % col_stride) * col_step,
            up = 1.f - u;

        Vec4 position = up * cast_vec(left->position) + u * cast_vec(right->position),
            color = up * cast_vec(left->color) + u * cast_vec(right->position);

        Vertex * out = out_mesh + out_rows * (out_cols + 1) + out_i;
        out->position = cast_position(position);
        out->color = cast_color(color);
    }
}

*(out_mesh + out_rows * (out_cols + 1) + out_cols) = *(in_mesh + in_rows * (in_cols + 1) + in_cols);

return true;
