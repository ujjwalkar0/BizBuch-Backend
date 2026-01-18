# AWS Lambda Deployment Guide: Presigned URL Function (Go)

This guide provides detailed instructions for deploying the Go-based presigned URL Lambda function to AWS.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Code Structure](#code-structure)
4. [Building the Lambda Function](#building-the-lambda-function)
5. [IAM Role Setup](#iam-role-setup)
6. [Deploying to AWS Lambda](#deploying-to-aws-lambda)
7. [API Gateway Configuration](#api-gateway-configuration)
8. [Environment Variables](#environment-variables)
9. [Testing](#testing)
10. [Updating the Function](#updating-the-function)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The presigned URL Lambda function is written in Go and provides two endpoints:
- **`POST /presign/upload`**: Generates presigned URLs for uploading files to S3
- **`POST /presign/view`**: Generates presigned URLs for viewing/downloading files from S3

### Key Features
- JWT authentication (compatible with Django SimpleJWT)
- CORS support for specified origins
- Content type validation (only allows `image/jpeg`, `image/png`, `image/webp`)
- Upload URLs expire in 5 minutes
- View URLs expire in 1 hour
- Files stored under `posts/{user_id}/{uuid}.jpg` path structure

---

## Prerequisites

### Required Tools
```bash
# Go (version 1.21 or later)
go version

# AWS CLI (configured with appropriate credentials)
aws --version
aws configure list

# Optional: AWS SAM CLI (for local testing)
sam --version

# Zip utility (usually pre-installed on Linux/macOS)
zip --version
```

### AWS Permissions
Ensure your AWS CLI is configured with an IAM user/role that has permissions to:
- Create/update Lambda functions
- Create/update IAM roles
- Create/update API Gateway
- Access S3 buckets

---

## Code Structure

```
lambda/pre-signed-url/
├── main.go           # Main Lambda handler code
├── local.go          # Local development server (not used in Lambda)
├── go.mod            # Go module dependencies
├── go.sum            # Dependency checksums
├── template.yaml     # AWS SAM template
├── env.json          # Local environment variables for SAM
├── bootstrap         # Compiled binary (generated during build)
├── function.zip      # Deployment package (generated during build)
└── README.md         # Basic documentation
```

### Main Components in `main.go`

| Component | Description |
|-----------|-------------|
| `init()` | Initializes AWS SDK, S3 client, and loads environment variables |
| `handler()` | Main Lambda entry point, routes requests based on path |
| `handlePresignUpload()` | Generates presigned PUT URLs for file uploads |
| `handlePresignView()` | Generates presigned GET URLs for file viewing |
| `validateJWTAndGetUserID()` | Validates JWT tokens and extracts user ID |
| `getCORSHeaders()` | Returns CORS headers based on allowed origins |

---

## Building the Lambda Function

### Step 1: Navigate to the Lambda Directory

```bash
cd /home/ujjwal/Desktop/BizBuch/BizBuch-Backend/lambda/pre-signed-url
```

### Step 2: Download Dependencies

```bash
go mod tidy
```

### Step 3: Build the Binary

#### For x86_64 Architecture (Standard)
```bash
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -tags lambda.norpc -o bootstrap main.go
```

#### For ARM64 Architecture (Graviton2 - Recommended for Cost Savings)
```bash
GOOS=linux GOARCH=arm64 CGO_ENABLED=0 go build -tags lambda.norpc -o bootstrap main.go
```

> **Note**: The `CGO_ENABLED=0` flag ensures the binary is statically linked, which is required for Lambda.

### Step 4: Create Deployment Package

```bash
zip function.zip bootstrap
```

### One-Liner Build Command (x86_64)
```bash
cd /home/ujjwal/Desktop/BizBuch/BizBuch-Backend/lambda/pre-signed-url && \
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -tags lambda.norpc -o bootstrap main.go && \
zip function.zip bootstrap
```

### One-Liner Build Command (ARM64)
```bash
cd /home/ujjwal/Desktop/BizBuch/BizBuch-Backend/lambda/pre-signed-url && \
GOOS=linux GOARCH=arm64 CGO_ENABLED=0 go build -tags lambda.norpc -o bootstrap main.go && \
zip function.zip bootstrap
```

---

## IAM Role Setup

### What is IAM and Why Do We Need It?

**IAM (Identity and Access Management)** is AWS's security system that controls who can do what in your AWS account. Think of it like a security guard system:

- **Users**: People who log into AWS (like you)
- **Roles**: Temporary identities that AWS services (like Lambda) can "wear" to get permissions
- **Policies**: Documents that list what actions are allowed or denied

**Why does Lambda need a role?**

When your Lambda function runs, it needs to:
1. Read and write files to S3 (your storage bucket)
2. Write logs to CloudWatch (AWS's logging service)

Without proper permissions, Lambda would be blocked from doing these things. We create a "role" that Lambda can assume, and attach "policies" that grant the necessary permissions.

---

### Method 1: Using AWS Console (Recommended for Beginners)

This method uses the visual AWS website interface - no command line needed!

#### Step 1: Log into AWS Console

1. Open your web browser and go to: https://console.aws.amazon.com/
2. Sign in with your AWS account credentials
3. Make sure you're in the correct region (e.g., `ap-south-1` for Mumbai, India)
   - You can see/change the region in the top-right corner of the AWS Console

#### Step 2: Navigate to IAM

1. In the search bar at the top, type **"IAM"**
2. Click on **"IAM"** (Identity and Access Management) from the search results
3. You'll see the IAM Dashboard

---

### PART A: Create the Custom Policy FIRST

We need to create the S3 access policy **before** creating the role.

#### Step 3: Go to Policies Page

1. In the left sidebar of IAM Dashboard, click on **"Policies"**
2. Click the orange **"Create policy"** button in the top-right

#### Step 4: Create the S3 Access Policy

1. On the "Specify permissions" page, you'll see two tabs: **"Visual"** and **"JSON"**
2. Click on the **"JSON"** tab

3. Delete all the existing content in the editor and paste this policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3UploadDownloadAccess",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::bizbuch-media/*"
        }
    ]
}
```

**Understanding this policy:**
| Field | Meaning |
|-------|---------|
| `Version` | Policy language version (always use "2012-10-17") |
| `Sid` | A friendly name/identifier for this permission block |
| `Effect` | "Allow" means grant permission (could also be "Deny") |
| `Action` | What operations are allowed: `s3:PutObject` (upload), `s3:GetObject` (download) |
| `Resource` | Which S3 bucket/files this applies to. The `/*` means all files in the bucket |

> ⚠️ **Important**: Replace `bizbuch-media` with your actual S3 bucket name!

4. Click **"Next"** button

#### Step 5: Name and Create the Policy

1. **Policy name**: Enter `bizbuch-lambda-s3-access-policy`

2. **Description** (optional): Enter `Allows Lambda to upload and download files from the bizbuch-media S3 bucket`

3. Scroll down and click **"Create policy"** button

4. ✅ You'll see a green success banner: "Policy bizbuch-lambda-s3-access-policy created"

---

### PART B: Create the IAM Role

Now that we have the policy, let's create the role and attach it.

#### Step 6: Go to Roles Page

1. In the left sidebar, click on **"Roles"**
2. Click the blue **"Create role"** button

#### Step 7: Select Trusted Entity Type

On the "Select trusted entity" page:

1. **Trusted entity type**: Select **"AWS service"**
   - This means we're creating a role for an AWS service (Lambda) to use

2. **Use case**: 
   - In the "Service or use case" dropdown, select **"Lambda"**
   - This tells AWS that Lambda functions will use this role

3. Click **"Next"** button

#### Step 8: Add Permissions (Attach Policies)

On the "Add permissions" page:

1. In the search box under "Permissions policies", type `bizbuch-lambda-s3`

2. Check the checkbox ☑️ next to **`bizbuch-lambda-s3-access-policy`** (the policy you created in Step 5)

3. Clear the search box and type `AWSLambdaBasicExecutionRole`
   - This is an AWS-managed policy that allows Lambda to write logs to CloudWatch

4. Check the checkbox ☑️ next to **`AWSLambdaBasicExecutionRole`**

5. You should now have **2 policies selected** (shown at the bottom or in a "Selected" section):
   - ✅ `bizbuch-lambda-s3-access-policy`
   - ✅ `AWSLambdaBasicExecutionRole`

6. Click **"Next"** button

#### Step 7: Name and Create the Role

1. **Role name**: Enter `bizbuch-presigned-url-lambda-role`

2. **Description**: Enter `Role for BizBuch presigned URL Lambda function to access S3 and CloudWatch`

3. **Step 1: Select trusted entities** - Should show "AWS service: lambda.amazonaws.com" (already configured)

4. **Step 2: Add permissions** - Should show the 2 policies you selected

5. Scroll down and click **"Create role"** button

6. ✅ You'll see a green success message: "Role bizbuch-presigned-url-lambda-role created"

#### Step 8: Get the Role ARN (You'll Need This Later!)

1. Click on the role name **`bizbuch-presigned-url-lambda-role`** to view its details

2. At the top, you'll see the **ARN** (Amazon Resource Name). It looks like:
   ```
   arn:aws:iam::123456789012:role/bizbuch-presigned-url-lambda-role
   ```

3. **Copy this ARN** and save it somewhere - you'll need it when deploying the Lambda function!

> 💡 **Tip**: The `123456789012` part is your AWS Account ID. Your ARN will have your actual account ID.

---

### Method 2: Using AWS CLI (For Advanced Users)

If you prefer using the command line, follow these steps:

#### Prerequisites

Make sure AWS CLI is installed and configured:

```bash
# Check if AWS CLI is installed
aws --version

# Configure AWS CLI (if not already done)
aws configure
# You'll be prompted for:
# - AWS Access Key ID: (your access key)
# - AWS Secret Access Key: (your secret key)
# - Default region name: ap-south-1
# - Default output format: json
```

#### Step 1: Create the Trust Policy File

First, navigate to your lambda directory:

```bash
cd /home/ujjwal/Desktop/BizBuch/BizBuch-Backend/lambda/pre-signed-url
```

Create a file named `trust-policy.json`:

```bash
cat > trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
```

**What this does**: This "trust policy" tells AWS that the Lambda service is allowed to "assume" (use) this role.

#### Step 2: Create the IAM Role

```bash
aws iam create-role \
    --role-name bizbuch-presigned-url-lambda-role \
    --assume-role-policy-document file://trust-policy.json \
    --description "Role for BizBuch presigned URL Lambda function"
```

**Expected output**:
```json
{
    "Role": {
        "Path": "/",
        "RoleName": "bizbuch-presigned-url-lambda-role",
        "RoleId": "AROAXXXXXXXXXXXXXXXXX",
        "Arn": "arn:aws:iam::123456789012:role/bizbuch-presigned-url-lambda-role",
        "CreateDate": "2026-01-18T10:00:00+00:00",
        ...
    }
}
```

> 📝 **Save the ARN** from the output! You'll need it later.

#### Step 3: Create the S3 Access Policy File

Create a file named `lambda-s3-policy.json`:

```bash
cat > lambda-s3-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3UploadDownloadAccess",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::bizbuch-media/*"
        },
        {
            "Sid": "CloudWatchLogsAccess",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
EOF
```

> ⚠️ **Important**: Replace `bizbuch-media` with your actual S3 bucket name!

#### Step 4: Create the Policy in AWS

```bash
aws iam create-policy \
    --policy-name bizbuch-presigned-url-lambda-policy \
    --policy-document file://lambda-s3-policy.json \
    --description "Policy for BizBuch Lambda to access S3 and CloudWatch"
```

**Expected output**:
```json
{
    "Policy": {
        "PolicyName": "bizbuch-presigned-url-lambda-policy",
        "PolicyId": "ANPAXXXXXXXXXXXXXXXXX",
        "Arn": "arn:aws:iam::123456789012:policy/bizbuch-presigned-url-lambda-policy",
        ...
    }
}
```

> 📝 **Save the Policy ARN** from the output!

#### Step 5: Attach the Policy to the Role

Now connect the policy to the role:

```bash
# First, get your AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Your AWS Account ID is: $AWS_ACCOUNT_ID"

# Attach the policy to the role
aws iam attach-role-policy \
    --role-name bizbuch-presigned-url-lambda-role \
    --policy-arn "arn:aws:iam::${AWS_ACCOUNT_ID}:policy/bizbuch-presigned-url-lambda-policy"
```

> 💡 **Note**: This command doesn't produce output on success. No output = success!

#### Step 6: Verify the Setup

Check that everything is configured correctly:

```bash
# List policies attached to the role
aws iam list-attached-role-policies \
    --role-name bizbuch-presigned-url-lambda-role
```

**Expected output**:
```json
{
    "AttachedPolicies": [
        {
            "PolicyName": "bizbuch-presigned-url-lambda-policy",
            "PolicyArn": "arn:aws:iam::123456789012:policy/bizbuch-presigned-url-lambda-policy"
        }
    ]
}
```

#### Step 7: Get the Role ARN (Save This!)

```bash
# Get and display the Role ARN
aws iam get-role \
    --role-name bizbuch-presigned-url-lambda-role \
    --query 'Role.Arn' \
    --output text
```

**Example output**:
```
arn:aws:iam::123456789012:role/bizbuch-presigned-url-lambda-role
```

> 🔴 **IMPORTANT**: Copy this ARN and save it! You will need it in the next section when deploying the Lambda function.

---

### Quick Reference: What We Created

| Resource | Name | Purpose |
|----------|------|---------|
| **IAM Role** | `bizbuch-presigned-url-lambda-role` | The identity that Lambda assumes when running |
| **IAM Policy** | `bizbuch-presigned-url-lambda-policy` | The permissions document attached to the role |

### Permissions Summary

| Permission | What It Allows |
|------------|----------------|
| `s3:PutObject` | Upload files to S3 bucket |
| `s3:GetObject` | Download/read files from S3 bucket |
| `logs:CreateLogGroup` | Create log groups in CloudWatch |
| `logs:CreateLogStream` | Create log streams in CloudWatch |
| `logs:PutLogEvents` | Write log entries to CloudWatch |

---

### Troubleshooting IAM Setup

#### Error: "User is not authorized to perform: iam:CreateRole"
**Cause**: Your AWS user doesn't have permission to create IAM roles.
**Solution**: 
- Contact your AWS administrator to grant you IAM permissions
- Or use an AWS account with admin access

#### Error: "Role already exists"
**Cause**: A role with that name already exists.
**Solution**: 
- Use a different role name, OR
- Delete the existing role first:
  ```bash
  # First detach all policies
  aws iam detach-role-policy \
      --role-name bizbuch-presigned-url-lambda-role \
      --policy-arn "arn:aws:iam::ACCOUNT_ID:policy/bizbuch-presigned-url-lambda-policy"
  
  # Then delete the role
  aws iam delete-role --role-name bizbuch-presigned-url-lambda-role
  ```

#### Error: "Policy already exists"
**Cause**: A policy with that name already exists.
**Solution**:
- Use a different policy name, OR
- Delete the existing policy first:
  ```bash
  aws iam delete-policy \
      --policy-arn "arn:aws:iam::ACCOUNT_ID:policy/bizbuch-presigned-url-lambda-policy"
  ```

#### Can't Find Your AWS Account ID?
Run this command:
```bash
aws sts get-caller-identity --query Account --output text
```

Or find it in the AWS Console:
1. Click on your username in the top-right corner
2. Your Account ID is shown in the dropdown menu

---

## Deploying to AWS Lambda

### Option 1: Using AWS CLI (Recommended)

#### First-Time Deployment

```bash
# Replace ACCOUNT_ID with your AWS account ID
# Replace ap-south-1 with your desired region

aws lambda create-function \
  --function-name bizbuch-presigned-url \
  --runtime provided.al2023 \
  --handler bootstrap \
  --architectures x86_64 \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::ACCOUNT_ID:role/bizbuch-presigned-url-lambda-role \
  --timeout 10 \
  --memory-size 128 \
  --environment "Variables={AWS_REGION=ap-south-1,AWS_S3_BUCKET=bizbuch-media,JWT_SECRET=your-jwt-secret-here}" \
  --region ap-south-1
```

#### For ARM64 Architecture (Graviton2)
```bash
aws lambda create-function \
  --function-name bizbuch-presigned-url \
  --runtime provided.al2023 \
  --handler bootstrap \
  --architectures arm64 \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::ACCOUNT_ID:role/bizbuch-presigned-url-lambda-role \
  --timeout 10 \
  --memory-size 128 \
  --environment "Variables={AWS_REGION=ap-south-1,AWS_S3_BUCKET=bizbuch-media,JWT_SECRET=your-jwt-secret-here}" \
  --region ap-south-1
```

### Option 2: Using AWS SAM

```bash
cd /home/ujjwal/Desktop/BizBuch/BizBuch-Backend/lambda/pre-signed-url

# Build
sam build

# Deploy (guided mode for first-time setup)
sam deploy --guided

# Or deploy with specific parameters
sam deploy \
  --stack-name bizbuch-presigned-url-stack \
  --capabilities CAPABILITY_IAM \
  --region ap-south-1
```

### Option 3: Using AWS Console

1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda)
2. Click **Create function**
3. Choose **Author from scratch**
4. Configure:
   - Function name: `bizbuch-presigned-url`
   - Runtime: `Amazon Linux 2023`
   - Architecture: `x86_64` (or `arm64` for Graviton2)
   - Execution role: Select the role created earlier
5. Click **Create function**
6. In the **Code** tab, click **Upload from** → **.zip file**
7. Upload `function.zip`
8. In **Runtime settings**, set Handler to `bootstrap`
9. Go to **Configuration** → **Environment variables** and add the required variables

---

## API Gateway Configuration

### Option 1: HTTP API (Recommended for Simplicity)

```bash
# Create HTTP API
aws apigatewayv2 create-api \
  --name bizbuch-presigned-url-api \
  --protocol-type HTTP \
  --region ap-south-1

# Note the API ID from the output, then create integration
aws apigatewayv2 create-integration \
  --api-id YOUR_API_ID \
  --integration-type AWS_PROXY \
  --integration-uri arn:aws:lambda:ap-south-1:ACCOUNT_ID:function:bizbuch-presigned-url \
  --payload-format-version 2.0 \
  --region ap-south-1

# Create routes
aws apigatewayv2 create-route \
  --api-id YOUR_API_ID \
  --route-key "POST /presign/upload" \
  --target integrations/YOUR_INTEGRATION_ID \
  --region ap-south-1

aws apigatewayv2 create-route \
  --api-id YOUR_API_ID \
  --route-key "OPTIONS /presign/upload" \
  --target integrations/YOUR_INTEGRATION_ID \
  --region ap-south-1

aws apigatewayv2 create-route \
  --api-id YOUR_API_ID \
  --route-key "POST /presign/view" \
  --target integrations/YOUR_INTEGRATION_ID \
  --region ap-south-1

aws apigatewayv2 create-route \
  --api-id YOUR_API_ID \
  --route-key "OPTIONS /presign/view" \
  --target integrations/YOUR_INTEGRATION_ID \
  --region ap-south-1

# Create default stage with auto-deploy
aws apigatewayv2 create-stage \
  --api-id YOUR_API_ID \
  --stage-name '$default' \
  --auto-deploy \
  --region ap-south-1
```

### Option 2: Using AWS Console

1. Go to [API Gateway Console](https://console.aws.amazon.com/apigateway)
2. Click **Create API** → **HTTP API** → **Build**
3. Add integration:
   - Integration type: Lambda
   - Lambda function: `bizbuch-presigned-url`
4. Configure routes:
   - `POST /presign/upload`
   - `POST /presign/view`
   - `OPTIONS /presign/upload` (for CORS)
   - `OPTIONS /presign/view` (for CORS)
5. Configure stage: `$default` with auto-deploy
6. Click **Create**

### Grant API Gateway Permission to Invoke Lambda

```bash
aws lambda add-permission \
  --function-name bizbuch-presigned-url \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:ap-south-1:ACCOUNT_ID:YOUR_API_ID/*" \
  --region ap-south-1
```

---

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AWS_REGION` | AWS region for S3 operations | Yes | - |
| `AWS_S3_BUCKET` | S3 bucket name for file storage | No | `bizbuch-media` |
| `JWT_SECRET` | Secret key for JWT validation (must match Django's `SECRET_KEY` or SimpleJWT signing key) | Yes | - |

### Updating Environment Variables

```bash
aws lambda update-function-configuration \
  --function-name bizbuch-presigned-url \
  --environment "Variables={AWS_REGION=ap-south-1,AWS_S3_BUCKET=bizbuch-media,JWT_SECRET=your-new-secret}" \
  --region ap-south-1
```

---

## Testing

### Test Upload Endpoint

```bash
# Get a JWT token from your Django backend first
TOKEN="your-jwt-token-here"
API_URL="https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com"

curl -X POST "${API_URL}/presign/upload" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"contentType": "image/jpeg"}'
```

Expected Response:
```json
{
  "uploadUrl": "https://bizbuch-media.s3.ap-south-1.amazonaws.com/posts/123/uuid.jpg?...",
  "publicUrl": "posts/123/uuid.jpg"
}
```

### Test View Endpoint

```bash
curl -X POST "${API_URL}/presign/view" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"key": "posts/123/uuid.jpg"}'
```

Expected Response:
```json
{
  "viewUrl": "https://bizbuch-media.s3.ap-south-1.amazonaws.com/posts/123/uuid.jpg?..."
}
```

### Local Testing with SAM

```bash
cd /home/ujjwal/Desktop/BizBuch/BizBuch-Backend/lambda/pre-signed-url

# Start local API
sam local start-api --env-vars env.json

# Test locally
curl -X POST "http://127.0.0.1:3000/presign/upload" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"contentType": "image/jpeg"}'
```

---

## Updating the Function

### Quick Update (Code Only)

```bash
cd /home/ujjwal/Desktop/BizBuch/BizBuch-Backend/lambda/pre-signed-url

# Rebuild
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -tags lambda.norpc -o bootstrap main.go
zip function.zip bootstrap

# Update
aws lambda update-function-code \
  --function-name bizbuch-presigned-url \
  --zip-file fileb://function.zip \
  --region ap-south-1
```

### Full Deployment Script

Create a file `deploy.sh` in the `lambda/pre-signed-url` directory:

```bash
#!/bin/bash
set -e

FUNCTION_NAME="bizbuch-presigned-url"
REGION="ap-south-1"
ARCH="amd64"  # Change to "arm64" for Graviton2

echo "Building for linux/${ARCH}..."
GOOS=linux GOARCH=${ARCH} CGO_ENABLED=0 go build -tags lambda.norpc -o bootstrap main.go

echo "Creating deployment package..."
zip -j function.zip bootstrap

echo "Updating Lambda function..."
aws lambda update-function-code \
  --function-name ${FUNCTION_NAME} \
  --zip-file fileb://function.zip \
  --region ${REGION}

echo "Waiting for update to complete..."
aws lambda wait function-updated \
  --function-name ${FUNCTION_NAME} \
  --region ${REGION}

echo "Deployment complete!"
aws lambda get-function \
  --function-name ${FUNCTION_NAME} \
  --region ${REGION} \
  --query 'Configuration.{LastModified:LastModified,CodeSize:CodeSize,Runtime:Runtime}' \
  --output table
```

Make it executable:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## Troubleshooting

### Common Issues

#### 1. "Permission denied" when executing bootstrap
```bash
# Ensure the binary has execute permissions before zipping
chmod +x bootstrap
zip function.zip bootstrap
```

#### 2. "exec format error"
- Ensure you're building for the correct architecture (`GOARCH=amd64` or `GOARCH=arm64`)
- Ensure the Lambda architecture setting matches your build

#### 3. JWT Validation Fails
- Verify `JWT_SECRET` matches your Django `SECRET_KEY` or SimpleJWT signing key
- Check that the token is an access token (not refresh token)
- Ensure the token hasn't expired

#### 4. S3 Access Denied
- Verify the Lambda execution role has the correct S3 permissions
- Check that the bucket name in `AWS_S3_BUCKET` is correct
- Verify the bucket exists in the specified region

#### 5. CORS Errors
- Check that the request origin is in the `allowedOrigins` list in `main.go`
- Verify OPTIONS routes are configured in API Gateway
- Update the code to add your production domain to `allowedOrigins`:

```go
allowedOrigins = []string{
    "http://localhost:3000",
    "http://localhost:8080",
    "https://yourdomain.com",
}
```

### Viewing Logs

```bash
# View recent logs
aws logs tail /aws/lambda/bizbuch-presigned-url --region ap-south-1 --follow

# View logs for a specific time range
aws logs filter-log-events \
  --log-group-name /aws/lambda/bizbuch-presigned-url \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --region ap-south-1
```

### Checking Function Configuration

```bash
aws lambda get-function-configuration \
  --function-name bizbuch-presigned-url \
  --region ap-south-1
```

---

## Security Considerations

1. **JWT Secret**: Never commit the actual JWT secret to version control. Use AWS Secrets Manager or Parameter Store for production.

2. **CORS Origins**: Only include trusted domains in `allowedOrigins`. Remove localhost domains in production.

3. **Content Type Validation**: The function only allows specific image types. Update `isAllowedContentType()` if you need to support additional file types.

4. **IAM Least Privilege**: The Lambda role only has access to the specific S3 bucket and CloudWatch Logs.

---

## Cost Optimization Tips

1. **Use ARM64 (Graviton2)**: 20% cheaper than x86_64 with better performance
2. **Memory Setting**: 128MB is sufficient for this function
3. **Timeout**: 10 seconds is adequate; reduce if possible based on actual execution times
4. **Provisioned Concurrency**: Not needed unless you have strict latency requirements

---

## Related Documentation

- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [AWS Lambda Go Handler](https://docs.aws.amazon.com/lambda/latest/dg/golang-handler.html)
- [API Gateway HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)
- [S3 Presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
