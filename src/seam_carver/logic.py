# Imports
import math
import numpy as np
from PIL import Image


def load_image(path: str):
    """
    Loads an image from a file path into an array.

    Args:
        path (str): Image path.
    """
    img: Image.Image = Image.open(path)
    return np.asarray(img, dtype=np.uint8) 

def save_image(img_array, path: str):
    """
    Saves an array as an image.

    Args:
        img_array: Numpy image array.
        path (str): Image path.
    """
    img: Image.Image = Image.fromarray(img_array)
    img.save(path)

def _to_grayscale(img_array):
    """
    Converts a 3-channel (H, W, 3) RGB array to a 2-channel (H, W) 
    grayscale array using the luminance formula.

    Args:
        img_array: Numpy image array.
    """
    # Ensure the array is float64 for the math
    img_array_float = img_array.astype(np.float64)
    # The standard NTSC coefficients for luminance
    luminance_weights = np.array([0.299, 0.587, 0.114])
    # Multiply the last axis of img_array (the 3 color channels)
    # by the luminance_weights and sum them, resulting in a (H, W) array
    return np.dot(img_array_float, luminance_weights)

def compute_energy(img_array):
    """
    Computes an energy map of the image and returns it as an array.
    
    Args:
        img_array: Numpy image array.

    Returns:
        energy_array: A new array of the original image's energy map.
    """
    grayscale_img = _to_grayscale(img_array)

    height: int = grayscale_img.shape[0]
    width: int = grayscale_img.shape[1]  # .shape → (height, width, channels)

    output_energy_array = np.zeros((height, width), dtype=np.float64)

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

                    # Get grayscale value of the neighbor
                    pixel_value = grayscale_img[pixel_y, pixel_x]

                    # (i+1, j+1) maps from (-1, -1) -> (0, 0)
                    sum_x += pixel_value * x_kernel[i + 1, j + 1]
                    sum_y += pixel_value * y_kernel[i + 1, j + 1]

            # Magnitude of the 2d gradient vector
            output_energy_array[y, x] = math.sqrt((sum_x * sum_x) + (sum_y * sum_y))

    return output_energy_array

def carve(img_array, width: int):
    """
    Runs seam carving algorithm on the image until target width is reached.

    Args:
        img_array: Numpy image array.
        width (int): Target image width.
    """
    energy_array = compute_energy(img_array)
