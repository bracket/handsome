#include "Integer.hpp"
#include "SampleBuffer.hpp"
#include <cstring>

namespace {
	inline uint16 make_magic_number(char const * ptr) {
		return *reinterpret_cast<uint16 const *>(ptr);
	}

	struct BitmapHeader {
		BitmapHeader() {
			std::memset(data_, 0, sizeof(data_));
			magic_number() = make_magic_number("BM");
		}

		uint16 & magic_number() { return *reinterpret_cast<uint16*>(data_); }
		uint32 & size() { return *reinterpret_cast<uint32*>(data_ + 2); }
		uint32 & reserved() { return *reinterpret_cast<uint32*>(data_ + 6); }
		uint32 & offset() { return *reinterpret_cast<uint32*>(data_ + 10); }

		private:
			uint8 data_[14];
	};

	struct BitmapInfo {
		BitmapInfo() {
			std::memset(this, 0, sizeof(*this));
			header_sz = sizeof(*this);
		}

		uint32 header_sz;
		uint32 width;
		uint32 height;
		uint16 nplanes;
		uint16 bitspp;
		uint32 compress_type;
		uint32 bmp_bytesz;
		uint32 hres;
		uint32 vres;
		uint32 ncolors;
		uint32 nimpcolors;
	};

	BitmapInfo make_info(uint32 width, uint32 height) {
		BitmapInfo info;
		info.width = width;
		info.height = height;
		info.nplanes = 1;
		info.bitspp = 32;
		info.compress_type = 0;
		info.vres = 1;
		info.hres = 1;

		return info;
	}
}

void write_bitmap(char const * path, SampleBuffer const & buffer) {
	FILE * fd = fopen(path, "wb");

	BitmapHeader header;
	BitmapInfo info = make_info(buffer.get_width(), buffer.get_height());

	header.size() = sizeof(header) + sizeof(info) + buffer.get_size() * sizeof(uint32);
	header.offset() = sizeof(header) + sizeof(info);

	fwrite(&header, sizeof(header), 1, fd);
	fwrite(&info, sizeof(info), 1, fd);
	buffer.write_bitmap(fd);

	fclose(fd);
}
