import boto3
import uuid
import os
from django.conf import settings

# Build S3 client config - supports both AWS S3 and MinIO
s3_config = {
    "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
    "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
    "region_name": settings.AWS_REGION,
}

# Add endpoint_url for MinIO or other S3-compatible services
if settings.AWS_S3_ENDPOINT_URL:
    s3_config["endpoint_url"] = settings.AWS_S3_ENDPOINT_URL

s3 = boto3.client("s3", **s3_config)

def generate_presigned_upload(user_id, content_type):
    key = f"posts/{user_id}/{uuid.uuid4()}.jpg"

    upload_url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": settings.AWS_S3_BUCKET,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=300,  # URL expires in 5 minutes
    )

    return {
        "uploadUrl": upload_url,
        "publicUrl": key,
    }
