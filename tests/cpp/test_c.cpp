#include <sstream>
#include <string>

struct Coordinate {
    float x, y;
};

std::ostream & operator << (std::ostream & out, Coordinate const & c) {
    return out << "[ " << c.x << ", " << c.y << " ]";
}

std::string buffer;

extern "C" {
    char const * print_coordinates(Coordinate const * coords, int size) {
        std::stringstream out;

        out << "[" << std::endl;

        for (int i = 0; i < size; ++i) {
            if (i) {
                out << "," << std::endl;
            }

            out << coords[i];
        }

        out << std::endl << "]" << std::endl;

        buffer = out.str();

        return buffer.c_str();
    }
}
