from flask import Flask, request, jsonify, send_from_directory
from actions import bp as actionsbp
from filters import bp as filtersbp
from android import bp as androidbp
import boto3, botocore

from helpers import allowed_extension, upload_to_s3

UPLOAD_FOLDER = "uploads/"
DOWNLOAD_FOLDER = 'downloads/'
ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg"]
app = Flask(__name__)

app.config["S3_BUCKET"]="imageapibucket"
app.config["S3_KEY"]="AKIA44Y6CYGWMJVHSQ5B"
app.config["S3_SECRET"]="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"
app.config["S3_LOCATION"]="https://imageapibucket.s3.eu-north-1.amazonaws.com/uploads/"

app.secret_key = "SECRET_KEY"

app.register_blueprint(actionsbp)
app.register_blueprint(filtersbp)
app.register_blueprint(androidbp)


app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["DOWNLOAD_FOLDER"] = DOWNLOAD_FOLDER
app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS


@app.route("/images", methods=[ "GET","POST"])
def image():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file was selected"}), 404

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No file was selected"}), 404

        if not allowed_extension(file.filename):
            return jsonify({"error": "The extension is not supported"}), 400

        output = upload_to_s3(file, app.config['S3_BUCKET'])
        return jsonify({"message": "File successfully upload", "filename": str(output)}),201
    
    images = []
    s3_resource = boto3.resource('s3', aws_access_key_id=app.config['S3_KEY'], aws_secret_access_key=app.config['S3_SECRET'])
    s3_bucket = s3_resource.Bucket(app.config['S3_BUCKET'])

    for obj in s3_bucket.objects.filter(Prefix='uploads/'):
        if obj.key == 'uploads/':
            continue
        images.append(obj.key)
    return jsonify({"data": images}), 200

@app.route('/downloads/<name>')
def download_image(name):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],name)

if __name__ == "__main__":
    app.run()