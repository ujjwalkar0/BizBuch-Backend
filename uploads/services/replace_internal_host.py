from urllib.parse import urlparse
from core.request_context import get_current_request
from django.conf import settings

def replace_internal_host(url):
    """
    Replace internal MinIO hostname with user's accessible host.
    Useful for presigned URLs in local/development environments.
    """
    request = get_current_request()
    if not request or not getattr(settings, "AWS_S3_ENDPOINT_URL", None):
        return url

    endpoint = settings.AWS_S3_ENDPOINT_URL
    parsed_endpoint = urlparse(endpoint)
    minio_port = parsed_endpoint.port or 9000

    # Get host from request (e.g., "192.168.0.5:8000" -> "192.168.0.5")
    request_host = request.get_host().split(":")[0]
    scheme = "https" if request.is_secure() else "http"

    # Build public MinIO URL using user's host
    public_minio_url = f"{scheme}://{request_host}:{minio_port}"
    return url.replace(endpoint, public_minio_url)

