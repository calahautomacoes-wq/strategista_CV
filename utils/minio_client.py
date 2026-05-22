import os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()

_ENDPOINT = os.getenv("MINIO_API_ENDPOINT", "https://bots-strategista-minio.1eybor.easypanel.host")
_BUCKET = os.getenv("MINIO_BUCKET", "curriculos")
_PREFIX = os.getenv("MINIO_PREFIX", "curriculo/")
_S3_NS = "http://s3.amazonaws.com/doc/2006-03-01/"


def list_cv_files() -> list[dict]:
    """List all objects under the configured prefix in the public MinIO bucket."""
    url = f"{_ENDPOINT}/{_BUCKET}"
    params = {"list-type": "2", "prefix": _PREFIX, "max-keys": "1000"}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    # Handle response with or without XML namespace
    ns = _S3_NS if root.tag.startswith("{") else ""
    tag = lambda name: f"{{{_S3_NS}}}{name}" if ns else name  # noqa: E731

    files = []
    for obj in root.iter(tag("Contents")):
        key_el = obj.find(tag("Key"))
        size_el = obj.find(tag("Size"))
        if key_el is None or size_el is None:
            continue
        key = key_el.text
        size = int(size_el.text)
        filename = key.split("/")[-1]
        if size > 0 and filename:
            files.append({"key": key, "filename": filename, "size": size})
    return files


def download_file(key: str) -> bytes:
    """Download a file from the public MinIO bucket."""
    url = f"{_ENDPOINT}/{_BUCKET}/{key}"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return resp.content
