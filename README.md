# Screenshot Maker

This project helps create screenshots for medical images for use in presentations and/or manuscripts.

## Installation

```powershell
git clone https://github.com/sarthakpati/screenshot_maker.git
cd screenshot_maker
conda create -n venv_screenshot python=3.7 -y
conda activate venv_screenshot
pip install -e .
```

OR directly via Pip:

```powershell
pip install ScreenshotMaker
```

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

### Examples

1. Vertical screenshot of multiple images:
```powershell
python ./screenshot_run -images C:/input/subject_001_flair.nii.gz,C:/input/subject_001_t1ce.nii.gz,C:/input/subject_001_t1.nii.gz,C:/input/subject_001_t2.nii.gz -masks C:/input/subject_001_seg.nii.gz -output C:/input/fig.png -axisrow False
```
Gives the following output:
![axisrow_false](images/axisrow_false.png)

2. Horizontal screenshot of multiple images:
```powershell
python ./screenshot_run -images C:/input/subject_001_flair.nii.gz,C:/input/subject_001_t1ce.nii.gz,C:/input/subject_001_t1.nii.gz,C:/input/subject_001_t2.nii.gz -masks C:/input/subject_001_seg.nii.gz -output C:/input/fig.png -axisrow True
```
Gives the following output:
![axisrow_true](images/axisrow_true.png)
