#ifndef BACKEND_H
#define BACKEND_H
#include <stdint.h>
#include <stdlib.h>

// Only function to be used with Cython
int carve(size_t h, size_t w, uint8_t* rgb_matrix, size_t target_width);

#endif