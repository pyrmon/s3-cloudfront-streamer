#!/bin/bash

set -e

echo "🚀 S3 CloudFront Video Streamer Setup"
echo "====================================="

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found. Please install Terraform first."
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

if ! command -v openssl &> /dev/null; then
    echo "❌ OpenSSL not found. Please install OpenSSL first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3 first."
    exit 1
fi

echo "✅ All prerequisites found"

# Check AWS credentials
echo "🔐 Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi
echo "✅ AWS credentials configured"

# Generate keys if they don't exist
if [ ! -f "private_key.pem" ] || [ ! -f "public_key.pem" ]; then
    echo "🔑 Generating CloudFront key pair..."
    openssl genrsa -out private_key.pem 2048
    openssl rsa -pubout -in private_key.pem -out public_key.pem
    echo "✅ Key pair generated"
else
    echo "✅ Key pair already exists"
fi

# Initialize and deploy Terraform
echo "🏗️  Initializing Terraform..."
cd terraform
terraform init

echo "🚀 Deploying infrastructure..."
terraform apply -auto-approve

# Get outputs
echo "📝 Getting Terraform outputs..."
BUCKET_NAME=$(terraform output -raw bucket_name)
DISTRIBUTION_ID=$(terraform output -raw distribution_id)
DOMAIN_NAME=$(terraform output -raw distribution_domain)
KEY_PAIR_ID=$(terraform output -raw key_pair_id)
AWS_REGION=$(terraform output -raw aws_region)

cd ..

# Create .env file
echo "⚙️  Creating .env configuration..."
cat > .env << EOF
# AWS Configuration
AWS_REGION=$AWS_REGION
AWS_PROFILE=default

# S3 Configuration
S3_BUCKET_NAME=$BUCKET_NAME

# CloudFront Configuration
CLOUDFRONT_DISTRIBUTION_ID=$DISTRIBUTION_ID
CLOUDFRONT_DOMAIN_NAME=$DOMAIN_NAME
CLOUDFRONT_KEY_PAIR_ID=$KEY_PAIR_ID

# Security
PRIVATE_KEY_FILE=./private_key.pem
PUBLIC_KEY_FILE=./public_key.pem

# URL Expiration (in days)
URL_EXPIRATION_DAYS=1
EOF

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install -r requirements.txt

# Run tests
echo "🧪 Running tests..."
python3 run_tests.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Configuration:"
echo "   S3 Bucket: $BUCKET_NAME"
echo "   CloudFront Domain: $DOMAIN_NAME"
echo "   Region: $AWS_REGION"
echo ""
echo "🚀 Next steps:"
echo "   1. Upload videos: python3 src/upload_to_s3.py /path/to/videos/"
echo "   2. Generate URLs: python3 src/generate_signed_urls.py"
echo ""
echo "💰 Remember to run 'cd terraform && terraform destroy' when done to avoid costs!"