# Screenshot Maker

This project helps create screenshots for medical images for use in presentations and/or manuscripts.

## Usage

```powershell
python ./screenshot_run -h
usage: ScreenshotMaker [-h] -images IMAGES [-masks MASKS]
                       [-mask_opacity MASK_OPACITY] [-colormap COLORMAP]
                       -output OUTPUT [-axisrow AXISROW] [-bounded BOUNDED]
                       [-borderpc BORDERPC] [-v]

Constructing screenshots from medical images.

Contact: software@cbica.upenn.edu

This program is NOT FDA/CE approved and NOT intended for clinical use.
Copyright (c) 2021 University of Pennsylvania. All rights reserved.

optional arguments:
  -h, --help            show this help message and exit
  -images IMAGES        Input image files (comma-separated without any spaces in path and co-registered)
  -masks MASKS          Mask files  (comma-separated without any spaces in path and co-registered with images); if multiple files are passed, first is ground truth
  -mask_opacity MASK_OPACITY
                        Mask opacity between 0-1
  -output OUTPUT        Output screenshot file
  -axisrow AXISROW      Put all axes views across each column and stack images and blends in rows, defaults to False
  -bounded BOUNDED      Construct bounding box around binarized ground truth
  -borderpc BORDERPC    Percentage of size to use as border around bounding box (used only when mask and bounded are defined)
  -v, --version         Show program's version number and exit.
```

- Image (single or multiple co-registered)
  - for multiple images:
    - perform sanity check 
- Mask: Optional
  - for multiple masks (in case of showing ground truth and computationally-generated masks), assume first is ground truth
  - perform sanity check 
- Mask opacity: Optional (default is 100 - full opacity)
- Slice number: Optional
  - if not defined and mask is present, binarize the mask (first file if multiple masks are passed) and use the slices with largest area
  - if not defined and mask is absent, use middle of each axis from image(s)

## Outputs

### For single image

A single PNG:
- All axes views along the x-axis
- Show only the image in the first row
- Second row image and mask overlaid based on opacity
- Repeat one row per mask file 

### For multiple images

Two images:
1. Stack previous in in multiple rows (2-column manuscript)
2. Stack previous in in multiple columns (1-column manuscript)
