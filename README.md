# Figure Generator

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
usage: ScreenshotMaker [-h] -images IMAGES [-masks MASKS] [-opacity OPACITY]
                       -output OUTPUT [-axisrow AXISROW] [-bounded BOUNDED] 
                       [-boundmask BOUNDMASK] [-borderpc BORDERPC] [-v]     

Constructing screenshots from medical images.

Contact: software@cbica.upenn.edu

This program is NOT FDA/CE approved and NOT intended for clinical use.
Copyright (c) 2021 University of Pennsylvania. All rights reserved.

optional arguments:
  -h, --help            show this help message and exit
  -images IMAGES        Input image files (comma-separated without any spaces in path and co-registered)
  -masks MASKS          Mask files  (comma-separated without any spaces in path and co-registered with images); if multiple files are passed, first is ground truth
  -opacity OPACITY      Mask opacity between 0-1
  -output OUTPUT        Output screenshot file
  -axisrow AXISROW      Put all axes views across each column and stack images and blends in rows, defaults to False
  -bounded BOUNDED      Construct bounding box around non-zero pixels of input images
  -boundmask BOUNDMASK  Construct bounding box around binarized ground truth
  -borderpc BORDERPC    Percentage of size to use as border around bounding box (used only when mask and bounded are defined)
  -v, --version         Show program's version number and exit.
```

### Examples

1. **Vertical** screenshot of multiple images **without** bounding:
```powershell
python ./figure_generator \
-images C:/input/subject_001_flair.nii.gz,C:/input/subject_001_t1ce.nii.gz,C:/input/subject_001_t1.nii.gz,C:/input/subject_001_t2.nii.gz \
-masks C:/input/subject_001_seg.nii.gz \
-axisrow False \
-output C:/input/fig.png 
```
Gives the following output:

<p align="center">
  <img width="450" src="images/fig_axisrowfalse.png">
</p>
<!-- full-size image
[<img src="images/fig_axisrowfalse.png" width="450"/>](axisrow_false)
![axisrow_false](images/fig_axisrowfalse.png)
 -->

2. **Horizontal** screenshot of multiple images **without** bounding:
```powershell
python ./figure_generator \
-images C:/input/subject_001_flair.nii.gz,C:/input/subject_001_t1ce.nii.gz,C:/input/subject_001_t1.nii.gz,C:/input/subject_001_t2.nii.gz \
-masks C:/input/subject_001_seg.nii.gz \
-axisrow True \
-output C:/input/fig.png 
```
Gives the following output:

[<img src="images/fig_axisrowtrue.png" width="900"/>](axisrow_true)
<!-- full-size image
![axisrow_true](images/fig_axisrowtrue.png)
 -->

3. Horizontal screenshot of multiple images with **image-based bounding**:
```powershell
python ./figure_generator \
-images C:/input/subject_001_flair.nii.gz,C:/input/subject_001_t1ce.nii.gz,C:/input/subject_001_t1.nii.gz,C:/input/subject_001_t2.nii.gz \
-masks C:/input/subject_001_seg.nii.gz \
-axisrow True \
-bounded True \
-output C:/input/fig.png 
```
Gives the following output:

[<img src="images/fig_axistrue_boundedimage.png" width="900"/>](axistrue_boundedimage)
<!-- full-size image
![axisrow_true](images/fig_axistrue_boundedimage.png)
 -->

**Note**: This can be used with vertical orientation as well, by passing `-axisrow False` to the command.

4. Horizontal screenshot of multiple images with **mask-based bounding**:
```powershell
python ./figure_generator \
-images C:/input/subject_001_flair.nii.gz,C:/input/subject_001_t1ce.nii.gz,C:/input/subject_001_t1.nii.gz,C:/input/subject_001_t2.nii.gz \
-masks C:/input/subject_001_seg.nii.gz \
-axisrow True \
-boundmask True \
-borderpc 0.001 \
-output C:/input/fig.png 
```
Gives the following output:

[<img src="images/fig_axistrue_boundedmask.png" width="900"/>](axistrue_boundedmask)
<!-- full-size image
![axisrow_true](images/fig_axistrue_boundedmask.png)
 -->

**Note**: This can be used with vertical orientation as well, by passing `-axisrow False` to the command.

## Feedback

Please post on GitHub [Discussions](https://github.com/CBICA/FigureGenerator/discussions) or post an [issue](https://github.com/CBICA/FigureGenerator/issues/new/choose).
