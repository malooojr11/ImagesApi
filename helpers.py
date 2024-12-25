import os
from flask import current_app, jsonify
from werkzeug.utils import secure_filename
import boto3
from botocore.exceptions import ClientError


def allowed_extension(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def get_secure_filename_filepath(filename):
    filename = secure_filename(filename)
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    return filename, filepath


from werkzeug.utils import secure_filename
import boto3
import os
from botocore.exceptions import ClientError
from flask import current_app, jsonify


def upload_to_s3(file, bucket_name, acl="public-read"):
    s3_client = boto3.client("s3",aws_access_key_id=current_app.config["S3_KEY"],aws_secret_access_key=current_app.config["S3_SECRET"],)
    file.filename = secure_filename(file.filename)
    s3_key = os.path.join("uploads/", file.filename)

    try:
        # Upload the file to S3
        s3_client.upload_fileobj(file,bucket_name,s3_key,
            ExtraArgs={"ACL": acl, "ContentType": file.content_type},)
    except ClientError as e:
        current_app.logger.error(f"Error uploading file to S3: {e}")
        return jsonify({"message": "Cannot upload files to S3 account. "}), 400

    return s3_key  # Return the S3 key for the uploaded file


def download_from_s3(filename):
    # Ensure the filename is consistent with the upload key
    s3_key = os.path.join('uploads/', filename)

    # Initialize S3 resource
    s3_resource = boto3.resource('s3', aws_access_key_id=current_app.config['S3_KEY'], aws_secret_access_key=current_app.config['S3_SECRET'])
    bucket = s3_resource.Bucket(current_app.config['S3_BUCKET'])
    s3_object = bucket.Object(s3_key)

    try:
        # Get the object from S3
        response = s3_object.get()
        return response['Body']  # Return the file content
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            current_app.logger.error(f"File not found in S3: {s3_key}")
            raise FileNotFoundError(f"The file {filename} does not exist in S3.")
        else:
            current_app.logger.error(f"Error retrieving file from S3: {e}")
            raise
