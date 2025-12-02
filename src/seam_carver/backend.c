/* Imports */
#include <math.h> 
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>


/* Indexing Macros */
// Use `w` for grayscale_matrix, current_width for energy_matrix (with IDX)
#define IDX(y, x, w) ((y) * (w) + (x))  // For grayscale, energy
#define RGB_IDX(y, x, w) (((y) * (w) + (x)) * 3)  // For RGB


/* Struct */
typedef struct Enpixel {
    double energy;  // Energy value
    int y;  // Vertical coordinates
    int x;  // Horizontal coordinates
    struct Enpixel* weakest_neighbor;  // Weakest neighbor from previous row
} Enpixel;  // Energy pixel, used in energy matrix


/* Functions */
static inline int clamp(
    int value, int min, int max) {
    /**
     * Clamp coordinates to the image bounds; cleans up image edge handling.
     */
    if (value < min) return min;
    if (value > max) return max;

    return value;
}

static inline Enpixel* get_weaker_pixel_ptr(
    Enpixel* target_one, Enpixel* target_two) {
    /**
     * Returns target_one if weaker, returns target_two otherwise.
     * 
     * Returns pointers to the existing structs within the 
     * main energy_matrix buffer.
     */
    if (target_one->energy < target_two->energy) return target_one;
    
    return target_two;
}

static void convert_rgb_to_grayscale(
    size_t h, size_t w, uint8_t* rgb_matrix, int* grayscale_matrix) {
    /**
     * Converts an rgb matrix to a grayscale matrix. Fills `grayscale_matrix`.
     * 
     * Uses NTSC coefficients for luminance.
     */
    for (size_t i = 0; i < h; i++) {
        for (size_t j = 0; j < w; j++) {
            size_t idx = RGB_IDX(i, j, w);
            grayscale_matrix[IDX(i, j, w)] = (int)(
                0.299 * rgb_matrix[idx + 0] + // R
                0.587 * rgb_matrix[idx + 1] + // G
                0.114 * rgb_matrix[idx + 2]   // B
            );
        }
    }
}

static Enpixel* get_weakest_neighbor(
    size_t h, size_t current_width, Enpixel* energy_matrix, Enpixel target) {
    /**
     * Returns the weakest neighbor (from the prior row) of a pixel 
     * from the energy matrix.
     * 
     * Target cannot be in the first row.
     */
    // Y coordinate of the prior row
    size_t prev_y = target.y - 1;
    Enpixel *n1, *n2, *n3;

    if (target.x == 0) {  // Left edge
        n1 = &energy_matrix[IDX(prev_y, 0, current_width)];
        n2 = &energy_matrix[IDX(prev_y, 1, current_width)];
        
        return get_weaker_pixel_ptr(n1, n2);
    } 
    else if (target.x == current_width - 1) {  // Right edge
        n1 = &energy_matrix[IDX(prev_y, target.x - 1, current_width)];
        n2 = &energy_matrix[IDX(prev_y, target.x, current_width)];

        return get_weaker_pixel_ptr(n1, n2);
    }
    else {
        n1 = &energy_matrix[IDX(prev_y, target.x - 1, current_width)];
        n2 = &energy_matrix[IDX(prev_y, target.x, current_width)];
        n3 = &energy_matrix[IDX(prev_y, target.x + 1, current_width)];
        
        Enpixel* weaker = get_weaker_pixel_ptr(n1, n2);
        weaker = get_weaker_pixel_ptr(weaker, n3);

        return weaker;
    }
}

static double calculate_energy(
    size_t h, size_t w, size_t current_width, 
    int* grayscale_matrix, Enpixel target) {
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
            // Find neighbor's coords with clamping to handle edges
            int offset_y = target.y + i;
            int offset_x = target.x + j;
            int neighbor_y = clamp(offset_y, 0, h - 1);
            int neighbor_x = clamp(offset_x, 0, current_width - 1);
            double pixel_value = grayscale_matrix[IDX(
                neighbor_y, neighbor_x, w)];
            sum_y = sum_y + (pixel_value * y_kernel[i + 1][j + 1]);
            sum_x = sum_x + (pixel_value * x_kernel[i + 1][j + 1]);
        }
    }

    return sqrt((sum_x * sum_x) + (sum_y * sum_y));
}


