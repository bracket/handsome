#pragma once

#include "Vec.hpp"

struct SampleBuffer;
struct TileCache;

void convolve_into(
	SampleBuffer & out,
	SampleBuffer const & in,
	SampleBuffer const & kernel,
	Vec<2, int> const & out_offset,
	Vec<2, int> const & in_offset,
	int out_sample_rate,
	int in_sample_rate
);

void convolve_into(
	SampleBuffer & out,
	TileCache const & cache,
	SampleBuffer const & kernel,
	int out_sample_rate
);
