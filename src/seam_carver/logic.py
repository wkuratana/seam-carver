# Imports
import math
import numpy as np
from PIL import Image


def load_image(path: str):
    """
    Loads an image from a file path into an matrix.

    Args:
        path (str): Image path.
    """
    img: Image.Image = Image.open(path)
    return np.asarray(img, dtype=np.uint8) 

def save_image(img_matrix, path: str):
    """
    Saves an matrix as an image.

    Args:
        img_matrix: Numpy nested image array.
        path (str): Image path.
    """
    img: Image.Image = Image.fromarray(img_matrix)
    img.save(path)

def _to_grayscale(img_matrix):
    """
    Converts a 3-channel (H, W, 3) RGB matrix to a 2-channel (H, W) 
    grayscale matrix using the luminance formula.

    Args:
        img_matrix: Numpy nested image array.
    """
    # If image is already 2D (grayscale), convert to float
    if img_matrix.ndim == 2:
        return img_matrix.astype(np.float64)
    
    img_matrix_float = img_matrix.astype(np.float64)
    
    # NTSC coefficients for luminance
    luminance_weights = np.array([0.299, 0.587, 0.114])

    # Mult the last axis of img_matrix (the 3 color channels)
    # by the luminance_weights and sum them, resulting in a (H, W) matrix
    return np.dot(img_matrix_float, luminance_weights)

def compute_energy(img_matrix):
    """
    Computes an energy map of the image and returns it as an matrix.
    
    Args:
        img_matrix: Numpy nested image array.

    Returns:
        energy_matrix: A new matrix of the original image's energy map.
    """
    grayscale_img = _to_grayscale(img_matrix)

    height: int = grayscale_img.shape[0]
    width: int = grayscale_img.shape[1]  # .shape → (height, width, channels)

    output_energy_matrix = np.zeros((height, width), dtype=np.float64)

    # Sobel operator for edge detection
    x_kernel = np.array([
        [-1, 0, 1],
        [-2, 0 ,2],
        [-1, 0, 1]
    ], dtype=np.float64)

    y_kernel = np.array([
        [-1, -2, -1],
        [0, 0, 0],
        [1, 2, 1]
    ], dtype=np.float64)
    
    for y in range(height):
        for x in range(width):
            sum_x = sum_y = 0.0
            for i in range(-1, 2):  # i will be -1, 0, 1
                for j in range(-1, 2):  # j will be -1, 0, 1
                    # Find neighbor's coords with wrapping to handle edges
                    pixel_y = (y + i) % height
                    pixel_x = (x + j) % width

                    pixel_value = grayscale_img[pixel_y, pixel_x]

                    # (i+1, j+1) maps from (-1, -1) to (0, 0)
                    sum_x += pixel_value * x_kernel[i + 1, j + 1]
                    sum_y += pixel_value * y_kernel[i + 1, j + 1]

            # Magnitude of the 2D gradient vector
            output_energy_matrix[y, x] = math.sqrt(
                (sum_x * sum_x) + (sum_y * sum_y))
    return output_energy_matrix

