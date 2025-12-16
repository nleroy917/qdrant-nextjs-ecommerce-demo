import os
import sys
import zipfile

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple

import boto3

from botocore.exceptions import ClientError
from tqdm import tqdm

import mimetypes

# configuration
BUCKET_NAME = "qdrant-nextjs-demo-product-images"  # must match terraform bucket_name
MAX_WORKERS = 20  # number of parallel upload threads (adjust based on your connection)
S3_PREFIX = "images/"  # prefix/folder in S3 where images will be stored

# supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.ico'}


def extract_zip(zip_path: str, extract_to: str) -> str:
    """
    Extract zip file to specified directory.

    Args:
        zip_path (str): Path to the zip file.
        extract_to (str): Directory to extract files to.
    Returns:
        str: Path to the extracted directory.
    """
    print(f"Extracting {zip_path}...")
    extract_path = Path(extract_to)
    extract_path.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    print(f"Extracted to {extract_path}")
    return str(extract_path)


def find_images(directory: str) -> List[Tuple[str, str]]:
    """
    Recursively find all image files in directory.
    Returns list of tuples: (local_path, s3_key)
    """
    images = []
    root_path = Path(directory)

    for file_path in root_path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            relative_path = file_path.relative_to(root_path)
            s3_key = S3_PREFIX + str(relative_path).replace('\\', '/')
            images.append((str(file_path), s3_key))

    return images


def get_content_type(file_path: str) -> str:
    """
    Get MIME type for file.
    """
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type or 'application/octet-stream'


def upload_file_to_s3(s3_client, local_path: str, s3_key: str) -> Tuple[bool, str, str]:
    """
    Upload a single file to S3.
    Returns: (success, local_path, error_message)
    """
    try:
        content_type = get_content_type(local_path)

        # upload with progress disabled for individual files (use overall progress bar)
        s3_client.upload_file(
            local_path,
            BUCKET_NAME,
            s3_key,
            ExtraArgs={
                'ContentType': content_type,
            }
        )
        return (True, local_path, "")
    except ClientError as e:
        return (False, local_path, str(e))
    except Exception as e:
        return (False, local_path, str(e))


def upload_images_parallel(images: List[Tuple[str, str]], max_workers: int = MAX_WORKERS):
    """
    Upload images to S3 using thread pool.
    """
    # initialize S3 client
    s3_client = boto3.client('s3')

    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print(f"✓ Connected to S3 bucket: {BUCKET_NAME}")
    except ClientError as e:
        print(f"✗ Error accessing bucket {BUCKET_NAME}: {e}")
        print("Make sure you've run 'terraform apply' and the bucket exists.")
        sys.exit(1)

    print(f"\nUploading {len(images)} images with {max_workers} parallel workers...")

    successful = 0
    failed = 0
    errors = []

    # create a progress bar
    with tqdm(total=len(images), unit='file') as pbar:
        # use ThreadPoolExecutor for parallel uploads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # submit all upload tasks
            future_to_image = {
                executor.submit(upload_file_to_s3, s3_client, local_path, s3_key): (local_path, s3_key)
                for local_path, s3_key in images
            }

            # process completed uploads
            for future in as_completed(future_to_image):
                success, local_path, error_msg = future.result()

                if success:
                    successful += 1
                else:
                    failed += 1
                    errors.append((local_path, error_msg))

                pbar.update(1)

    # print summary
    print(f"\n{'='*60}")
    print("Upload Complete!")
    print(f"{'='*60}")
    print(f"✓ Successful: {successful}")
    if failed > 0:
        print(f"✗ Failed: {failed}")
        print("\nErrors:")
        for path, error in errors[:10]:  # Show first 10 errors
            print(f"  {path}: {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")

    # print example URLs
    if successful > 0:
        print("\nYour images are now publicly accessible!")
        example_key = images[0][1]
        print("\nExample URL format:")
        print(f"https://{BUCKET_NAME}.s3.amazonaws.com/{example_key}")
        print("\nOr using regional domain:")
        # Get bucket region
        try:
            region = s3_client.get_bucket_location(Bucket=BUCKET_NAME)['LocationConstraint']
            if region is None:
                region = 'us-east-1'
            print(f"https://{BUCKET_NAME}.s3.{region}.amazonaws.com/{example_key}")
        except Exception:
            pass


def main():
    global BUCKET_NAME, MAX_WORKERS, S3_PREFIX

    import argparse

    parser = argparse.ArgumentParser(description='Upload images from zip to S3')
    parser.add_argument('path', help='Path to zip file or directory containing images')
    parser.add_argument('--bucket', default=BUCKET_NAME, help=f'S3 bucket name (default: {BUCKET_NAME})')
    parser.add_argument('--workers', type=int, default=MAX_WORKERS, help=f'Number of parallel workers (default: {MAX_WORKERS})')
    parser.add_argument('--prefix', default=S3_PREFIX, help=f'S3 key prefix (default: {S3_PREFIX})')
    parser.add_argument('--no-extract', action='store_true', help='Skip extraction (if path is already a directory)')

    args = parser.parse_args()

    # update globals from args
    BUCKET_NAME = args.bucket
    MAX_WORKERS = args.workers
    S3_PREFIX = args.prefix

    path = Path(args.path)

    # check if path exists
    if not path.exists():
        print(f"Error: Path {path} does not exist")
        sys.exit(1)

    # extract zip if needed
    if path.suffix.lower() == '.zip' and not args.no_extract:
        extract_dir = path.parent / path.stem
        image_dir = extract_zip(str(path), str(extract_dir))
    elif path.is_dir():
        image_dir = str(path)
    else:
        print(f"Error: {path} is not a zip file or directory")
        sys.exit(1)

    # find all images
    print(f"\nScanning for images in {image_dir}...")
    images = find_images(image_dir)

    if not images:
        print("No images found!")
        sys.exit(1)

    print(f"Found {len(images)} images")

    # calculate total size
    total_size = sum(os.path.getsize(img[0]) for img in images)
    print(f"Total size: {total_size / (1024**3):.2f} GB")

    # confirm before uploading
    response = input(f"\nUpload {len(images)} images to s3://{BUCKET_NAME}/{S3_PREFIX}? (y/n): ")
    if response.lower() != 'y':
        print("Upload cancelled")
        sys.exit(0)

    # upload images
    upload_images_parallel(images, args.workers)


if __name__ == '__main__':
    main()