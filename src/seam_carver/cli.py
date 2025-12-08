# Imports
import librosa
import numpy as np
import soundfile as sf
import time
import typer
from typing_extensions import Annotated
from PIL import Image
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from .wrapper import c_carve  # type: ignore
from .wrapper import c_expand  # type: ignore

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
        print(f"Adjusting the width of [yellow]{input_file}[/yellow]")

        # Open the input file
        input_img_pil = Image.open(input_file)
        input_img = np.array(input_img_pil)
        height, width, dimension = input_img.shape
    
        if target_width == width:
            print(
                "[red]Error:[/red] Target width must not equal current width")
            return
        
        start_time = time.time()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            transient=True,
        ) as progress:
            progress.add_task(
                description="Adjusting...", total=None)
            if width > target_width:
                result_img = c_carve(input_img, target_width)

            elif width < target_width:
                result_img = c_expand(input_img, target_width)

        result_img_pil = Image.fromarray(result_img)
        result_img_pil.save(output_file)
        
        elapsed = time.time() - start_time

        minutes = int(elapsed // 60)
        seconds = int(round(elapsed % 60))

        print(
            "[green]Success![/green] Image saved to"
            f" [yellow]{output_file}[/yellow]")
        print(f"Processing time: {minutes:02d}:{seconds:02d}")

    except Exception as e:
         print(f"[red]Error:[/red] Unable to adjust image: {e}")
        
@app.command()
def adjust_audio(
    # Necessary arguments
    input_file: Annotated[str, typer.Argument(
        help="Path to the input audio file (wav, flac, ogg)"
    )],
    output_file: Annotated[str, typer.Argument(
        help="Path to save the carved output audio file"
    )],
    target_duration: Annotated[float, typer.Argument(
        help="Target duration in seconds for the carved audio"
    )]
):
    try:
        print(f"Loading audio from [yellow]{input_file}[/yellow]")
        
        # Load audio file
        time_series, sample_rate = librosa.load(input_file, sr=None)
        # Total samples / samples per second
        original_duration = len(time_series) / sample_rate
        
        if target_duration == original_duration:
            print(
                "[red]Error:[/red] Target duration must not equal"
                " current duration")
            return
        
        start_time = time.time()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task(
                description="Computing spectrogram...", total=None)
            
            # Compute STFT (Short-time Fourier transform)
            stft = librosa.stft(
                time_series, n_fft=2048, hop_length=512)
            magnitude = np.abs(stft)

            # Normalize magnitude to 0-255 for carving (keep linear scale)
            # (Track max_val to restore volume later)
            # Find the loudest moment in the song to make 255, silence becomes 0
            max_val = np.max(magnitude)
            mag_uint8 = (magnitude / max_val * 255).astype(np.uint8)
            
            # Stack to 3 channels for the C backend
            spectrogram_img = np.dstack([mag_uint8] * 3)

            progress.update(
                task, description="Carving spectrogram...")
            
            # Calculate target dimensions
            target_frames = int(
                stft.shape[1] * (target_duration / original_duration))
            
            # Perform Carving
            if stft.shape[1] > target_frames:
                result_img = c_carve(spectrogram_img, target_frames)
            elif stft.shape[1] < target_frames:
                result_img = c_expand(spectrogram_img, target_frames) 

            progress.update(
                task, description="Reconstructing audio...")

            # Recover carved magnitude
            # Take 0-255 pixels and shrink them back to 0.0-1.0 decimals, and mult original volume
            carved_magnitude = (
                result_img[:, :, 0].astype(np.float32) / 255.0) * max_val

            # Reconstruct audio from magnitude using Griffin-Lim
            # This estimates the phase iteratively from the spectrogram alone.
            carved_time_series = librosa.griffinlim(
                carved_magnitude, 
                n_iter=32,       # Higher iterations = better quality but slower
                hop_length=512, 
                n_fft=2048
            )
        
        sf.write(output_file, carved_time_series, sample_rate)
        
        elapsed = time.time() - start_time

        minutes = int(elapsed // 60)
        seconds = int(round(elapsed % 60))
        
        print(
            "[green]Success![/green] Audio saved to"
            f" [yellow]{output_file}[/yellow]")
        print(f"Processing time: {minutes:02d}:{seconds:02d}")
        
    except Exception as e:
        print(f"[red]Error:[/red] Unable to adjust audio: {e}")

@app.command()
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
            help="Target height for the carved image"
        )],
):
    try:
        print(f"Adjusting the width of [yellow]{input_file}[/yellow] (BLI)")

        # Open the input file
        input_img_pil = Image.open(input_file)
        # Convert to RGB to ensure 3 dimensions (handles Grayscale/RGBA safely)
        input_img_pil = input_img_pil.convert("RGB") 
        input_img = np.array(input_img_pil)
        height, width, dimension = input_img.shape

        if target_width == width:
            print(
                "[red]Error:[/red] Target width must not equal current width")
            return
        
        start_time = time.time()

        output = np.zeros((target_height, target_width, dimension), dtype=np.uint8)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            transient=True,
        ) as progress:
            progress.add_task(
                description="Adjusting...", total=None)
                
            x_scale_factor = width / target_width
            y_scale_factor = height / target_height


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
                        value = (
                            ((1 - alpha) * (1 - beta) * input_img[y1, x1, z]) 
                            + (alpha * (1 - beta) * input_img[y1, x2, z]) 
                            + ((alpha * beta) * input_img[y2, x2, z])
                            + ((1 - alpha) * beta * input_img[y2, x1, z])
                        )
                        output[y,x,z] = int(value + 0.5)

        result_img_pil = Image.fromarray(output)
        result_img_pil.save(output_file)
        
        elapsed = time.time() - start_time

        minutes = int(elapsed // 60)
        seconds = int(round(elapsed % 60))

        print(
            "[green]Success![/green] Image saved to"
            f" [yellow]{output_file}[/yellow]")
        print(f"Processing time: {minutes:02d}:{seconds:02d}")

    except Exception as e:
        print(f"[red]Error:[/red] Unable to adjust image (BLI): {e}")

def main():
    app()