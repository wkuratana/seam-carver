from libc.stdint cimport uint8_t
cdef extern from "backend.h":
    int carve(size_t h, size_t w, uint8_t rgb_matrix, size_t target_width)

def carve(h:size_t, w:size_t, rgb_matrix:uint8_t,target_width:size_t) -> int:
    return carve(h,w,rgb_matrix,target_width)

#these may be unnecessary

cdef struct Enpixel:
    double energy
    int x
    int y
    #figure out how to declare structs for weakest_neighbor

cdef int clamp(int value, int min, int max)

cdef Enpixel get_weaker_pixel_ptr(Enpixel* target_one, Enpixel* target_two)

cdef void convert_rgb_to_grayscale(size_t h, size_t w, uint8_t* rgb_matrix, int* grayscale_matrix)
    #figure out how to wrap the array

cdef Enpixel* get_weakest_neighbor(size_t h, size_t current_width, Enpixel* energy_matrix, Enpixel target)

cdef double calculate_energy(size_t h, size_t w, size_t current_width, int* grayscale_matrix, Enpixel target)

cdef Enpixel* set_energy_matrix(size_t h, size_t w, size_t current_width, int* grayscale_matrix, Enpixel* energy_matrix)

cdef Enpixel* get_seam(size_t h, size_t current_width, Enpixel* energy_matrix)

cdef void remove_seam(size_t h, size_t w, size_t current_width, Enpixel* seam, int* grayscale_matrix, uint8_t* rgb_matrix)
    #figure out how to wrap the array
