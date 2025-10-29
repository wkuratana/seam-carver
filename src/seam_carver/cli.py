# Imports
import numpy as np
from .logic import load_image, save_image, compute_energy

def main():
    print("Hello from the seam_carver CLI!")
    # file_name = 'assets/drpepper.jpg'
    # final_file_name = 'assets/sobel.jpg'

    # array = load_image(file_name)
    # energy_array = compute_energy(array)

    # # For testing purposes, normalize it 
    # # (scale all values to fit between 0.0 and 1.0)
    # max_val = np.max(energy_array)
    # min_val = np.min(energy_array)
    # normalized_map = (energy_array - min_val) / (max_val - min_val)

    # # Scale to 0-255 and convert to uint8
    # uint8_energy_map = (normalized_map * 255).astype(np.uint8)

    # save_image(uint8_energy_map, final_file_name)
