// Imports
#include <math.h>  // fmin, fmod
#include <stdio.h>
#include <stdlib.h>  // calloc

typedef struct Enpixel {
    double energy;  // Energy value
    int y;  // Vertical coordinates
    int x;  // Horizontal coordinates
    struct Enpixel* weakest_neighbor;  // Neighbor from previous row
    // TODO: Maybe use a separate path matrix instead of weakest_neighbor?
} Enpixel;  // Energy pixel, used in energy matrix

static inline Enpixel choose_weaker(Enpixel target_one, Enpixel target_two) {
    /**
     * Returns target_one if weaker, returns target_two otherwise.
     */
    if (target_one.energy < target_two.energy) {
        return target_one;
    }
    else {
        return target_two;
    }
} 

static Enpixel* get_weakest_neighbor(
    size_t h, size_t w, int grayscale_matrix[h][w], Enpixel target) {
    /**
     * Returns the weakest neighbor (from the prior row) of a pixel 
     * from the energy matrix.
     * 
     * Target cannot be in the first row.
     */
    if (target.x == 0) {  // Left edge
        // Two vertical neighbors: (y-1, 0) and (y-1, 1)
        Enpixel zero_neighbor;
        Enpixel pos_neighbor;
        
    } 
    else if (target.x == w - 1) {  // Right edge
        // Two vertical neighbors: (y-1, x-1) and (y-1, x)
        Enpixel neg_neighbor;
        Enpixel zero_neighbor;
    }
    else {
        // Three vertical neighbors: (y-1, x-1), (y-1, x), (y-1, x+1)
        Enpixel neg_neighbor;
        Enpixel zero_neighbor;
        Enpixel pos_neighbor;
    }
}

static double calculate_energy(
    size_t h, size_t w, int grayscale_matrix[h][w], Enpixel target) {
    /**
     * Returns the energy value of a given pixel based off of it and its
     * neighbors.
     */
    // Sobel operator for edge detection
    const int x_kernel[3][3] = {
        {-1, 0, 1}, 
        {-2, 0, 2},
        {-1, 0, 1}
    };
    const int y_kernel[3][3] = {
        {-1, -2, -1},
        {0, 0 ,0},
        {1, 2, 1}
    };
    double sum_y = 0;
    double sum_x = 0;
    for (int i = -1; i < 2; i++) {
        for (int j = -1; j < 2; j++) {
            // Find neighbor's coords with wrapping to handle edges
            int offset_y = target.y + i;
            int offset_x = target.x + j;
            int neighbor_y = (int)fmod((fmod(offset_y, h) + h), h);
            int neighbor_x = (int)fmod((fmod(offset_x, w) + w), w);
            double pixel_value = grayscale_matrix[neighbor_y][neighbor_x];
            sum_y = sum_y + (pixel_value * y_kernel[i + 1][j + 1]);
            sum_x = sum_x + (pixel_value * x_kernel[i + 1][j + 1]);
        }
    }
    return sqrt((sum_x * sum_x) + (sum_y * sum_y));
}

static struct Enpixel* get_seam(
    size_t h, size_t w, int grayscale_matrix[h][w]) {
    /**
     * Returns an optimal seam (array) of pixels to be carved.
     * 
     * For each pixel in each row, the energy of said pixel is calculated
     * using sobel operators. Then, that energy is summed with the lowest
     * energy of neighboring pixels of the prior row.
     */

    // TODO: Probably move the energy_matrix allocation out of this function
    // so it isn't responsible for freeing up the memory (it'll be reused)
    // Also calloc can probably just be malloc

    // Matrix that will store energy pixels that will determine seam; 1D array
    Enpixel* energy_matrix = calloc(h * w, sizeof(Enpixel));
    if (energy_matrix == NULL) {
        perror("Failed to allocate energy_matrix.");
        return NULL;
    }
    // Seam of energy pixels to be carved
    Enpixel* seam = calloc(h, sizeof(Enpixel));
    if (seam == NULL) {
        perror("Failed to allocate seam.");
        free(energy_matrix);
        return NULL; 
    }

    for (size_t i = 0; i < h; i++) {
        for (size_t j = 0; j < w; j++) {  // For each pixel
            Enpixel pixel = {0, i, j, NULL};
            pixel.energy = calculate_energy(
                h, w, grayscale_matrix, pixel);
            energy_matrix[i * w + j] = pixel;
            if (i > 0) {  // If not on first row (there are previous neighbors)
                pixel.weakest_neighbor = get_weakest_neighbor(
                    h, w, grayscale_matrix, pixel);
            }
            // Update energy            
        }
    }
    return seam;
}
