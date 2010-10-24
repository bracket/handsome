#pragma once

#include "SampleBuffer.hpp"

SampleBuffer make_box_kernel(int width, int height, float value) {
	SampleBuffer out(width, height);
	Sample s(value, value, value, value);

	for (int j = 0; j < height; ++j) {
		for (int i = 0; i < width; ++i) { out(i, j) = s; }
	}

	return out;
}
