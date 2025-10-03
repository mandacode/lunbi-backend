"""Download the Chroma index from S3 when it is missing locally."""

import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from lunbi.config import CHROMA_PATH, AWS_SECRET_KEY, AWS_ACCESS_KEY

BUCKET_NAME = "lunbi"
OBJECT_KEY = "chroma.zip"
REGION = "eu-west-1"
INDEX_FILENAME = "chroma.sqlite3"


def chroma_exists() -> bool:
    index_path = CHROMA_PATH / INDEX_FILENAME
    return index_path.exists()


def download_zip(target_path: Path) -> None:
    try:
        session = boto3.Session(
            region_name=REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
        )
        client = session.client("s3")
        client.download_file(BUCKET_NAME, OBJECT_KEY, str(target_path))
    except (BotoCoreError, ClientError) as error:
        raise RuntimeError(f"Failed to download s3://{BUCKET_NAME}/{OBJECT_KEY}: {error}") from error


def _copy_contents(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for entry in source.iterdir():
        target = destination / entry.name
        if entry.is_dir():
            shutil.copytree(entry, target, dirs_exist_ok=True)
        else:
            shutil.copy2(entry, target)


def extract_zip(zip_path: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    try:
        with zipfile.ZipFile(zip_path) as archive, tempfile.TemporaryDirectory() as tmp_dir:
            archive.extractall(tmp_dir)
            staging = Path(tmp_dir)
            candidates = [item for item in staging.iterdir() if item.name != "__MACOSX"]
            if len(candidates) == 1 and candidates[0].is_dir():
                source = candidates[0]
            else:
                source = staging
            _copy_contents(source, destination)
    except zipfile.BadZipFile as error:
        shutil.rmtree(destination, ignore_errors=True)
        raise RuntimeError(f"Invalid zip archive at {zip_path}") from error
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    index_path = destination / INDEX_FILENAME
    if not index_path.exists():
        shutil.rmtree(destination, ignore_errors=True)
        raise RuntimeError(f"Extraction did not produce {index_path}")


def main() -> int:
    if chroma_exists():
        print(f"Found {CHROMA_PATH / INDEX_FILENAME}; skipping download.")
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
