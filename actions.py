from flask import Blueprint, jsonify, request, redirect, url_for, current_app
from PIL import Image
from helpers import get_secure_filename_filepath, download_from_s3
import os 

bp = Blueprint("actions", __name__, url_prefix="/actions")


@bp.route("/resize", methods=["POST"])
def resize():
    filename = request.json["filename"]
    filename, filepath = get_secure_filename_filepath(filename)
    try:
        width, height = int(request.json["width"]), int(request.json["height"])
        file_stream = download_from_s3(filename)
        image = Image.open(file_stream)
        out = image.resize((width, height))
        out.save(os.path.join(current_app.config['DOWNLOAD_FOLDER'], filename))
        return redirect(url_for("download_image", name=filename))
    except FileNotFoundError:
        return jsonify({"message": "File not found"}), 404


@bp.route("/presets/<preset>", methods=["POST"])
def resize_preset(preset):
    prestes = {"small": (600, 500), "medium": (1280, 960), "large": (1600, 1200)}
    if preset not in prestes:
        return jsonify({"message": "the preset is not available"}), 404

    filename = request.json["filename"]
    filename, filepath = get_secure_filename_filepath(filename)
    try:
        size = prestes[preset]
        file_stream = download_from_s3(filename)
        image = Image.open(file_stream)
        out = image.resize(size=size)
        out.save(os.path.join(current_app.config['DOWNLOAD_FOLDER'], filename))
        return redirect(url_for("download_image", name=filename))

    except FileNotFoundError:
        return jsonify({"message": "File not found"}), 404


@bp.route("/rotate", methods=["POST"])
def rotate():
    filename = request.json["filename"]
    filename, filepath = get_secure_filename_filepath(filename)
    try:
        degree = float(request.json["degree"])
        file_stream = download_from_s3(filename)
        image = Image.open(file_stream)
        out = image.rotate(degree)
        out.save(os.path.join(current_app.config['DOWNLOAD_FOLDER'], filename))
        return redirect(url_for("download_image", name=filename))

    except FileNotFoundError:
        return jsonify({"message": "File not found"}), 404


@bp.route("/flip", methods=["POST"])
def flip():
    filename = request.json["filename"]
    filename, filepath = get_secure_filename_filepath(filename)
    try:
        file_stream = download_from_s3(filename)
        image = Image.open(file_stream)
        out = None
        if request.json["direction"] == "horizontal":
            out = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        else:
            out = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        out.save(os.path.join(current_app.config['DOWNLOAD_FOLDER'], filename))
        return redirect(url_for("download_image", name=filename))

    except FileNotFoundError:
        return jsonify({"message": "File not found"}), 404
