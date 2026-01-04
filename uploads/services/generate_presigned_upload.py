import boto3
import uuid
from django.conf import settings

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)

def generate_presigned_upload(user_id, data):
    key = f"posts/{user_id}/{uuid.uuid4()}.jpg"

    upload_url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": settings.AWS_S3_BUCKET,
            "Key": key,
            "ContentType": data["contentType"],
        },
        ExpiresIn=300,  # URL expires in 5 minutes
    )

    public_url = f"https://{settings.AWS_S3_BUCKET}.s3.amazonaws.com/{key}"

    return {
        "uploadUrl": upload_url,
        "publicUrl": public_url,
    }
