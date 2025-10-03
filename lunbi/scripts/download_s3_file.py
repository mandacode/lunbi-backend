"""Download the Chroma index from S3 when it is missing locally."""

import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from lunbi.config import CHROMA_PATH

BUCKET_NAME = "lunbi"
OBJECT_KEY = "chroma.zip"
REGION = "eu-west-1"


def chroma_exists() -> bool:
    return CHROMA_PATH.exists()


def download_zip(target_path: Path) -> None:
    try:
        session = boto3.Session(region_name=REGION)
        client = session.client("s3")
        client.download_file(BUCKET_NAME, OBJECT_KEY, str(target_path))
    except (BotoCoreError, ClientError) as error:
        raise RuntimeError(f"Failed to download s3://{BUCKET_NAME}/{OBJECT_KEY}: {error}") from error


def extract_zip(zip_path: Path, destination: Path) -> None:
    try:
        with zipfile.ZipFile(zip_path) as archive:
            members = [name for name in archive.namelist() if name.rstrip("/")]
            if not members:
                raise RuntimeError(f"Archive {zip_path} is empty")
            top_level = {name.split("/", 1)[0] for name in members}
            extract_to_parent = top_level == {destination.name}
            if not extract_to_parent:
                destination.mkdir(parents=True, exist_ok=False)
            archive.extractall(destination.parent if extract_to_parent else destination)
    except zipfile.BadZipFile as error:
        shutil.rmtree(destination, ignore_errors=True)
        raise RuntimeError(f"Invalid zip archive at {zip_path}") from error
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    if not destination.exists():
        raise RuntimeError(f"Extraction did not produce {destination}")


def main() -> int:
    if chroma_exists():
        print(f"Chroma directory already present at {CHROMA_PATH}; skipping download.")
        return 0

    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = Path(tmp_dir) / OBJECT_KEY
        try:
            download_zip(zip_path)
            extract_zip(zip_path, CHROMA_PATH)
        except RuntimeError as error:
            print(str(error), file=sys.stderr)
            return 1

    print(f"Downloaded and extracted s3://{BUCKET_NAME}/{OBJECT_KEY} to {CHROMA_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
