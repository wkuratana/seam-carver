# Imports
import numpy as np
from .logic import carve

def main():
    print("Hello from the seam_carver CLI! Shrinking Dr. Pepper...")
    file_name = 'assets/drpepper.jpg'
    final_file_name = 'assets/half_width.jpg'
    target_width = int(768 / 2)
    carve(target_width, file_name, final_file_name)