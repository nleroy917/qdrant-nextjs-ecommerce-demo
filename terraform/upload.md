# Image Upload Guide

## Prerequisites

1. **Install Python dependencies:**

   ```bash
   uv pip install -r requirements.txt
   ```

2. **Configure AWS credentials** (if not already done):

   ```bash
   aws configure
   ```

3. **Deploy the S3 bucket:**
   ```bash
   terraform init
   terraform apply
   ```

If you wish to tear down the S3 bucket later, run:

```bash
terraform destroy
```

## Quick Upload

### Option 1: Using the Python Script (Recommended for Speed)

The script supports multi-threaded uploads (default: 20 parallel workers) for maximum speed.

```bash
# upload from zip file (will auto-extract)
python upload_images.py /path/to/your/images.zip

# upload from directory
python upload_images.py /path/to/extracted/folder --no-extract

# custom options
python upload_images.py images.zip \
  --bucket your-bucket-name \
  --workers 30 \
  --prefix images/products/
```

### Option 2: Using AWS CLI (Simpler, but potentially slower)

```bash
# extract the zip first
unzip images.zip -d ./images

# upload with sync (has some parallelization)
aws s3 sync ./images s3://your-bucket-name/images/ \
  --exclude "*" \
  --include "*.jpg" \
  --include "*.jpeg" \
  --include "*.png" \
  --include "*.gif" \
  --include "*.webp"
```

## Performance Tips

1. **Adjust worker count** based on your connection:

   - Fast connection (500+ Mbps): `--workers 50`
   - Medium (100-500 Mbps): `--workers 20` (default)
   - Slower (<100 Mbps): `--workers 10`

2. **Monitor upload progress** - the script shows a progress bar and ETA

3. **Resume failed uploads** - if upload fails, you can re-run the script (S3 will skip existing files by default)

## After Upload

Your images will be publicly accessible at:

```
https://your-bucket-name.s3.amazonaws.com/images/path/to/image.jpg
```

Or with regional domain:

```
https://your-bucket-name.s3.us-east-1.amazonaws.com/images/path/to/image.jpg
```

## Troubleshooting

**"Access Denied" error:**

- Make sure you've run `terraform apply`
- Check your AWS credentials: `aws sts get-caller-identity`

**Slow uploads:**

- Increase workers: `--workers 50`
- Check your internet upload speed
- Consider using AWS CLI's `s3 cp` with `--recursive` flag

**Out of memory:**

- The script processes files one at a time, so memory usage is minimal
- If extraction fails, extract the zip manually first

## Cost Monitoring

After upload, check costs:

```bash
# See how much data is in your bucket
aws s3 ls s3://your-bucket-name --recursive --human-readable --summarize
```

For 32GB:

- Storage: ~$0.74/month
- No transfer costs until images are accessed
