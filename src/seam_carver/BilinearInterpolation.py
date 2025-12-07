import numpy as np
import time
import typer
from typing_extensions import Annotated
from PIL import Image
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

def bilinear_interpolation(
        input_file: Annotated[str, typer.Argument(
            help="Path to the input image file"
        )],
        output_file: Annotated[str, typer.Argument(
            help="Path to save the carved output image file"
        )],
        target_width: Annotated[int, typer.Argument(
            help="Target width for the carved image"
        )],
        target_height: Annotated[int, typer.Argument(
            help="Target width for the carved image"
        )],
):
    try:
        # Open the input file
        input_img_pil = Image.open(input_file)
        input_img = np.array(input_img_pil)
        height, width, dimension = input_img.shape

        x_scale_factor = width/target_width
        y_scale_factor = height / target_height

        output = np.zeros(target_width,target_height)

        for y in range(target_height):
            for x in range(target_width):
                xOrigin = x * x_scale_factor
                yOrigin = y * y_scale_factor

                #Coordinates, clamping for the edges
                x1 = int(xOrigin)
                y1 = int(yOrigin)
                x2 = min(x1+1, width-1) 
                y2 = min(y1+1, height-1) 

                # Interpolation Coefficients
                alpha = xOrigin - x1
                beta = yOrigin - y1

                for z in range(dimension):
                    output[y,x,z] = (
                        (1-alpha)(1-beta)(input_img[y1,x1,z]) 
                        + alpha(x1)(1-beta)(input_img[y1,x2,z]) 
                        + (alpha*beta)(y1,x1,z)
                        + (1-alpha)(beta)(y2,x1,z)
                    )
    except Exception as e:
        print(f"Unable to adjust the image due to {e}")

    return output




