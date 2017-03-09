//  void sample_texture_to_mesh(
//    MeshPoint * mesh, int mesh_width, int mesh_height,
//    Sample const * texture,  int texture_width, int texture_height
//  )

for (int j = 0; j < mesh_height; ++j) {
    float t = static_cast<float>(j) / static_cast<float>(mesh_height - 1);

    for (int i = 0; i < mesh_width; ++i) {
        float s = static_cast<float>(i) / static_cast<float>(mesh_width - 1);

        (mesh + j * mesh_width + i)->color
          = sample_texture(&cast_vec(*texture), texture_width, texture_height, s, t);
        // (mesh + j * mesh_width + i)->color = green;
    }
}
