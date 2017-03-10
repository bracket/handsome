#include <stdio.h>

typedef struct {
    unsigned char R, G, B, A;
} Pixel;

void fill(Pixel * image, int width, int height) {
    Pixel white = { 255, 255, 255, 255 };

    for (int i = 0; i < width; ++i) {
        for (int j = 0; j < height; ++j) {
            image[j * width + i] = white;
        }
    }
}

void test() {
    printf("Weasel weasel\n");
}
