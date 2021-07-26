#!usr/bin/env python
# -*- coding: utf-8 -*-


class ScreenShotMaker:
    def __init__(self, images, masks, slice_numbers, mask_opacity=100):
        self.images = images
        self.masks = masks
        self.slice_numbers = slice_numbers
        self.mask_opacity = mask_opacity

    def save_screenshot(self, filename):
        # save the screenshot to a file
        test = 1
