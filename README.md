# S3 CloudFront Video Streamer

A quick infrastructure setup for uploading video files from your home server and distributing them globally via AWS CloudFront for fast worldwide downloads.

## Overview

This project creates:
- **S3 bucket** for video storage
- **CloudFront distribution** with signed URLs for secure access
- **Python scripts** for uploading videos and generating download links

## Prerequisites

- AWS CLI configured with appropriate permissions
- Terraform installed
- Python 3.8+
- OpenSSL (for key generation)

## Quick Start

### Automated Setup

```bash
# Clone and setup everything
git clone <repository-url>
cd s3-cloudfront-streamer
./scripts/setup.sh
```

### Manual Setup

#### 1. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

#### 2. Generate CloudFront Key Pair

```bash
openssl genrsa -out private_key.pem 2048
openssl rsa -pubout -in private_key.pem -out public_key.pem
```

#### 3. Deploy Infrastructure

```bash
cd terraform
terraform init
terraform apply
```

#### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with terraform outputs
```

## Usage

### Upload Videos
```bash
python src/upload_to_s3.py /path/to/videos/
```

### Generate Download URLs
```bash
python src/generate_signed_urls.py
```

### Download Videos
```bash
python src/download_videos.py signed_urls.txt
```

## Development

### Using Make (Recommended)

```bash
# Setup virtual environment and install dependencies
make setup

# Run tests
make test

# Clean up
make clean
```

### Manual Development Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python run_tests.py
```

## Project Structure

```
├── src/                    # Python source code
│   ├── upload_to_s3.py     # Video upload script
│   ├── generate_signed_urls.py  # URL generation script
│   └── download_videos.py  # Video download script
├── terraform/              # Infrastructure as code
│   └── main.tf            # Terraform configuration
├── scripts/                # Setup and utility scripts
│   └── setup.sh           # Automated setup script
├── tests/                  # Unit tests
├── .github/workflows/      # CI/CD pipelines
├── .env.example           # Environment configuration template
├── Makefile              # Development commands
└── requirements.txt      # Python dependencies
```

## Configuration

### Terraform Variables (terraform.tfvars)
```hcl
aws_region = "us-east-1"
bucket_prefix = "my-video-streaming"
public_key_file = "../public_key.pem"
```

### Environment Variables (.env)
| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | AWS region | `ap-northeast-1` |
| `S3_BUCKET_NAME` | S3 bucket name | From Terraform output |
| `CLOUDFRONT_DISTRIBUTION_ID` | CloudFront distribution ID | From Terraform output |
| `CLOUDFRONT_DOMAIN_NAME` | CloudFront domain | From Terraform output |
| `CLOUDFRONT_KEY_PAIR_ID` | CloudFront key pair ID | From Terraform output |
| `PRIVATE_KEY_FILE` | Path to private key | `./private_key.pem` |
| `URL_EXPIRATION_DAYS` | URL validity period | `1` |

## Testing

### Run All Tests
```bash
make test
# or
python run_tests.py
```

### Test Coverage
- Filename sanitization
- Configuration validation
- Error handling
- Terraform syntax validation

## Cost Considerations

⚠️ **Important**: This infrastructure incurs AWS costs:

- **S3 storage**: ~$0.023/GB/month
- **CloudFront data transfer**: ~$0.085/GB (varies by region)
- **CloudFront requests**: ~$0.0075/10,000 requests

Use the [AWS Pricing Calculator](https://calculator.aws) for detailed estimates.

## Security Features

- Private S3 bucket (no public access)
- CloudFront Origin Access Control (OAC)
- Signed URLs with expiration
- No hardcoded credentials

## Cleanup

```bash
cd terraform
terraform destroy
```

## Troubleshooting

### Virtual Environment Issues
```bash
# If venv activation fails
python3 -m venv --clear venv
source venv/bin/activate
pip install -r requirements.txt
```

### Common Issues

1. **"Access Denied" errors**: Check AWS credentials and permissions
2. **"Bucket not found"**: Verify bucket name in `.env` matches Terraform output
3. **"Invalid signature" for URLs**: Ensure private key file path is correct
4. **Upload failures**: Check file permissions and network connectivity

### Required AWS Permissions

Your AWS user/role needs:
- `s3:CreateBucket`, `s3:PutObject`, `s3:GetObject`, `s3:ListBucket`
- `cloudfront:CreateDistribution`, `cloudfront:CreatePublicKey`, `cloudfront:CreateKeyGroup`
- `iam:CreateRole`, `iam:AttachRolePolicy` (for S3 bucket policy)

## Legal Disclaimer

Users are responsible for:
- Ensuring uploaded content complies with local laws
- Following AWS Terms of Service
- Monitoring and managing AWS costs
- Securing their AWS credentials and private keys

## Contributing

1. Fork the repository
2. Create a feature branch
3. Setup development environment: `make setup`
4. Run tests: `make test`
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.