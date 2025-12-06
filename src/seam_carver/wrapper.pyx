# Imports
import numpy as np
cimport numpy as np
from libc.stdint cimport uint8_t


cdef extern from "backend.h":
    int carve(size_t h, size_t w, uint8_t* rgb_matrix, size_t target_width) nogil

cdef extern from "backend2.h":
    int expand(size_t h, size_t w, uint8_t* rgb_matrix, size_t target_width) nogil

def _validate_image_type(image):
    """Raises error if image is the wrong type."""
    # Validation
    if image.dtype != np.uint8:
        raise TypeError("Image must be of type uint8 (0-255).")

def _grayscale(image):
    """Returns 1 if grayscale by default, 0 if not; returns process_image."""
    cdef bint is_grayscale = 0
    
    # Handle Grayscale (2D)
    if image.ndim == 2:
        is_grayscale = 1
        process_image = np.dstack((image, image, image))  # Creates copies
    elif image.ndim == 3:
        process_image = np.ascontiguousarray(image, dtype=np.uint8)
    else:
        raise ValueError("Image must be 2D (grayscale) or 3D (RGB).")
    
    return (is_grayscale, process_image)

def c_carve(image, int target_width):
    # Specific to carve
    if target_width >= image.shape[1]:
        raise ValueError("Target width must be smaller than current width.")

    _validate_image_type(image)
    is_grayscale, process_image = _grayscale(image)

    # Can't take address of a Python object, so create memory view
    cdef unsigned char[:, :, ::1] img_view = process_image

    cdef size_t h = img_view.shape[0]
    cdef size_t w = img_view.shape[1]
    cdef uint8_t* img_ptr = <uint8_t*>&img_view[0, 0, 0]
    cdef size_t tw = <size_t>target_width
   
    cdef int result
    
    # Release GIL during the C function call
    # (Needed for time elapsed counter in CLI)
    with nogil:
        result = carve(h, w, img_ptr, tw)
    
    if result != 0:
        raise RuntimeError("C function 'carve()' failed.")

    # Slice to :target_width to hide the garbage data on the right
    output = process_image[:, :target_width, :]

    # Convert back to 2D if the input was grayscale
    if is_grayscale:
        return output[:, :, 0]
    
    
    return output