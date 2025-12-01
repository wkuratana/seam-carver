# Imports
import numpy as np
import os
from PIL import Image
from .wrapper import c_carve  # type: ignore


def test_1(input_file_name, output_file_name):
    input_img_pil = Image.open(
        os.path.join('assets', input_file_name))
    input_img = np.array(input_img_pil) #

    h, w, _ = input_img.shape
    target_w = w - (w // 2)

    print(f"Original shape: {input_img.shape}")
    print("Carving...")
    result_img = c_carve(input_img, target_w)
    print(f"New shape: {result_img.shape}")

    # Convert the resulting NumPy array back to a PIL Image object
    result_img_pil = Image.fromarray(result_img)

    # Save image using Pillow
    result_img_pil.save(
        os.path.join('assets', output_file_name))


def main():
    test_1('surfer.jpg', 'narrow_surfer.jpg')