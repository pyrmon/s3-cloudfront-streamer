terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "ap-northeast-1"
}

variable "bucket_prefix" {
  description = "Prefix for S3 bucket name"
  type        = string
  default     = "video-streaming"
}

variable "public_key_file" {
  description = "Path to CloudFront public key file"
  type        = string
  default     = "public_key.pem"
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "streaming_bucket" {
  bucket = "${var.bucket_prefix}-${random_id.bucket_suffix.hex}"
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket_public_access_block" "streaming_bucket_pab" {
  bucket = aws_s3_bucket.streaming_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_cloudfront_origin_access_control" "streaming_oac" {
  name                              = "streaming-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_s3_bucket_policy" "streaming_bucket_policy" {
  bucket = aws_s3_bucket.streaming_bucket.id
  policy = jsonencode({
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "cloudfront.amazonaws.com"
      }
      Action   = "s3:GetObject"
      Resource = "${aws_s3_bucket.streaming_bucket.arn}/*"
      Condition = {
        StringEquals = {
          "AWS:SourceArn" = aws_cloudfront_distribution.streaming_distribution.arn
        }
      }
    }]
  })
}

resource "aws_cloudfront_public_key" "video_key" {
  name        = "video-streaming-key"
  encoded_key = file(var.public_key_file)
}

resource "aws_cloudfront_key_group" "video_keys" {
  name  = "video-streaming-keys"
  items = [aws_cloudfront_public_key.video_key.id]
}

resource "aws_cloudfront_distribution" "streaming_distribution" {
  enabled = true
  comment = "Video streaming distribution"

  origin {
    domain_name              = aws_s3_bucket.streaming_bucket.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.streaming_bucket.id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.streaming_oac.id
  }

  default_cache_behavior {
    target_origin_id       = "S3-${aws_s3_bucket.streaming_bucket.id}"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    trusted_key_groups     = [aws_cloudfront_key_group.video_keys.id]
    compress               = false
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    min_ttl     = 0
    default_ttl = 86400
    max_ttl     = 31536000
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

output "bucket_name" {
  value = aws_s3_bucket.streaming_bucket.bucket
}

output "distribution_id" {
  value = aws_cloudfront_distribution.streaming_distribution.id
}

output "distribution_domain" {
  value = aws_cloudfront_distribution.streaming_distribution.domain_name
}

output "key_pair_id" {
  value = aws_cloudfront_public_key.video_key.id
}

output "aws_region" {
  value = var.aws_region
}