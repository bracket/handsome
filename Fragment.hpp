#pragma once

#include "Vec.hpp"

struct Fragment {
	Vec<2, float> position;
	Vec<2, float> interpolants;
	Vec<2, int> sample_indices;
	int sample_rate;
};
