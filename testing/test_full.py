from pathlib import Path
import requests, zipfile, io, os, csv, random, copy, shutil, sys
import SimpleITK as sitk


def test_download_data():
    """
    This function downloads the sample data, which is the first step towards getting everything ready
    """
    urlToDownload = "https://github.com/CBICA/FigureGenerator/raw/main/testing/data.zip"
    # do not download data again
    if not Path(os.getcwd() + "/testing/data/fl.nii.gz").exists():
        print("Downloading and extracting sample data")
        r = requests.get(urlToDownload)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall("./testing")
