from pathlib import Path
import requests, zipfile, io, os, argparse
import SimpleITK as sitk

from FigureGenerator.screenshot_maker import FigureGenerator
from FigureGenerator.utils import sanity_checker_with_files

## global variables
inputDir = os.path.abspath(os.path.normpath("./testing/data"))
baseImagesDir = os.path.abspath(os.path.normpath("./images"))
args = argparse.Namespace
args.images = (
    os.path.join(inputDir, "fl.nii.gz")
    + ","
    + os.path.join(inputDir, "t1c.nii.gz")
    + ","
    + os.path.join(inputDir, "t1.nii.gz")
    + ","
    + os.path.join(inputDir, "t2.nii.gz")
)
args.masks = os.path.join(inputDir, "seg.nii.gz")
args.output = os.path.join(inputDir, "output.png")
args.opacity = 0.5
args.axisrow = True
args.boundimg = False
args.boundmask = False
args.borderpc = 0.1
args.ylabels = "FL,T1C,T1,T2,FL+seg,T1C+seg,T1+seg,T2+seg",


def test_download_data():
    """This function downloads the sample data, which is the first step towards getting everything ready"""
    urlToDownload = "https://github.com/CBICA/FigureGenerator/raw/main/testing/data.zip"
    # do not download data again
    if not Path(os.path.join(inputDir, "fl.nii.gz")).exists():
        print("Downloading and extracting sample data")
        r = requests.get(urlToDownload)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall("./testing")


def test_axis_true_bounded_false():
    if os.path.exists(args.output):
        os.remove(args.output)
    args.axisrow = False
    fig_generator = FigureGenerator(args)
    fig_generator.save_image(fig_generator.output)
    file_to_check = os.path.join(baseImagesDir, "fig_axisrowfalse.png")
    assert sanity_checker_with_files(
        args.output, file_to_check
    ), "axis row false bounded false failed"

    os.remove(args.output)
    print("Passed")


def test_axis_false_bounded_false():
    if os.path.exists(args.output):
        os.remove(args.output)
    args.axisrow = True
    fig_generator = FigureGenerator(args)
    fig_generator.save_image(fig_generator.output)
    file_to_check = os.path.join(baseImagesDir, "fig_axisrowtrue.png")
    assert sanity_checker_with_files(
        args.output, file_to_check
    ), "axis row true bounded false failed"

    os.remove(args.output)
    print("Passed")


def test_axis_true_bounded_image():
    if os.path.exists(args.output):
        os.remove(args.output)
    args.axisrow = True
    args.boundimg = True
    fig_generator = FigureGenerator(args)
    fig_generator.save_image(fig_generator.output)
    file_to_check = os.path.join(baseImagesDir, "fig_axisrowtrue_boundedimage.png")
    assert sanity_checker_with_files(
        args.output, file_to_check
    ), "axis row true bounded image failed"

    os.remove(args.output)
    print("Passed")


def test_axis_true_bounded_mask():
    if os.path.exists(args.output):
        os.remove(args.output)
    args.axisrow = True
    args.boundmask = True
    fig_generator = FigureGenerator(args)
    fig_generator.save_image(fig_generator.output)
    file_to_check = os.path.join(baseImagesDir, "fig_axisrowtrue_boundedmask.png")
    assert sanity_checker_with_files(
        args.output, file_to_check
    ), "axis row true bounded mask failed"

    os.remove(args.output)
    print("Passed")
