#!usr/bin/env python
# -*- coding: utf-8 -*-
from .utils import sanity_checker_base
import SimpleITK as sitk


class ScreenShotMaker:
    def __init__(self, images, masks=None, slice_numbers=None, mask_opacity=100):

        assert len(images) > 0, "Please provide at least one image."
        assert images is not None, "Please provide at least one image."

        # change comma-separated string to list for images and masks
        self.images = images.split(",")
        if masks is not None:
            self.masks = masks.split(",")
        else:
            self.masks = None
        self.slice_numbers = slice_numbers
        self.mask_opacity = mask_opacity

    def check_validity(self):
        # if a single image and no mask is given, return True
        if (len(self.images) == 1) and (self.masks is None):
            return True
        # read the first image and save that for comparison
        file_reader_base = sitk.ImageFileReader()
        file_reader_base.SetFileName(self.images[0])
        file_reader_base.ReadImageInformation()

        if sanity_checker_base(file_reader_base, self.images[1:]):
            # only check masks if sanity check for images passes
            return sanity_checker_base(file_reader_base, self.masks)
        else:
            return False

    def save_screenshot(self, filename):
        # save the screenshot to a file
        test = 1
