# Presigned URL Lambda Function

AWS Lambda function written in Go for generating S3 presigned URLs for file uploads and viewing.

## Endpoints

### POST /presign/upload
Generates a presigned URL for uploading files to S3.

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "contentType": "image/jpeg"  // Allowed: image/jpeg, image/png, image/webp
}
```

**Response:**
```json
{
  "uploadUrl": "https://...",  // Presigned PUT URL (expires in 5 minutes)
  "publicUrl": "posts/123/uuid.jpg"  // S3 key for the uploaded file
}
```

### POST /presign/view
Generates a presigned URL for viewing/downloading files from S3.

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "key": "posts/123/uuid.jpg"  // S3 key of the file
}
```

**Response:**
```json
{
  "viewUrl": "https://..."  // Presigned GET URL (expires in 1 hour)
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | AWS region | Required |
| `AWS_S3_BUCKET` | S3 bucket name | `bizbuch-media` |
| `JWT_SECRET` | Secret key for JWT validation | Required |

## Build & Deploy

### Build for Linux (Lambda)
```bash
cd lambda/presigned-url
GOOS=linux GOARCH=amd64 go build -o bootstrap main.go
zip function.zip bootstrap
```

### Build for ARM64 (Graviton2 - recommended for cost savings)
```bash
cd lambda/presigned-url
GOOS=linux GOARCH=arm64 go build -o bootstrap main.go
zip function.zip bootstrap
```

### Deploy via AWS CLI
```bash
aws lambda create-function \
  --function-name bizbuch-presigned-url \
  --runtime provided.al2023 \
  --handler bootstrap \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-s3-role \
  --environment Variables="{AWS_REGION=ap-south-1,AWS_S3_BUCKET=bizbuch-media,JWT_SECRET=your-secret}"
```

### Update existing function
```bash
aws lambda update-function-code \
  --function-name bizbuch-presigned-url \
  --zip-file fileb://function.zip
```

## IAM Role Permissions

The Lambda function needs an IAM role with the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::bizbuch-media/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

## API Gateway Setup

1. Create a new HTTP API in API Gateway
2. Add routes:
   - `POST /presign/upload`
   - `POST /presign/view`
   - `OPTIONS /presign/upload` (for CORS preflight)
   - `OPTIONS /presign/view` (for CORS preflight)
3. Integrate all routes with the Lambda function
4. Deploy the API

## Local Testing

```bash
# Install dependencies
go mod tidy

# Run locally (for testing outside Lambda)
go run main.go
```

## Notes

- Upload URLs expire in 5 minutes
- View URLs expire in 1 hour
- Only image types (jpeg, png, webp) are allowed for uploads
- Files are stored under `posts/{user_id}/{uuid}.jpg` in S3
