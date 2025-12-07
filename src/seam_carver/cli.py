# Imports
import numpy as np
import time
import typer
from typing_extensions import Annotated
from PIL import Image
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from .wrapper import c_carve  # type: ignore
# from .wrapper import c_expand  # type: ignore


app = typer.Typer(add_completion=False)

@app.command()
def adjust(
    # Necessary arguments
    input_file: Annotated[str, typer.Argument(
        help="Path to the input image file"
    )],
    output_file: Annotated[str, typer.Argument(
        help="Path to save the carved output image file"
    )],
    target_width: Annotated[int, typer.Argument(
        help="Target width for the carved image"
    )],
):
    try:
        # Open the input file
        input_img_pil = Image.open(input_file)
        input_img = np.array(input_img_pil)
        height, width, dimension = input_img.shape
        
        if width != target_width:
            print(f"Adjusting the width of [yellow]{input_file}[/yellow]")
            
            if width > target_width:
                start_time = time.time()
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    TimeElapsedColumn(),
                    transient=True,
                ) as progress:
                    progress.add_task(description="Adjusting...", total=None)
                    result_img = c_carve(input_img, target_width)
                
                elapsed = time.time() - start_time
                
                result_img_pil = Image.fromarray(result_img)
                result_img_pil.save(output_file)

                minutes = int(elapsed // 60)
                seconds = int(round(elapsed % 60))

                print(
                    f"Adjusted image successfully saved to [yellow]{output_file}[/yellow]"
                    f" in {minutes:02d}:{seconds:02d}")
                
            elif width < target_width:
                # TODO: Call expand width function once implemented
                # pass  # Temporary
                # Implemented in the same manner as the above function
                start_time = time.time()
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    TimeElapsedColumn(),
                    transient=True,
                ) as progress:
                    progress.add_task(description="Adjusting...", total=None)
                    result_img = c_expand(input_img, target_width)
                
                elapsed = time.time() - start_time
                
                result_img_pil = Image.fromarray(result_img)
                result_img_pil.save(output_file)

                minutes = int(elapsed // 60)
                seconds = int(round(elapsed % 60))

                print(
                    f"Adjusted image successfully saved to [yellow]{output_file}[/yellow]"
                    f" in {minutes:02d}:{seconds:02d}")

        else:
            print(
                "Please enter a target width that does not match"
                " the current width of the image")
    except Exception as e:
        print(f"Unable to adjust the image due to {e}")
        
def main():
    app()