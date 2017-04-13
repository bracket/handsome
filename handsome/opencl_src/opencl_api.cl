// #pragma OPENCL EXTENSION cl_khr_fp64: enable

typedef float2 Coordinate;
typedef float4 Point;
typedef float4 Pixel;
typedef float4 BoundingBox;

typedef struct Vertex_tag {
    float4 position;
    float4 color;
} Vertex;

typedef struct Rectanbgle_tag {
    float left, bottom, right, top;
} Rectangle;

float4 rational_bilinear_invert(
    Coordinate c,
    Point lower_left, Point lower_right,
    Point upper_left, Point upper_right
);

float2 rotate_left(float2 in);

float2 solve_quadratic(float a, float b, float c);
float2 solve_quadratic_(float a, float b, float c);
float2 solve_linear(float b, float c);

__kernel void fill_micropolygon_mesh(
    __global Vertex const * mesh,
    __global BoundingBox const * bounds,
    int mesh_rows, int mesh_columns,
    // Rectangle tile_bounds,
    __global Coordinate const * coordinates,
    __global Pixel * tile
)
{
    int y = get_global_id(0),
        height = get_global_size(0);

    int x = get_global_id(1),
        width = get_global_size(1);

    int tile_index = y * width + x;

    Coordinate c = coordinates[tile_index];

    for (int i = 1; i < mesh_rows; ++i) {
        __global Vertex const * lower_row = mesh + i * mesh_columns;

        for (int j = 1; j < mesh_columns; ++j) {
            __global Vertex const
                * lower_right = lower_row + j,
                * lower_left = lower_right - 1,
                * upper_left = lower_left - mesh_columns,
                * upper_right = upper_left + 1
            ;

            // TODO: If coordinate not in bounds of micropolygon, continue

            // rational bilinear inversion

            float4 s = rational_bilinear_invert(
                c,
                lower_left->position, lower_right->position,
                upper_left->position, upper_right->position
            );

            float u = s.x, v = s.y,
                up = 1.f - u, vp = 1.f - v
            ;

            Pixel low = up * lower_left->color + u * lower_right->color,
                high = up * upper_left->color + u * upper_right->color,
                color = vp * low + v * high;

            if (!any(isnan(color))) {
                tile[tile_index] = color;
                continue;
            }

            u = s.z;
            v = s.w;
            up = 1.f - u;
            vp = 1.f - v;

            low = up * lower_left->color + u * lower_right->color;
            high = up * upper_left->color + u * upper_right->color;
            color = vp * low + v * high;

            if (any(isnan(color))) {
                tile[tile_index] = (float4)(0);
            }
            else {
                tile[tile_index] = color;
            }
        }
    }
}

float2 rotate_left(float2 in) {
    return (float2)(-in.y, in.x);
}

void swap_rows(float4 * m, int length, int row_1, int row_2) {
    for (int i = 0; i < length; ++i) {
        float t = m[i][row_1];
        m[i][row_1] = m[i][row_2];
        m[i][row_2] = t;
    }
}

int find_pivot_row(float4 column, int start) {
    int pivot_index = start;
    float pivot_value = fabs(column[start]);

    for (int i = start + 1; i < 4; ++i) {
        float t = fabs(column[i]);

        if (t > pivot_value) {
            pivot_index = i;
            pivot_value = t;
        }
    }

    return pivot_index;
}

void normalize_front(float4 * m, int length, int row) {
    float scale = 1.f / m[row][row];
    for (int i = row; i < length; ++i) {
        m[i][row] *= scale;
    }
}

void scale_and_subtract_below_row(float4 * m, int length, int row) {
    for (int j = row + 1; j < 4; ++j) {
        float scale = -m[row][j] / m[row][row];

        for (int i = row; i < length; ++i) {
            m[i][j] += scale * m[i][row];
        }
    }
}

void scale_and_subtract_above_row(float4 * m, int length, int row) {
    for (int j = row - 1; j >= 0; --j) {
        float scale = -m[row][j] / m[row][row];

        for (int i = row; i < length; ++i) {
            m[i][j] += scale * m[i][row];
        }
    }
}

float2 solve_quadratic(float a, float b, float c) {
    if (a == 0.f) {
        return solve_linear(b, c);
    }
    else {
        return solve_quadratic_(a, b, c);
    }
}

float2 solve_linear(float b, float c) {
    if (b == 0.f) { return (float2)(NAN); }

    return (float2)(-c/b);
}

float2 solve_quadratic_(float a, float b, float c) {
    float d = b * b - 4.f * a * c;
    if (d < 0.f) { return (float2)(NAN); }

    a *= 2.f;
    b = -b;

    if (d == 0.f) {
        return (float2)(b / a);
    }
    else {
        d = sqrt(d);

        float2 out = (float2)((b - d)/a, (b + d)/a);

        if (out.y < out.x) { return out.yx; }
        else { return out.xy; }
    }
}

float4 rational_bilinear_invert(
    Coordinate c,
    Point p00, Point p10,
    Point p01, Point p11
)
{
    // We do Gaussian elimination with pivoting to solve for parameters
    // we're going to plug into a quadratic equation

    float4 m[6] = {
        p00, p10, p01,
        (float4)(-c, (float2)(-1, 0)),
        (float4)(0, 0, 0, 1),
        -p11
    };
    
    // Scale each row so the absolute value of the largest entry is 1
    float4 max = (float4)(0, 0, 0, 0);

    for (int i = 0; i < 6; ++i) { max = fmax(max, fabs(m[i])); }
    for (int i = 0; i < 6; ++i) { m[i] /= max; }

    // Solve the matrix using pivoting
    for (int row = 0; row < 3; ++row) {
        int pivot_row = find_pivot_row(m[row], row);

        if (row != pivot_row) {
            swap_rows(m, 6, row, pivot_row);
        }

        normalize_front(m, 6, row);
        scale_and_subtract_below_row(m, 6, row);
    }

    normalize_front(m, 6, 3);

    for (int row = 1; row < 4; ++row) {
        scale_and_subtract_above_row(m, 6, row);
    }

    float quad_a = m[5].x - m[5].y * m[5].z,
          quad_b = m[4].x - m[4].y * m[5].z - m[5].y * m[4].z,
          quad_c = -m[4].y * m[4].z;

    quad_a = fabs(quad_a) < 1e-3f ? 0.f : quad_a;
    quad_b = fabs(quad_b) < 1e-3f ? 0.f : quad_b;
    quad_c = fabs(quad_c) < 1e-3f ? 0.f : quad_c;

    float2 q = solve_quadratic(quad_a, quad_b, quad_c);

    float4 out = (float4)(NAN);

    for (int i = 0; i < 2; ++i) {
        float D = q[i];

        if (isnan(D)) { continue; }

        float alpha = m[4].w + m[5].w * D;
        
        if (alpha < 1.f - 1e-3f) { continue; }

        float A = m[4].x + m[5].x * D,
            B = m[4].y + m[5].y * D,
            C = m[4].z + m[5].z * D,
            d = A + B + C + D
        ;

        if (isnan(d) || !d) { continue; }

        float r = 1.f / d,
            u = (B + D) * r,
            v = (C + D) * r;

        if (u < -1e-3f || u >= 1.f - 1e-3f) { continue; }
        if (v < -1e-3f || v >= 1.f - 1e-3f) { continue; }

        if (i == 0) {
            out.xy = (float2)(u, v);
        }
        else{
            out.zw = (float2)(u, v);
        }
    }

    if (out.z < out.z) {
        return out.zwxy;
    }
    else {
        return out;
    }
}
