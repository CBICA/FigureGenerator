#!usr/bin/env python
# -*- coding: utf-8 -*-
import os, pathlib
from .utils import (
    sanity_checker_base,
    resample_image,
    rescale_intensity,
    get_bounding_box,
    alpha_blend,
)
import SimpleITK as sitk
import numpy as np

# from .multi_image_display import MultiImageDisplay
import matplotlib.pyplot as plt


class FigureGenerator:
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
        self.axisrow = args.axisrow
        self.calculate_bounds = args.bounded
        self.output = args.output
        _, ext = os.path.splitext(self.output)
        if ext == "" or ext is None:
            pathlib.Path(self.output).mkdir(parents=True, exist_ok=True)
            self.output = os.path.join(self.output, "screenshot.png")
        self.tiler = sitk.TileImageFilter()

        if self.axisrow:
            self.layout = (3 * len(self.images), 1 + len(self.masks), 0)
        else:
            self.layout = (3, len(self.images) + len(self.images) * len(self.masks), 0)

        self.tiler.SetLayout(self.layout)

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

        input_images = [
            rescale_intensity(resample_image(sitk.ReadImage(image)))
            for image in self.images
        ]

        input_masks = None
        if self.mask_present:
            input_masks = [
                (
                    (
                        resample_image(
                            sitk.ReadImage(mask), interpolator=sitk.sitkNearestNeighbor
                        )
                    )
                )
                for mask in self.masks
            ]

        ## 3d-specific calculations start here.
        if self.calculate_bounds:
            bounding_box = get_bounding_box(
                input_images[0], input_masks, self.border_pc
            )
        else:
            bounding_box = get_bounding_box(input_images[0], None, None)

        extract = sitk.ExtractImageFilter()
        extract.SetSize(
            [
                bounding_box[1] - bounding_box[0] + 1,
                bounding_box[3] - bounding_box[2] + 1,
                bounding_box[5] - bounding_box[4] + 1,
            ]
        )
        extract.SetIndex([bounding_box[0], bounding_box[2], bounding_box[4]])

        # get the bounded image and masks in the form of arrays
        if len(input_images[0].GetSize()) == 3:
            self.input_images_bounded = [
                image[
                    bounding_box[0] : bounding_box[1] + 1,
                    bounding_box[2] : bounding_box[3] + 1,
                    bounding_box[4] : bounding_box[5] + 1,
                ]
                for image in input_images
            ]
            self.image_is_2d = False
        elif len(input_images[0].GetSize()) == 2:
            # raise NotImplementedError("2D not yet supported")
            self.input_images_bounded = [
                image[
                    bounding_box[0] : bounding_box[1] + 1,
                    bounding_box[2] : bounding_box[3] + 1,
                    :,
                ]
                for image in input_images
            ]
            self.image_is_2d = True

        if self.mask_present:
            if len(input_images[0].GetSize()) == 3:
                self.input_masks_bounded = [
                    image[
                        bounding_box[0] : bounding_box[1] + 1,
                        bounding_box[2] : bounding_box[3] + 1,
                        bounding_box[4] : bounding_box[5] + 1,
                    ]
                    for image in input_masks
                ]
            elif len(input_images[0].GetSize()) == 2:
                self.input_masks_bounded = [
                    image[
                        bounding_box[0] : bounding_box[1] + 1,
                        bounding_box[2] : bounding_box[3] + 1,
                        :,
                    ]
                    for image in input_masks
                ]

            # loop over each axis and get index with largest area
            max_nonzero = 0
            max_id = [0, 0, 0]
            size = self.input_masks_bounded[0].GetSize()
            for xid in range(size[0]):  # for each x-axis
                current_slice = self.input_masks_bounded[0][xid, :, :]
                current_nonzero = np.count_nonzero(
                    sitk.GetArrayFromImage(current_slice)
                )
                if current_nonzero > max_nonzero:
                    max_nonzero = current_nonzero
                    max_id[0] = xid

            max_nonzero = 0
            for yid in range(size[1]):  # for each y-axis
                current_slice = self.input_masks_bounded[0][:, yid, :]
                current_nonzero = np.count_nonzero(
                    sitk.GetArrayFromImage(current_slice)
                )
                if current_nonzero > max_nonzero:
                    max_nonzero = current_nonzero
                    max_id[1] = yid

            if not (self.image_is_2d):
                max_nonzero = 0
                for zid in range(size[2]):  # for each z-axis
                    current_slice = self.input_masks_bounded[0][:, :, zid]
                    current_nonzero = np.count_nonzero(
                        sitk.GetArrayFromImage(current_slice)
                    )
                    if current_nonzero > max_nonzero:
                        max_nonzero = current_nonzero
                        max_id[2] = zid

        else:
            self.input_masks_bounded = None
            # if mask is not defined, pick the middle of the array
            max_id = (
                np.around(np.true_divide(self.input_images_bounded[0].shape, 2))
                .astype(int)
                .tolist()
            )

        self.max_id = max_id
        self.get_image_to_write()

    def get_image_and_mask_slices(self, image_list):
        """
        Function to get the image and mask slices from the input array.

        Args:
            image_list (list of SimpleITK.Image): The array list to get the slices from.

        Returns:
            list of list of SimpleITK.Image: The list of list of image and mask slices.
        """
        output_slices = []
        for image in image_list:
            current_image_slices = []
            if self.image_is_2d:
                current_image_slices.append(image[self.max_id[0], :])
                current_image_slices.append(image[:, self.max_id[1]])
            else:
                current_image_slices.append(image[self.max_id[0], :, :])
                current_image_slices.append(image[:, self.max_id[1], :])
                current_image_slices.append(image[:, :, self.max_id[2]])
            output_slices.append(current_image_slices)
        return output_slices

    def get_image_to_write(self):
        image_slices = self.get_image_and_mask_slices(self.input_images_bounded)
        mask_slices = None
        if self.input_masks_bounded is not None:
            mask_slices = self.get_image_and_mask_slices(self.input_masks_bounded)
        else:
            mask_slices = [[None] * len(slice) for slice in image_slices]

        images_blended = []
        only_images, images_with_mask = [], []
        # first put the image slices
        for image_slice in image_slices:
            for i in range(len(image_slice)):
                blended_image = alpha_blend(image_slice[i])

                images_blended.append(blended_image)
                only_images.append(blended_image)

        # next, put in the image slices blended with the masks
        if self.mask_present:
            for image_slice in image_slices:
                for mask_slice in mask_slices:
                    for i in range(len(image_slice)):

                        mask = None
                        if mask_slice[i] is not None:
                            mask = mask_slice[i]

                        blended_image = alpha_blend(image_slice[i], mask)
                        images_with_mask.append(blended_image)
                        images_blended.append(blended_image)

        # start the plotting
        self.fig, _ = plt.subplots(
            self.layout[1],
            self.layout[0],
            figsize=(self.layout[0] * 5 / 2, self.layout[1] * 5 / 2),
        )
        # set plot properties
        self.fig.set_dpi(600)
        plt.subplots_adjust(wspace=0, hspace=0)
        plt.rcParams.update(
            {
                "lines.color": "white",
                "patch.edgecolor": "white",
                "text.color": "white",
                "axes.facecolor": "white",
                "axes.edgecolor": "lightgray",
                "axes.labelcolor": "white",
                "xtick.color": "white",
                "ytick.color": "white",
                "grid.color": "lightgray",
                "figure.facecolor": "black",
                "figure.edgecolor": "black",
                "savefig.facecolor": "black",
                "savefig.edgecolor": "black",
            }
        )

        # we only want the titles for first row
        counter = 0
        for ax, img in zip(self.fig.axes, images_blended):
            ax.imshow(sitk.GetArrayFromImage(img))
            ax.axis("off")
            counter += 1
            if counter <= self.layout[0]:
                if counter % 3 == 1:
                    ax.set_title("Sagittal")
                elif counter % 3 == 2:
                    ax.set_title("Coronal")
                elif counter % 3 == 0:
                    ax.set_title("Axial")
                ax.title.set_color("white")

        plt.tight_layout()
        plt.savefig(os.path.join(self.output))
