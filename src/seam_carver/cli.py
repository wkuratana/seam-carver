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
# from .wrapper import c_expand  # type: ignore
# from .BilinearInterpolation import bilinear_interpolation


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
                # result_img = c_expand(input_img, target_width)
                return  # Temporary

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
                # result_img = c_expand(spectrogram_img, target_frames)
                return 
            else:
                result_img = spectrogram_img

            progress.update(
                task, description="Reconstructing audio...")

            # Recover carved magnitude
            carved_magnitude = (
                result_img[:, :, 0].astype(np.float32) / 255.0) * max_val

            # Phase reconstruction
            x_old = np.linspace(0, 1, stft.shape[1])
            x_new = np.linspace(0, 1, target_frames)
            
            # Interpolate real and imaginary parts separately
            stft_real_stretched = np.array(
                [np.interp(x_new, x_old, row) for row in np.real(stft)])
            stft_imag_stretched = np.array(
                [np.interp(x_new, x_old, row) for row in np.imag(stft)])
            # Then combine to get the new phase angles
            carved_phase = np.angle(
                stft_real_stretched + 1j * stft_imag_stretched)
            
            # Combine magnitude and phase 
            carved_stft = carved_magnitude * np.exp(1j * carved_phase)

            # Inverse STFT
            carved_time_series = librosa.istft(
                carved_stft, 
                hop_length=512, 
                length=int(target_duration * sample_rate)
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

def main():
    app()