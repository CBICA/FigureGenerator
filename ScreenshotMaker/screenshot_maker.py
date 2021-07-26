#!usr/bin/env python
# -*- coding: utf-8 -*-
from .utils import perform_sanity_check_on_subject


class ScreenShotMaker:
    def __init__(self, images, masks=None, slice_numbers=None, mask_opacity=100):
        self.images = images
        self.masks = masks
        self.slice_numbers = slice_numbers
        self.mask_opacity = mask_opacity

    def check_validity(self):
        return perform_sanity_check_on_subject(self.images, self.masks)

    def save_screenshot(self, filename):
        # save the screenshot to a file
        test = 1
