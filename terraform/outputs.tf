output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.product_images.id
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.product_images.arn
}

output "bucket_domain_name" {
  description = "Bucket domain name"
  value       = aws_s3_bucket.product_images.bucket_domain_name
}

output "bucket_regional_domain_name" {
  description = "Bucket regional domain name"
  value       = aws_s3_bucket.product_images.bucket_regional_domain_name
}

output "public_url_format" {
  description = "Format for public URLs to images"
  value       = "https://${aws_s3_bucket.product_images.bucket_regional_domain_name}/your-image-file.jpg"
}