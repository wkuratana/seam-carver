# Seam Carver

This project implements seam carving, inverted seam carving (image widening), audio seam carving, and inverted audio seam carving in C, with a Cython/Python wrapper. It also implements bilinear interpolation in Python.

## What is Seam Carving?

![Seam carving process GIF](assets/seam_carver.gif)  
*GIF credit to Ben Tanen: https://ben-tanen.com/projects/2020/10/08/seam-carving-pt1.html* 

Seam carving is a content-aware image resizing algorithm which relies on calculating paths of least importance—"seams"—in an image for removal or insertion.

The algorithm contrasts with alternative resizing methods, which may stretch and distort important features of an image.

## What is Audio Seam Carving?

Seam carving is an image resizing algorithm that was first developed in 2007 by Shai Avidan and Ariel Shamir. As it is a visual algorithm, most innovations have come in the form of refining how image seams or "energy" are defined.

The audio seam carving implemented in this project is a novel use case for this algorithm. Any audio file that is to be resized (lengthened or shortened) gets converted into a spectrogram—which is then processed as an image. Once the spectrogram reaches a target length, the spectrogram is used to reconstruct the audio: producing a newly resized audio file.

Interesting auditory byproducts can be heard in the output following resizing; the seam carving algorithm distorts the horizontal coordinates of pitches in the spectrogram, resulting in incongruent alignment within the output audio file. Additionally, because some information is lost (and then needs to be reapproximated) when audio is turned into a spectrogram, then reconstructed, a sort of "echo" and warbled sound is consistent accross outputs.

## Bilinear Interpolation

This project also comes with a Python implementation of bilinear interpolation. Bilinear interpolation is an algorithm which is commonly used for image transformations. When compared to nearest-neighbor interpolation, bilinear interpolation is known for producing smoother results.

## How to Install

*To build this project, you must have a C compiler installed (e.g., GCC on Linux/macOS or MSVC on Windows) and Python 3.x.*

This project can be installed using `pip`:

```
pip install git+https://github.com/wkuratana/seam-carver
```

### Development
If you have cloned the repository, you can install the project locally with:

```
cd seam-carver; pip install -e .
```

# How to Use

## Seam Carving

After installing `seam-carver`, run:
```
seam-carver adjust <input_file> <output_file> <target_width>
```
Replace `<input_file>` with an exact path to the image you want to resize, including the file extension.

Replace `<output_file>` with an exact path to where you want to image to be outputted, including the file extension.

Replace `<target_width>` with the exact pixel width you would like to change the width of the `<input_file>` to.

> [!NOTE]  
> If the target width is smaller than the width of the input file, the image will be carved (width will be reduced).
> If the target width is larger, the image will be widened.

If you are ever unsure of what arguments to pass, type `adjust --help`.

### Example Usage
#### Original image:  
![Surfer image](assets/surfer.jpg)
*Image credit to kirildobrev: https://pixabay.com/photos/blue-beach-surf-travel-surfer-4145659/*
#### Shrinking
```
seam-carver adjust assets/surfer.jpg assets/narrow_surfer.jpg 1600
```
##### Output
![Narrowed surfer image](assets/narrow_surfer.jpg)
#### Widening
```
seam-carver adjust assets/surfer.jpg assets/wide_surfer.jpg 2200
```
##### Output
![Widened surfer image](assets/wide_surfer.jpg)

## Audio

Adjust audio with:
```
seam-carver adjust-audio <input_file> <output_file> <target_duration>
```

Ensure `<input_file>` is a `.wav` file (other file types may be supported, but are untested), and `<target_duration>` is in seconds (float).

## Bilinear Interpolation

Use bilinear interpolation to adjust the dimensions of an image with:
```
seam-carver bilinear-interpolation <input_file> <output_file> <target_width> <target_height>
```

## Example Usage

```
seam-carver bilinear-interpolation assets/surfer.jpg assets/bli_narrow_surfer.jpg 1200 1079
```
##### Output
![Distorted surfer image](assets/bli_narrow_surfer.jpg)

# References

Shai Avidan and Ariel Shamir. 2007. Seam carving for content-aware image resizing. In ACM SIGGRAPH 2007 papers (SIGGRAPH '07). Association for Computing Machinery, New York, NY, USA, 10–es. https://doi.org/10.1145/1275808.1276390

# Authors

Wren C. Kuratana  
Machiavelli Merkle-Ward