import math
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


def rescale_intensity(image):
    """
    Rescale the intensity of an image.

    Args:
        image (SimpleITK.Image): The input image.

    Returns:
        SimpleITK.Image: The rescaled image.
    """
    rescaler = sitk.RescaleIntensityImageFilter()
    rescaler.SetOutputMinimum(0)
    rescaler.SetOutputMaximum(255)
    return rescaler.Execute(image)


def resample_image(
    img, spacing=None, size=None, interpolator=sitk.sitkLinear, outsideValue=0
):
    """
    Resample image to certain spacing and size.

    Args:
        img (SimpleITK.Image): The input image to resample.
        spacing (list): List of length 3 indicating the voxel spacing as [x, y, z].
        size (list, optional): List of length 3 indicating the number of voxels per dim [x, y, z], which will use compute the appropriate size based on the spacing. Defaults to [].
        interpolator (SimpleITK.InterpolatorEnum, optional): The interpolation type to use. Defaults to SimpleITK.sitkLinear.
        origin (list, optional): The location in physical space representing the [0,0,0] voxel in the input image.  Defaults to [0,0,0].
        outsideValue (int, optional): value used to pad are outside image.  Defaults to 0.

    Raises:
        Exception: Spacing/resolution mismatch.
        Exception: Size mismatch.

    Returns:
        SimpleITK.Image: The resampled input image.
    """
    # initialize spacing to '1' for isotropic
    if spacing is None:
        spacing = []
        min_org_spacing = min(img.GetSpacing())
        spacing = [min_org_spacing for _ in range(0, img.GetDimension())]
    elif len(spacing) != img.GetDimension():
        raise Exception("len(spacing) != " + str(img.GetDimension()))

    # Set Size
    if size == None:
        inSpacing = img.GetSpacing()
        inSize = img.GetSize()
        size = [
            int(math.ceil(inSize[i] * (inSpacing[i] / spacing[i])))
            for i in range(img.GetDimension())
        ]
    else:
        if len(size) != img.GetDimension():
            raise Exception("len(size) != " + str(img.GetDimension()))

    # Resample input image
    resampled_image = sitk.Resample(
        img,
        size,
        sitk.Transform(),
        interpolator,
        img.GetOrigin(),
        spacing,
        img.GetDirection(),
        outsideValue,
    )

    orienter = sitk.DICOMOrientImageFilter()
    orienter.SetDesiredCoordinateOrientation("RAI")
    oriented_image = orienter.Execute(resampled_image)

    if oriented_image.GetDimension() == 3:
        oriented_image.SetOrigin((0, 0, 0))
        oriented_image.SetDirection((1, 0, 0, 0, 1, 0, 0, 0, 1))
    elif oriented_image.GetDimension() == 2:
        oriented_image.SetOrigin((0, 0))
        oriented_image.SetDirection((1, 0, 0, 1))

    return oriented_image


def get_bounding_box(image, mask_list, border_pc):
    """
    Get the bounding box of the image based on the first mask after it is binarized.

    Args:
        image (SimpleITK.Image): The input image.
        mask_list (list of SimpleITK.Image): The list of masks.
        border_pc (float): The percentage of the image size to consider as the border.

    Returns:
        list: The bounding box in the form of [x_min, x_max, y_min, y_max, z_min, z_max]
    """
    size = image.GetSize()
    if mask_list is not None:
        max_filter = sitk.MinimumMaximumImageFilter()
        max_filter.Execute(mask_list[0])
        thresholder = sitk.BinaryThresholdImageFilter()
        thresholder.SetOutsideValue(0)
        thresholder.SetInsideValue(1)
        thresholder.SetLowerThreshold(1)
        thresholder.SetUpperThreshold(max_filter.GetMaximum())
        extractor = sitk.LabelStatisticsImageFilter()
        extractor.Execute(image, thresholder.Execute(mask_list[0]))
        bb = list(extractor.GetBoundingBox(1))
        bb[0] = max(0, math.floor(bb[0] - border_pc * size[0]))
        bb[2] = max(0, math.floor(bb[2] - border_pc * size[1]))
        bb[4] = max(0, math.floor(bb[4] - border_pc * size[2]))

        bb[1] = min(size[0], math.floor(bb[1] + border_pc * size[0]))
        bb[3] = min(size[1], math.floor(bb[3] + border_pc * size[1]))
        bb[5] = min(size[2], math.floor(bb[5] + border_pc * size[2]))
        return bb
    else:
        if len(size) == 3:
            return (0, size[0] - 1, 0, size[1] - 1, 0, size[2] - 1)
        elif len(size) == 2:
            return (0, size[0] - 1, 0, size[1] - 1)


def alpha_blend(image, mask=None, alpha=0.5):
    """
    Alpha blend an image and a mask with specified opacity.

    Adapted from https://github.com/SimpleITK/NIH2019_COURSE/blob/master/09_results_visualization.ipynb

    Args:
        image (SimpleITK.Image): The input image.
        mask (SimpleITK.Image): The input mask. Defaults to None.
        alpha (float): The alpha value to use. Defaults to 0.5.

    Returns:
        list: The bounding box in the form of [x_min, x_max, y_min, y_max, z_min, z_max]
    """

    if not mask:
        mask = sitk.Image(image.GetSize(), sitk.sitkUInt8)
        mask.CopyInformation(image)

    filter = sitk.LabelOverlayImageFilter()
    filter.SetOpacity(alpha)
    # filter.SetColormap()
    return filter.Execute(sitk.Cast(image, sitk.sitkUInt8), mask)
