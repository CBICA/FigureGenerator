# Screenshot Maker

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/608de602c1bd4bec810efb0d08f269e6)](https://www.codacy.com/gh/CBICA/FigureGenerator/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CBICA/FigureGenerator&amp;utm_campaign=Badge_Grade)

This project helps create high quality figures for medical images for use in presentations and/or manuscripts.

## Installation

```powershell
git clone https://github.com/CBICA/FigureGenerator.git
cd screenshot_maker
conda create -n venv_screenshot python=3.7 -y
conda activate venv_screenshot
pip install -e .
```

OR directly via Pip:

```powershell
pip install FigureGenerator
```

## Usage

```powershell
python ./figure_generator -h
usage: FigureGenerator [-h] -images IMAGES [-masks MASKS]
                       [-mask_opacity MASK_OPACITY]
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
python ./figure_generator \
-images C:/input/subject_001_flair.nii.gz,C:/input/subject_001_t1ce.nii.gz,C:/input/subject_001_t1.nii.gz,C:/input/subject_001_t2.nii.gz \
-masks C:/input/subject_001_seg.nii.gz \
-axisrow False \
-output C:/input/fig.png 
```
Gives the following output:
[<img src="images/axisrow_false.png" width="450"/>](axisrow_false)
<!-- full-size image
![axisrow_false](images/axisrow_false.png)
 -->

2. Horizontal screenshot of multiple images:
```powershell
python ./figure_generator \
-images C:/input/subject_001_flair.nii.gz,C:/input/subject_001_t1ce.nii.gz,C:/input/subject_001_t1.nii.gz,C:/input/subject_001_t2.nii.gz \
-masks C:/input/subject_001_seg.nii.gz \
-axisrow True \
-output C:/input/fig.png 
```
Gives the following output:
![axisrow_true](images/axisrow_true.png)

3. Horizontal screenshot of multiple images with image-based bounding:
```powershell
python ./figure_generator \
-images C:/input/subject_001_flair.nii.gz,C:/input/subject_001_t1ce.nii.gz,C:/input/subject_001_t1.nii.gz,C:/input/subject_001_t2.nii.gz \
-masks C:/input/subject_001_seg.nii.gz \
-axisrow True \
-bounded True \
-output C:/input/fig.png 
```
Gives the following output:
![axisrow_true](images/fig_axistrue_boundedimage.png)

4. Horizontal screenshot of multiple images:
```powershell
python ./figure_generator \
-images C:/input/subject_001_flair.nii.gz,C:/input/subject_001_t1ce.nii.gz,C:/input/subject_001_t1.nii.gz,C:/input/subject_001_t2.nii.gz \
-masks C:/input/subject_001_seg.nii.gz \
-axisrow True \
-boundedmask True \
-output C:/input/fig.png 
```
Gives the following output:
![axisrow_true](images/fig_axistrue_boundedmask.png)

## Feedback

Please post on GitHub [Discussions](https://github.com/CBICA/FigureGenerator/discussions) or post an [issue](https://github.com/CBICA/FigureGenerator/issues/new/choose).
