from pathlib import Path
import requests, zipfile, io, os

from FigureGenerator.screenshot_maker import FigureGenerator

## global variables
inputDir = os.path.abspath(os.path.normpath("./testing/data"))
args = {}
args.images = os.join(inputDir, "fl.nii.gz") + "," + os.join(inputDir, "t1.nii.gz") + "," + os.join(inputDir, "t2.nii.gz") + "," + os.join(inputDir, "t1ce.nii.gz")
args.masks = os.join(inputDir, "seg.nii.gz")
args.output = os.join(inputDir, "output.nii.gz")

def test_download_data():
    """
    This function downloads the sample data, which is the first step towards getting everything ready
    """
    urlToDownload = "https://github.com/CBICA/FigureGenerator/raw/main/testing/data.zip"
    # do not download data again
    if not Path(os.join(inputDir, "fl.nii.gz")).exists():
        print("Downloading and extracting sample data")
        r = requests.get(urlToDownload)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall("./testing")


def test_axis_true_bounded_false():
    if os.path.exists(args.output):
        os.remove(args.output)
    args.axisrow = False


def test_axis_false_bounded_false():
    if os.path.exists(args.output):
        os.remove(args.output)
    args.axisrow = True


def test_axis_true_bounded_image():
    if os.path.exists(args.output):
        os.remove(args.output)
    args.axisrow = True
    args.boundimg = True


def test_axis_true_bounded_mask():
    if os.path.exists(args.output):
        os.remove(args.output)
    args.axisrow = True
    args.boundmask = True