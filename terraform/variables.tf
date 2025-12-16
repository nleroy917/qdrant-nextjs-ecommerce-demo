variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Name of the S3 bucket for product images"
  type        = string
  default     = "qdrant-nextjs-demo-product-images"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}