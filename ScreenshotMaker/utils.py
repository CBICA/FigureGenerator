import os, sys, math
import numpy as np
import SimpleITK as sitk


def sanity_checker_base(file_reader_base, images_to_check):
    """
    This function performs sanity check on a list of images to ensure presence of consistent header information WITHOUT loading images into memory.

    Args:
        file_reader_base (SimpleITK.ImageFileReader): File reader for the base image.
        images_to_check (list): List of images paths to check.

    Raises:
        ValueError: Dimension mismatch in the images.
        ValueError: Origin mismatch in the images.
        ValueError: Orientation mismatch in the images.
        ValueError: Spacing mismatch in the images.
    """
    if images_to_check is None:
        return True

    for image in images_to_check:
        file_reader_current = sitk.ImageFileReader()
        file_reader_current.SetFileName(image)
        file_reader_current.ReadImageInformation()

        if file_reader_base.GetDimension() != file_reader_current.GetDimension():
            raise ValueError("Dimensions for subject are not consistent.")

        if file_reader_base.GetOrigin() != file_reader_current.GetOrigin():
            raise ValueError("Origin for subject are not consistent.")

        if file_reader_base.GetDirection() != file_reader_current.GetDirection():
            raise ValueError("Orientation for subject are not consistent.")

        if file_reader_base.GetSpacing() != file_reader_current.GetSpacing():
            raise ValueError("Spacing for subject are not consistent.")

    return True


def perform_sanity_check_on_subject(images, masks=None):
    """
    This function performs sanity check on a list of images and masks (if present) to ensure presence of consistent header information WITHOUT loading images into memory.

    Args:
        images (list): List of images paths.
        masks (list): List of images paths. Defaults to None.

    Returns:
        bool: True if everything is okay.
    """
    if len(images) == 1:
        return True
    # read the first image and save that for comparison
    file_reader_base = sitk.ImageFileReader()
    file_reader_base.SetFileName(images[0])
    file_reader_base.ReadImageInformation()

    if sanity_checker_base(file_reader_base, images[1:]):
        return sanity_checker_base(file_reader_base, masks)

    return True
