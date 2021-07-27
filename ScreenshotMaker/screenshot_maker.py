#!usr/bin/env python
# -*- coding: utf-8 -*-
from SimpleITK.SimpleITK import GetArrayFromImage
from .utils import (
    sanity_checker_base,
    resample_image,
    rescale_intensity,
    get_bounding_box,
)
import SimpleITK as sitk
import numpy as np


class ScreenShotMaker:
    def __init__(self, args):
        # change comma-separated string to list for images and masks
        self.images = args.images.split(",")
        assert len(args.images) > 0, "Please provide at least one image."
        self.mask_present = False
        if args.masks is not None:
            self.masks = args.masks.split(",")
            self.mask_present = True
        else:
            self.masks = None

        # initialize members
        ## not using slice because it's calculation after resampling is a pain
        # if args.slice is not None:
        #     self.slice_numbers = args.slice.split(",")
        # else:
        #     self.slice_numbers = None
        self.mask_opacity = args.mask_opacity
        self.border_pc = args.borderpc
        self.colormap = args.colormap
        self.axis_row = args.axis_row
        self.calculate_bounds = args.bounded
        self.tiler = sitk.TileImageFilter()
        layout = self.tiler.GetLayout()

        ## sanity checker
        # read the first image and save that for comparison
        file_reader_base = sitk.ImageFileReader()
        file_reader_base.SetFileName(self.images[0])
        file_reader_base.ReadImageInformation()

        if sanity_checker_base(file_reader_base, self.images[1:]):
            # only check masks if sanity check for images passes
            sanity_checker_base(file_reader_base, self.masks)

        self.read_images_and_store_arrays()

    def read_images_and_store_arrays(self):
        # make the screenshot
        # try one of the following:
        # - https://simpleitk.org/doxygen/latest/html/classitk_1_1simple_1_1LabelMapOverlayImageFilter.html
        # - https://simpleitk.org/doxygen/latest/html/classitk_1_1simple_1_1LabelOverlayImageFilter.html -- seems to be more appropriate
        # - https://github.com/SimpleITK/NIH2019_COURSE/blob/master/09_results_visualization.ipynb

        input_images = [
            rescale_intensity(resample_image(sitk.ReadImage(image)))
            for image in self.images
        ]

        if self.mask_present:
            input_masks = [
                resample_image(
                    sitk.ReadImage(mask), interpolator=sitk.sitkNearestNeighbor
                )
                for mask in self.masks
            ]
        else:
            input_masks = None

        ## 3d-specific calculations start here.
        if self.calculate_bounds:
            bounding_box = get_bounding_box(
                input_images[0], input_masks, self.border_pc
            )
        else:
            bounding_box = get_bounding_box(input_images[0], None, self.border_pc)
        print(bounding_box)

        # get the bounded image and masks in the form of arrays
        if len(input_images[0].GetSize()) == 3:
            self.input_images_array = [
                np.swapaxes(sitk.GetArrayFromImage(image), 0, 2)[
                    bounding_box[0] : bounding_box[1],
                    bounding_box[2] : bounding_box[3],
                    bounding_box[4] : bounding_box[5],
                ]
                for image in input_images
            ]
            self.image_is_2d = False
        elif len(input_images[0].GetSize()) == 2:
            raise NotImplementedError("2D not yet supported")
            # self.input_images_array = [
            #     sitk.GetArrayFromImage(image)[
            #         bounding_box[0] : bounding_box[1],
            #         bounding_box[2] : bounding_box[3],
            #         :,
            #     ]
            #     for image in input_images
            # ]
            # self.image_is_2d = True

        if self.mask_present:
            if len(input_images[0].GetSize()) == 3:
                self.input_mask_array = [
                    np.swapaxes(sitk.GetArrayFromImage(image), 0, 2)[
                        bounding_box[0] : bounding_box[1],
                        bounding_box[2] : bounding_box[3],
                        bounding_box[4] : bounding_box[5],
                    ]
                    for image in input_masks
                ]
            elif len(input_images[0].GetSize()) == 2:
                self.input_mask_array = [
                    sitk.GetArrayFromImage(image)[
                        bounding_box[0] : bounding_box[1],
                        bounding_box[2] : bounding_box[3],
                        :,
                    ]
                    for image in input_masks
                ]

            # loop over each axis and get index with largest area
            max_nonzero = 0
            max_id = [0, 0, 0]
            for xid in range(self.input_mask_array[0].shape[0]):  # for each x-axis
                current_slice = self.input_mask_array[0][xid, :, :]
                current_nonzero = np.count_nonzero(current_slice)
                if current_nonzero > max_nonzero:
                    current_nonzero = max_nonzero
                    max_id[0] = xid

            max_nonzero = 0
            for yid in range(self.input_mask_array[0].shape[1]):  # for each y-axis
                current_slice = self.input_mask_array[0][:, yid, :]
                current_nonzero = np.count_nonzero(current_slice)
                if current_nonzero > max_nonzero:
                    current_nonzero = max_nonzero
                    max_id[1] = yid

            if not (self.image_is_2d):
                max_nonzero = 0
                for zid in range(self.input_mask_array[0].shape[2]):  # for each z-axis
                    current_slice = self.input_mask_array[0][:, :, zid]
                    current_nonzero = np.count_nonzero(current_slice)
                    if current_nonzero > max_nonzero:
                        current_nonzero = max_nonzero
                        max_id[2] = zid

        else:
            self.input_mask_array = None
            # if mask is not defined, pick the middle of the array
            max_id = np.around(
                np.true_divide(self.input_images_array[0].shape, 2)
            ).tolist()

        self.max_id = max_id

    def get_image_and_mask_slices(self, array_list):
        """
        Function to get the image and mask slices from the input array.

        Args:
            array_list (list of np.array): The array list to get the slices from.

        Returns:
            list of list of np.array: The list of list of image and mask slices.
        """
        output_slices = []
        for array in array_list:
            current_image_slices = []
            if not (self.image_is_2d):
                current_image_slices.append(array[self.max_id[0], :, :])
                current_image_slices.append(array[:, self.max_id[1], :])
                current_image_slices.append(array[:, :, self.max_id[2]])
            output_slices.append(current_image_slices)
        return output_slices

    def get_image_to_write(self):
        image_slices = self.get_image_and_mask_slices(self.input_images_array)
        mask_slices = self.get_image_and_mask_slices(self.input_masks_array)

        test = 1

    def save_screenshot(self, filename):
        # save the screenshot to a file
        test = 1
