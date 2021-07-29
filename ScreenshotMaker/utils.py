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
    return orienter.Execute(resampled_image)


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


def alpha_blend(image, mask=None, alpha=0.5, colormap="jet"):
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

    # colormap_lut = {
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

    if not mask:
        msk = sitk.Image(image.GetSize(), sitk.sitkFloat32) + 1.0
        msk.CopyInformation(image)
        msk = sitk.Compose(msk, msk, msk)
    else:
        filter = sitk.LabelToRGBImageFilter()
        # filter.SetColormap(colormap_lut[colormap])
        msk = filter.Execute(mask)
        msk = sitk.Cast(msk, sitk.sitkVectorFloat32)

    # components_per_pixel = mask.GetNumberOfComponentsPerPixel()
    img = sitk.Cast(image, sitk.sitkFloat32)
    # if components_per_pixel > 1:
    #     # img = sitk.Cast(image, sitk.sitkVectorFloat32)
    #     img = sitk.Cast(image, sitk.sitkFloat32)
    # else:
    #     img = sitk.Cast(image, mask.GetPixelID())

    for channel in range(3):
        tmp = sitk.VectorIndexSelectionCast(msk, channel)
        test = 1
    return sitk.Compose(
        [
            (alpha * sitk.VectorIndexSelectionCast(msk, channel)) * img # sitk.VectorIndexSelectionCast(img, channel)
            for channel in range(3)
        ]
    )


# def mask_image_multiply(mask, image):
#     components_per_pixel = image.GetNumberOfComponentsPerPixel()
#     if components_per_pixel == 1:
#         temp = mask * image
#         return sitk.Compose(temp,temp,temp)
#     else:
#         return sitk.Compose(
#             [
#                 mask * sitk.VectorIndexSelectionCast(image, channel)
#                 for channel in range(components_per_pixel)
#             ]
#         )


# def alpha_blend(image1, image2=None, mask1=None, mask2=None, alpha=0.5):
#     """
#     Alaph blend two images, pixels can be scalars or vectors.
#     The region that is alpha blended is controled by the given masks.
#     """

#     if not mask1:
#         mask1 = sitk.Image(image1.GetSize(), sitk.sitkFloat32) + 1.0
#         mask1.CopyInformation(image1)
#     else:
#         mask1 = sitk.Cast(mask1, sitk.sitkFloat32)
#     if not mask2:
#         mask2 = sitk.Image(image1.GetSize(), sitk.sitkFloat32) + 1
#         mask2.CopyInformation(image1)
#     else:
#         mask2 = sitk.Cast(mask2, sitk.sitkFloat32)

#     if not image2:
#         image2 = image1

#     components_per_pixel = image1.GetNumberOfComponentsPerPixel()
#     if components_per_pixel > 1:
#         img1 = sitk.Cast(image1, sitk.sitkVectorFloat32)
#         img2 = sitk.Cast(image2, sitk.sitkVectorFloat32)
#     else:
#         img1 = sitk.Cast(image1, sitk.sitkFloat32)
#         img2 = sitk.Cast(image2, sitk.sitkFloat32)

#     intersection_mask = mask1 * mask2

#     intersection_image = mask_image_multiply(
#         alpha * intersection_mask, img1
#     ) + mask_image_multiply((1 - alpha) * intersection_mask, img2)
#     return (
#         intersection_image
#         + mask_image_multiply(mask2 - intersection_mask, img2)
#         + mask_image_multiply(mask1 - intersection_mask, img1)
#     )
