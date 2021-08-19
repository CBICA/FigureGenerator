import math, os
import SimpleITK as sitk

## color_map look-up table
# colomap_lut = {
#     "red": sitk.ScalarToRGBColormapImageFilter.Red,
#     "green": sitk.ScalarToRGBColormapImageFilter.Green,
#     "blue": sitk.ScalarToRGBColormapImageFilter.Blue,
#     "grey": sitk.ScalarToRGBColormapImageFilter.Grey,
#     "hot": sitk.ScalarToRGBColormapImageFilter.Hot,
#     "cool": sitk.ScalarToRGBColormapImageFilter.Cool,
#     "spring": sitk.ScalarToRGBColormapImageFilter.Spring,
#     "summer": sitk.ScalarToRGBColormapImageFilter.Summer,
#     "autumn": sitk.ScalarToRGBColormapImageFilter.Autumn,
#     "winter": sitk.ScalarToRGBColormapImageFilter.Winter,
#     "copper": sitk.ScalarToRGBColormapImageFilter.Copper,
#     "jet": sitk.ScalarToRGBColormapImageFilter.Jet,
#     "hsv": sitk.ScalarToRGBColormapImageFilter.HSV,
#     "overunder": sitk.ScalarToRGBColormapImageFilter.OverUnder,
# }


def get_basename_sanitized(file_name):
    """
    Get the basename of the input file, without the extension.

    Args:
        file_name (str): The input file name.

    Returns:
        str: The basename of the input file.
    """
    temp_file = file_name
    if file_name.endswith(".nii.gz"):
        temp_file = file_name.replace(".nii.gz", "")
    return os.path.splitext(os.path.basename(temp_file))[0]


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

    Returns:
        bool: Result of sanity checking.
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


def sanity_checker_with_files(image_file_1, image_file_2):
    """
    This function performs sanity check on 2 image files WITHOUT loading images into memory.

    Args:
        image_file_1 (str): First image to check.
        image_file_2 (str): Second image to check.

    Raises:
        ValueError: Dimension mismatch in the images.
        ValueError: Origin mismatch in the images.
        ValueError: Orientation mismatch in the images.
        ValueError: Spacing mismatch in the images.

    Returns:
        bool: Result of sanity checking.
    """
    file_reader_current = sitk.ImageFileReader()
    file_reader_current.SetFileName(image_file_1)
    file_reader_current.ReadImageInformation()
    return sanity_checker_base(file_reader_current, [image_file_2])


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

    size = oriented_image.GetSize()
    max_size = max(size)

    padding = [0] * oriented_image.GetDimension()

    for i in range(oriented_image.GetDimension()):
        padding[i] = int(math.floor(max_size - size[i]) / 2.0)

    padded_image = sitk.ConstantPad(oriented_image, padding, padding, 0.0)

    return padded_image


def binarize_image(image):
    """
    Binarize the input image.

    Args:
        image (SimpleITK.Image): The input image, all pixel values are expected to be between 0 and 255.

    Returns:
        SimpleITK.Image: The binarized image.
    """
    max_filter = sitk.MinimumMaximumImageFilter()
    max_filter.Execute(image)
    thresholder = sitk.BinaryThresholdImageFilter()
    thresholder.SetOutsideValue(0)
    thresholder.SetInsideValue(1)
    thresholder.SetLowerThreshold(1)
    thresholder.SetUpperThreshold(max_filter.GetMaximum())
    return thresholder.Execute(image)


def get_bounding_box(image, mask, border_pc):
    """
    Get the bounding box of the image based on the first mask after it is binarized.

    Args:
        image (SimpleITK.Image): The input image.
        mask (SimpleITK.Image): The ground truth mask.
        border_pc (float): The percentage of the image size to consider as the border.

    Returns:
        list: The bounding box in the form of [x_min, x_max, y_min, y_max, z_min, z_max]
    """
    size = image.GetSize()
    if mask is not None:
        extractor = sitk.LabelStatisticsImageFilter()
        extractor.Execute(image, binarize_image(mask))
        bb = list(extractor.GetBoundingBox(1))
        bb[0] = max(0, math.floor(bb[0] - border_pc * size[0]))
        bb[2] = max(0, math.floor(bb[2] - border_pc * size[1]))
        bb[4] = max(0, math.floor(bb[4] - border_pc * size[2]))

        full_min = min(bb[0], bb[2], bb[4])
        bb[0], bb[2], bb[4] = full_min, full_min, full_min

        bb[1] = min(size[0], math.floor(bb[1] + border_pc * size[0]))
        bb[3] = min(size[1], math.floor(bb[3] + border_pc * size[1]))
        bb[5] = min(size[2], math.floor(bb[5] + border_pc * size[2]))
        full_max = max(bb[1], bb[3], bb[5])
        bb[1], bb[3], bb[5] = full_max, full_max, full_max

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

    ## the r was not getting visualized, so commented out
    # r = [255,0,0]
    # g = [0,255,0]
    # b = [0,0,255]
    # return sitk.LabelOverlay(image=sitk.Cast(image, sitk.sitkUInt8),
    #                                  labelImage=mask,
    #                                  opacity=alpha, backgroundValue = 0,
    #                                  colormap=r+g+b)

    filter_overlay = sitk.LabelOverlayImageFilter()
    filter_overlay.SetOpacity(alpha)
    # filter_overlay.SetBackgroundValue(0)
    # filter_overlay.SetColormap(r+g+b)
    return filter_overlay.Execute(sitk.Cast(image, sitk.sitkUInt8), sitk.Cast(mask, sitk.sitkUInt8))
