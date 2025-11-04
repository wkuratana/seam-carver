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


static inline Enpixel* get_weaker_pixel_ptr(
    Enpixel* target_one, Enpixel* target_two) {
    /**
     * Returns target_one if weaker, returns target_two otherwise.
     * 
     * Returns pointers to the existing structs within the 
     * main energy_matrix buffer
     */
    if (target_one->energy < target_two->energy) {
        return target_one;
    } else {
        return target_two;
    }
}

static Enpixel* get_weakest_neighbor(
    size_t h, size_t w, Enpixel* energy_matrix, Enpixel target) {
    /**
     * Returns the weakest neighbor (from the prior row) of a pixel 
     * from the energy matrix.
     * 
     * Target cannot be in the first row.
     */
    // Y coordinate of the prior row
    size_t prev_y = target.y - 1;
    Enpixel *n1, *n2, *n3;

    // Macro to get 1D index for clarity
    #define IDX(y, x) ((y) * w + (x))

    if (target.x == 0) {  // Left edge
        n1 = &energy_matrix[IDX(prev_y, 0)];
        n2 = &energy_matrix[IDX(prev_y, 1)];
        return get_weaker_pixel_ptr(n1, n2);
    } 
    else if (target.x == w - 1) {  // Right edge
        n1 = &energy_matrix[IDX(prev_y, target.x - 1)];
        n2 = &energy_matrix[IDX(prev_y, target.x)];
        return get_weaker_pixel_ptr(n1, n2);
    }
    else {
        n1 = &energy_matrix[IDX(prev_y, target.x - 1)];
        n2 = &energy_matrix[IDX(prev_y, target.x)];
        n3 = &energy_matrix[IDX(prev_y, target.x + 1)];
        
        Enpixel* weaker = get_weaker_pixel_ptr(n1, n2);
        weaker = get_weaker_pixel_ptr(weaker, n3);
        return weaker;
    }
    #undef IDX
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
    size_t h, size_t w, int grayscale_matrix[h][w], Enpixel* energy_matrix) {
    /**
     * Returns an optimal seam (array) of pixels to be carved.
     * 
     * For each pixel in each row, the energy of said pixel is calculated
     * using sobel operators. Then, that energy is summed with the lowest
     * energy of neighboring pixels of the prior row.
     */
    // Seam of energy pixels to be carved
    Enpixel* seam = calloc(h, sizeof(Enpixel));
    if (seam == NULL) {
        perror("Failed to allocate seam.");
        free(energy_matrix);
        return NULL; 
    }

    #define IDX(y, x) ((y) * w + (x))
    
    for (size_t i = 0; i < h; i++) {
        for (size_t j = 0; j < w; j++) {  // For each pixel
            Enpixel* current_pixel_ptr = &energy_matrix[IDX(i, j)];

            current_pixel_ptr->y = i;
            current_pixel_ptr->x = j;
            current_pixel_ptr->weakest_neighbor = NULL;

            current_pixel_ptr->energy = calculate_energy(
                h, w, grayscale_matrix, *current_pixel_ptr);

            if (i > 0) {  // If not on first row (there are previous neighbors)
                current_pixel_ptr->weakest_neighbor = get_weakest_neighbor(
                    h, w, energy_matrix, *current_pixel_ptr);
                current_pixel_ptr->energy += (
                    current_pixel_ptr->weakest_neighbor->energy);
            }
            // Update energy
        }
    }
    
    // Get weakest pixel of last row; the energies of the pixels in the 
    // last row be have the sum of all energy from the weakest seam 
    // ending at said pixels
    Enpixel* weakest = &energy_matrix[IDX(h - 1, 0)]; 
    for (size_t j = 1; j < w; j++) {
        Enpixel* pixel_ptr = &energy_matrix[IDX(h - 1, j)];
        if (pixel_ptr->energy < weakest->energy) {
            weakest = pixel_ptr;
        }
    }
    Enpixel* current_seam_pixel_ptr = weakest;
    seam[h - 1] = *current_seam_pixel_ptr; // Copy struct values into seam

    for (size_t i = 1; i < h; i++) {
        // Traverse up the chain using the stored pointer links
        current_seam_pixel_ptr = current_seam_pixel_ptr->weakest_neighbor; 
        seam[h - 1 - i] = *current_seam_pixel_ptr;
    }

    #undef IDX

    return seam;
}

void carve(
    size_t h, size_t w, int grayscale_matrix[h][w], size_t target_width) {
    // TODO: Change matrix passed to be the rgb matrix, then turn it grayscale
    size_t current_width = w;
    // Matrix that will store energy pixels that will determine seam; 1D array
    Enpixel* energy_matrix = calloc(h * w, sizeof(Enpixel));
    if (energy_matrix == NULL) {
        perror("Failed to allocate energy_matrix.");
        return NULL;
    }
    while (current_width > target_width) {
        Enpixel* seam = get_seam(h, w, grayscale_matrix[h][w], energy_matrix);
        // TODO: Remove seam from rgb matrix
        // TODO: Remove seam from energy_matrix and update energy values
        // along seam neighbors
        current_width--;
        free(seam);
    }
    free(energy_matrix);
}
