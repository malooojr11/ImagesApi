from datetime import datetime
import os
import shutil
from flask import Blueprint, current_app, request, redirect, url_for
from helpers import get_secure_filename_filepath, download_from_s3
from PIL import Image
from zipfile import ZipFile

bp = Blueprint("android", __name__, url_prefix="/android")
ICON_SIZES = [29, 40, 57, 58, 60, 80, 87, 114, 120, 180, 1024]


@bp.route("/", methods=["POST"])
def create_images():
    filename = request.json["filename"]
    filename, filepath = get_secure_filename_filepath(filename)
    tempfolder = os.path.join(current_app.config["DOWNLOAD_FOLDER"], "temp")
    os.makedirs(tempfolder)

    for size in ICON_SIZES:
        outfile = os.path.join(tempfolder, f"{size}.png")
        file_stream = download_from_s3(filename)
        image = Image.open(file_stream)
        out = image.resize((size, size))
        out.save(outfile, "PNG")

    now = datetime.now()
    timestamp = str(datetime.timestamp(now)).rsplit(".")[0]
    zipfilename = f"{timestamp}.zip"
    zipfilepath = os.path.join(
        current_app.config["DOWNLOAD_FOLDER"], zipfilename)

    with ZipFile(zipfilepath, "w") as zipObj:
        for foldername,subfolders,filenames, in os.walk(tempfolder):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                zipObj.write(filepath, os.path.basename(filepath))
        shutil.rmtree(tempfolder)
        return redirect(url_for("download_image", name=zipfilename))
