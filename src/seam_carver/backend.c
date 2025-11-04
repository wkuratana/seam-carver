// Imports
#include <math.h>
#include <stdio.h>
#include <stdlib.h>  // calloc

typedef struct Enpixel {
    float energy;  // Energy value
    int x;  // Horizontal coordinates
    int y;  // Vertical coordinates
    struct Enpixel* weakest_neighbor;  // Neighbor from previous row
    // Maybe use a separate path matrix instead of weakest_neighbor
} Enpixel;  // Energy pixel, used in energy matrix

struct Enpixel* get_seam(size_t height, size_t width, int grayscale_matrix[height][width]) {
    /**
     * Returns an optimal seam (array) of pixels to be carved.
     * 
     * For each pixel in each row, the energy of said pixel is calculated
     * using sobel operators. Then, that energy is summed with the lowest
     * energy of neighboring pixels of the prior row.
     */
    // Allocate memory
    Enpixel* energyMatrix = calloc(height * width, sizeof(Enpixel));
    if (energyMatrix == NULL) {
        perror("Failed to allocate energyMatrix.");
        return NULL;
    }
    Enpixel* seam = calloc(height, sizeof(Enpixel));
    if (seam == NULL) {
        perror("Failed to allocate seam.");
        free(energyMatrix);
        return NULL; 
    }
    // Sobel operator for edge detection
    const int xKernel[3][3] = {
        {-1, 0, 1}, 
        {-2, 0, 2},
        {-1, 0, 1}
    };
    const int yKernel[3][3] = {
        {-1, -2, -1},
        {0, 0 ,0},
        {1, 2, 1}
    };
    // Logic
    for (size_t i = 0; i < height; i++) {
        for (size_t j = 0; j < width; j++) {

        };
    };
    return seam;
}
