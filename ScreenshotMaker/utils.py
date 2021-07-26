import os, sys, math
import numpy as np
import SimpleITK as sitk


def perform_sanity_check_on_subject(images):
    """
    This function performs sanity check on the subject to ensure presence of consistent header information WITHOUT loading images into memory.

    Args:
        images (list): List of images paths.

    Returns:
        bool: True if everything is okay.

    Raises:
        ValueError: Dimension mismatch in the images.
        ValueError: Origin mismatch in the images.
        ValueError: Orientation mismatch in the images.
        ValueError: Spacing mismatch in the images.
    """
    if len(images) == 1:
        return True
    # read the first image and save that for comparison
    file_reader_base = None

    for image in images:
        if file_reader_base is None:
            file_reader_base = sitk.ImageFileReader()
            file_reader_base.SetFileName(image)
            file_reader_base.ReadImageInformation()
        else:
            # in this case, file_reader_base is ready
            file_reader_current = sitk.ImageFileReader()
            file_reader_current.SetFileName(image)
            file_reader_current.ReadImageInformation()

            if file_reader_base.GetDimension() != file_reader_current.GetDimension():
                raise ValueError("Dimensions for Subject are not consistent.")

            if file_reader_base.GetOrigin() != file_reader_current.GetOrigin():
                raise ValueError("Origin for Subject are not consistent.")

            if file_reader_base.GetDirection() != file_reader_current.GetDirection():
                raise ValueError("Orientation for Subject are not consistent.")

            if file_reader_base.GetSpacing() != file_reader_current.GetSpacing():
                raise ValueError("Spacing for Subject are not consistent.")

    return True