def find_seam(energy_matrix):
    """
    Returns 1D array of indices for the seam with the least energy.
    
    Args:
        energy_matrix: A matrix of the image's energy map.

    Returns:
        seam: Array of indices for the seam with the least energy.
    """
    height: int = energy_matrix.shape[0]
    width: int = energy_matrix.shape[1]  # .shape → (height, width, channels)

    # Array of directions for final seam
    # -1 for 'up-left', 0 for 'up', 1 for 'up-right'
    dir_matrix = np.zeros((height, width), dtype=np.int32)
    # Array of cumulative energies
    cumul_matrix = np.zeros((height, width), dtype=np.float64)

    # Copy the first row directly from the energy matrix
    cumul_matrix[0, :] = energy_matrix[0, :] 

    # Iterate from the second row (y=1) downwards
    for y in range(1, height):
        for x in range(width):
            if x == 0:  # Left edge
                # Two parents: (y-1, 0) and (y-1, 1)
                parents = [cumul_matrix[y-1, x], cumul_matrix[y-1, x+1]]
                min_parent_energy = min(parents)
                # np.argmin gives 0 or 1; map 0 to 0, 1 to 1
                direction = np.argmin(parents) 
            elif x == (width - 1):  # Right edge
                # Two parents: (y-1, x-1) and (y-1, x)
                parents = [cumul_matrix[y-1, x-1], cumul_matrix[y-1, x]]
                min_parent_energy = min(parents)
                # np.argmin gives 0 or 1; map 0 to -1, 1 to 0
                direction = np.argmin(parents) - 1 
            else:
                # Three parents: (y-1, x-1), (y-1, x), (y-1, x+1)
                parents = [
                    cumul_matrix[y-1, x-1], 
                    cumul_matrix[y-1, x], 
                    cumul_matrix[y-1, x+1]
                ]
                min_parent_energy = min(parents)
                # np.argmin gives 0, 1, or 2; map this to -1, 0, or 1
                direction = np.argmin(parents) - 1

            # Cumul. energy is this pixel's energy + its min parent's energy
            cumul_matrix[y, x] = energy_matrix[y, x] + min_parent_energy
            dir_matrix[y, x] = direction
    # Array to store the x-indices of the seam
    seam = np.zeros(height, dtype=np.int32)

    # Find the x-index of the minimum value in the last row
    min_x = np.argmin(cumul_matrix[height - 1, :])
    seam[height - 1] = min_x

    # Loop backwards from the second-to-last row up to the top
    current_x = min_x
    for y in range(height - 2, -1, -1):
        direction = dir_matrix[y + 1, current_x]  # Direction for pixel below
        # X-coord for this row is the pixel below's x + its direction
        current_x = current_x + direction
        seam[y] = current_x
    return seam

def remove_seam(img_matrix, seam):
    """
    Removes a single vertical seam from an image matrix.

    Args:
        img_matrix: The (H, W, 3) image array.
        seam: Array of indices for the seam with the least energy.

    Returns:
        A new (H, W-1, 3) image array with the seam removed.
    """
    height: int = img_matrix.shape[0]
    width: int = img_matrix.shape[1]    
    # Create an empty array to hold the new image
    new_img = np.zeros((height, width - 1), dtype=img_matrix.dtype)

    # Handle 3D (color) images
    if img_matrix.ndim == 3:
        channels: int = img_matrix.shape[2]
        new_img = np.zeros((height, width - 1, channels), dtype=img_matrix.dtype)
        
        for y in range(height):
            seam_x = seam[y]
            # Copy pixels before the seam
            new_img[y, :seam_x, :] = img_matrix[y, :seam_x, :]
            # Copy pixels after the seam
            new_img[y, seam_x:, :] = img_matrix[y, seam_x + 1:, :]
            
    # Handle 2D (grayscale) images
    else: 
        new_img = np.zeros((height, width - 1), dtype=img_matrix.dtype)
        
        for y in range(height):
            seam_x = seam[y]
            # Copy pixels before the seam
            new_img[y, :seam_x] = img_matrix[y, :seam_x]
            # Copy pixels after the seam
            new_img[y, seam_x:] = img_matrix[y, seam_x + 1:]
        
    return new_img

def carve(target_width: int, image_path: str, new_image_path: str):
    """
    Runs seam carving algorithm on the image until target width is reached.

    Args:
        width (int): Target image width.
        image_path (str): Image path.
        new_image_path (str): Path for newly resized image.
    """
    img_matrix = load_image(image_path)
    # TODO: This is currently incorrect, but it will work for now;
    # Ideally, because the energy values of pixels are dependent on their
    # neighbors, the energy should be recalculated along the removed seam
    # every time a seam is removed
    energy_matrix = compute_energy(img_matrix)

    current_width: int = img_matrix.shape[1]

    while current_width > target_width:
        seam = find_seam(energy_matrix)
        # Update img_matrix with the newly carved image
        img_matrix = remove_seam(img_matrix, seam) 
        energy_matrix = remove_seam(energy_matrix, seam)
        # Update the current width for the next loop check
        current_width = img_matrix.shape[1] 

    save_image(img_matrix, new_image_path)