static Enpixel* set_energy_matrix(
    size_t h, size_t w, size_t current_width, 
    int* grayscale_matrix, Enpixel* energy_matrix) {
    /**
     * For each pixel in each row, the energy of said pixel is calculated
     * using sobel operators. Then, that energy is summed with the lowest
     * energy of neighboring pixels of the prior row.
     * 
     * Also locates the weakest neighbor of each pixel, starting from
     * the second (i = 1) row.
     */
    for (size_t i = 0; i < h; i++) {
        for (size_t j = 0; j < current_width; j++) {  // For each pixel
            Enpixel* current_pixel_ptr = &energy_matrix[IDX(
                i, j, current_width)];
            current_pixel_ptr->y = i;
            current_pixel_ptr->x = j;
            current_pixel_ptr->weakest_neighbor = NULL;
            current_pixel_ptr->energy = calculate_energy(
                h, w, current_width, grayscale_matrix, *current_pixel_ptr);
            if (i > 0) {  
                // If not on first row (i.e. there are previous neighbors)...
                current_pixel_ptr->weakest_neighbor = get_weakest_neighbor(
                    h, current_width, energy_matrix, *current_pixel_ptr);
                // Update energy
                current_pixel_ptr->energy += (
                    current_pixel_ptr->weakest_neighbor->energy);
            }
        }
    }

    return energy_matrix;
}

static Enpixel* get_seam(
    size_t h, size_t current_width, Enpixel* energy_matrix) {
    /**
     * Returns an optimal seam (array) of pixels to be carved.
     */
    // Seam of energy pixels to be carved
    Enpixel* seam = calloc(h, sizeof(Enpixel));
    if (seam == NULL) {
        perror("Failed to allocate seam.");

        return NULL; 
    }
    // Get weakest pixel of last row (containing lowest seam sum)
    Enpixel* weakest = &energy_matrix[IDX(h - 1, 0, current_width)]; 
    for (size_t j = 1; j < current_width; j++) {
        Enpixel* pixel_ptr = &energy_matrix[IDX(h - 1, j, current_width)];
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

    return seam;
}

static void remove_seam(
    size_t h, size_t w, size_t current_width, 
    Enpixel* seam, int* grayscale_matrix, uint8_t* rgb_matrix) {
    /**
     * Removes the pixels at the coordinates specified by the Enpixels in the
     * seam.
     */
    for (size_t i = 0; i < h; i++) {
        Enpixel pixel = seam[i];
        size_t y = pixel.y;
        size_t x = pixel.x;

        // Shift all pixels from (x + 1) to (current_width - 1).
        size_t num_pixels_to_move = current_width - 1 - x;

        if (num_pixels_to_move > 0) {
            // Pointer to the destination (the pixel to be removed)
            int* gray_dest = &grayscale_matrix[IDX(y, x, w)];
            // Pointer to the source (pixel to the right)
            int* gray_src = &grayscale_matrix[IDX(y, x + 1, w)];
            memmove(
                gray_dest, gray_src, num_pixels_to_move * sizeof(int));

            uint8_t* rgb_dest = &rgb_matrix[RGB_IDX(y, x, w)];
            uint8_t* rgb_src = &rgb_matrix[RGB_IDX(y, x + 1, w)];
            
            // (num_pixels_to_move * 3) is the number of bytes
            memmove(
                rgb_dest, rgb_src, num_pixels_to_move * 3 * sizeof(uint8_t));
        }
    }
}

int carve(
    size_t h, size_t w, uint8_t* rgb_matrix, size_t target_width) {
    /**
     * Carves out low-energy seams from an image matrix until its width
     * reaches `target_width`.
     * 
     * If used with a Cython script, any image passed will point directly
     * to the NumPy array's data buffer. This function shuffles the data 
     * around inside said buffer.
     * 
     * Remember to slice the array in Python to see the proper results!
     * 
     * Note that `w` is original width.
     */
    size_t current_width = w;

    int* grayscale_matrix = calloc(h * w, sizeof(int));
    if (grayscale_matrix == NULL) {
        perror("Failed to allocate grayscale_matrix.");

        return -1;
    }
    convert_rgb_to_grayscale(h, w, rgb_matrix, grayscale_matrix);

    while (current_width > target_width) {
        // Matrix of energy pixels that will determine seam
        Enpixel* energy_matrix = calloc(h * current_width, sizeof(Enpixel));
        if (energy_matrix == NULL) {
            perror("Failed to allocate energy_matrix.");
            free(grayscale_matrix);

            return -1;
        }
        energy_matrix = set_energy_matrix(
            h, w, current_width, grayscale_matrix, energy_matrix);
        // Seam to carve from image
        Enpixel* seam = get_seam(h, current_width, energy_matrix);
        if (seam == NULL) {
            perror("Failed to allocate seam.");

            free(grayscale_matrix);
            free(energy_matrix);
            return -1;
        }
        // Remove the seam from the grayscale matrix and the original matrix
        remove_seam(
            h , w, current_width, seam, grayscale_matrix, rgb_matrix);
        free(energy_matrix);
        free(seam);
        current_width--;
    }

    free(grayscale_matrix);

    return 0;
}
