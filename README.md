# Image Seam Carver

This project is still in development!

## How to Install (Dev)

1. In the repository, create a virtual environment with `python3 -m venv venv` in the terminal, then activate it (`.\venv\Scripts\activate.ps1` on Windows).

2. Run `pip install -e .` to install the project and all dependencies to your virtual environment! If everything runs without errors, you are good to go.

3. Run the commands below!

## How to Use

After installing `seam-carver`, run:
```
seam-carver adjust <input_file> <output_file> <target_width>
```
Replace `<input_file>` with an exact path to the image you want to resize, including the file extension.

Replace `<output_file>` with an exact path to where you want to image to be outputted, including the file extension.

Replace `<target_width>` with the exact pixel width you would like to change the width of the `<input_file>` to.

> [!NOTE]  
> If the target width is smaller than the width of the input file, the image will be carved (width will be reduced).
> If the target width is larger, the image will be widened (WIP).

If you are ever unsure of what arguments to pass, type `adjust --help`.

### Example Usage
```
seam-carver adjust assets/surfer.jpg assets/narrow_surfer.jpg 1600
```

### Audio

Adjust audio with:
```
seam-carver adjust-audio <input_file> <output_file> <target_length>
```

Ensure `<input_file>` is a `.wav` file, and `<target_length>` is in seconds.