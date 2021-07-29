import matplotlib.pyplot as plt
import numpy as np
import os
import SimpleITK as sitk
import ipywidgets as widgets


class MultiImageDisplay(object):
    """
    This class provides a GUI for displaying 3D images. It supports display of
    multiple images in the same UI. The image slices are selected according to
    the axis specified by the user. Each image can have a title and a slider to
    scroll through the stack. The images can also share a single slider if they
    have the same number of slices along the given axis. Images are either
    grayscale or color. The intensity range used for display (window-level) can
    be specified by the user as input to the constructor or set via the displayed
    slider. For color images the intensity control slider will be disabled. This
    allows us to display both color and grayscale images in the same figure with
    a consistent look to the controls. The range of the intensity slider is set
    to be from top/bottom 2% of intensities (accommodating for outliers). Images
    are displayed either in horizontal or vertical layout, depending on the
    users choice.

    Adapted from: https://github.com/InsightSoftwareConsortium/SimpleITK-Notebooks/blob/master/Python/gui.py
    """

    def __init__(
        self,
        image_list,
        output_file,
        axis=0,
        title_list=None,
        figure_size=(10, 8),
        horizontal=True,
    ):
        self.npa_list, wl_range, wl_init = self.get_window_level_numpy_array(image_list, window_level_list=None, intensity_slider_range_percentile=[0,100])
        # self.npa_list = list(map(sitk.GetArrayFromImage, image_list))
        if title_list:
            if len(image_list) != len(title_list):
                raise ValueError("Title list and image list lengths do not match")
            self.title_list = list(title_list)
        else:
            self.title_list = [""] * len(image_list)

        # Our dynamic slice, based on the axis the user specifies
        self.slc = [slice(None)] * 3
        self.axis = axis

        # Create a figure.
        col_num, row_num = (len(image_list), 1) if horizontal else (1, len(image_list))
        self.fig, self.axes = plt.subplots(row_num, col_num, figsize=figure_size)
        if len(image_list) == 1:
            self.axes = [self.axes]

        # Display the data and the controls, first time we display the image is outside the "update_display" method
        # as that method relies on the previous zoom factor which doesn't exist yet.
        self.slider_list = []
        for npa in self.npa_list:
            slider = widgets.IntSlider(description='image slice:',
                                        min=0,
                                        max=npa.shape[self.axis]-1,
                                        step=1,
                                        value = int((npa.shape[self.axis]-1)/2),
                                        width='20em')
            # slider.observe(self.on_slice_slider_value_change, names='value')
            self.slider_list.append(slider)

        self.wl_list = []
        # Each image has a window-level slider, but it is disabled if the image
        # is a color image len(npa.shape)==4 . This allows us to display both
        # color and grayscale images in the same UI while retaining a reasonable
        # layout for the sliders.
        for r_values, i_values, npa in zip(wl_range, wl_init, self.npa_list):
            wl_range_slider = widgets.IntRangeSlider(description='intensity:',
                                              min=r_values[0],
                                              max=r_values[1],
                                              step=1,
                                              value = [i_values[0], i_values[1]],
                                              width='20em',
                                              disabled = len(npa.shape) == 4)
            # wl_range_slider.observe(self.on_wl_slider_value_change, names='value')
            self.wl_list.append(wl_range_slider)

        for ax, npa, slider, wl_slider in zip(
            self.axes, self.npa_list, self.slider_list, self.wl_list
        ):
            self.slc[self.axis] = slice(slider.value, slider.value + 1)
            # Need to use squeeze to collapse degenerate dimension (e.g. RGB image size 124 124 1 3)
            ax.imshow(
                np.squeeze(npa[tuple(self.slc)]),
                cmap=plt.cm.Greys_r,
                vmin=wl_slider.value[0],
                vmax=wl_slider.value[1],
            )
        plt.tight_layout()
        plt.savefig(os.path.join(output_file))
    
    def get_window_level_numpy_array(self, image_list, window_level_list=None, intensity_slider_range_percentile=[0,100]):
        # Using GetArray and not GetArrayView because we don't keep references
        # to the original images. If they are deleted outside the view would become
        # invalid, so we use a copy wich guarentees that the gui is consistent.
        npa_list = list(map(sitk.GetArrayFromImage, image_list))

        wl_range = []
        wl_init = []
        # We need to iterate over the images because they can be a mix of
        # grayscale and color images. If they are color we set the wl_range
        # to [0,255] and the wl_init is equal, ignoring the window_level_list
        # entry.
        for i, npa in enumerate(npa_list):
            if len(npa.shape) == 4: #color image
                wl_range.append((0,255))
                wl_init.append((0,255))
                # ignore any window_level_list entry
            else:
                # We don't necessarily take the minimum/maximum values, just in case there are outliers
                # user can specify how much to take off from top and bottom.
                min_max = np.percentile(npa.flatten(), intensity_slider_range_percentile)
                wl_range.append((min_max[0], min_max[1]))
                if not window_level_list: # No list was given.
                    wl_init.append(wl_range[-1])
                else:
                    wl = window_level_list[i]
                    if wl:
                        wl_init.append((wl[1]-wl[0]/2.0, wl[1]+wl[0]/2.0))
                    else: # We have a list, but for this image the entry was left empty: []
                        wl_init.append(wl_range[-1])
        return (npa_list, wl_range, wl_init)