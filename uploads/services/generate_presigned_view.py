import boto3
from django.conf import settings
from uploads.services.replace_internal_host import replace_internal_host

# Build S3 client config
s3_config = {
    "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
    "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
    "region_name": settings.AWS_REGION,
}

# Add endpoint_url only if configured (for MinIO/local development)
if getattr(settings, "AWS_S3_ENDPOINT_URL", None):
    s3_config["endpoint_url"] = settings.AWS_S3_ENDPOINT_URL

s3 = boto3.client("s3", **s3_config)

def generate_presigned_view(key):
    url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.AWS_S3_BUCKET,
            "Key": key,
        },
        ExpiresIn=3600,
    )
    return replace_internal_host(url)
