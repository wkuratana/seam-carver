# Seam Carver

## How to work on the project

0. Install Python and any necessary Python extensions onto your system/VSCode.

1. Install a C compiler! I've never used Windows to code in C, but you can probably find some tutorials on how to do this with VSCode. Maybe look into MinGW and installing `GCC` (a C compiler)?

2. In VSCode, install the official Microsoft C/C++ extension.

3. `git clone` the repository (I am using SSH, but you can use whatever).

4. In the repository, create a virtual environment with `python3 -m venv venv` in the terminal, then activate it (`source venv/bin/activate` on Windows, I believe).

5. Run `pip install -e .` to install the project and all dependencies to your virtual environment! If everything runs without errors, you are good to go.

6. Run `seam-carver` in the terminal → the rudimentary seam carving algorithm will run on the asset specified in `cli.py`