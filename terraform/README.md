# Terraform Configuration for Product Images S3 Bucket

This Terraform configuration sets up an S3 bucket for hosting product images with public read access.

## Prerequisites

1. Install Terraform: https://www.terraform.io/downloads
2. Configure AWS credentials:
   ```bash
   aws configure
   ```

## Usage

### 1. Initialize Terraform
```bash
cd terraform
terraform init
```

### 2. Customize Variables (Optional)
Edit `variables.tf` or create a `terraform.tfvars` file:
```hcl
aws_region  = "us-east-1"
bucket_name = "your-unique-bucket-name"
environment = "production"
```

**Important**: S3 bucket names must be globally unique. Change the `bucket_name` variable to something unique to your project.

### 3. Plan the Infrastructure
```bash
terraform plan
```

### 4. Apply the Configuration
```bash
terraform apply
```

### 5. Get the Bucket Information
After applying, Terraform will output the bucket details. You can also view them anytime with:
```bash
terraform output
```

## Uploading Images

### Using AWS CLI
```bash
# Upload a single file
aws s3 cp image.jpg s3://your-bucket-name/images/

# Upload a directory
aws s3 sync ./local-images/ s3://your-bucket-name/images/

# Upload with public-read ACL (optional, policy already allows public read)
aws s3 cp image.jpg s3://your-bucket-name/images/ --acl public-read
```

### Accessing Images
Your images will be publicly accessible at:
```
https://your-bucket-name.s3.amazonaws.com/images/your-image.jpg
```
or
```
https://your-bucket-name.s3.us-east-1.amazonaws.com/images/your-image.jpg
```

## Cost Estimation

For approximately 32GB of images:
- **Storage**: ~$0.74/month (S3 Standard at $0.023 per GB)
- **Data Transfer**: First 100GB out is ~$9/month (only charged when images are downloaded)
- **Requests**: Minimal cost for GET requests (~$0.0004 per 1,000 requests)

Total estimated cost: **Less than $2-10/month** depending on traffic.

## Cleanup

To destroy all resources:
```bash
terraform destroy
```

**Warning**: This will permanently delete the bucket and all images. Make sure to backup your data first.