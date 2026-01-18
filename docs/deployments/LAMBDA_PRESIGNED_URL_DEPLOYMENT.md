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

### What is AWS Lambda?

**AWS Lambda** is a "serverless" computing service. Instead of managing servers yourself, you just upload your code and AWS runs it for you. Key benefits:

- **No servers to manage**: AWS handles all the infrastructure
- **Pay only for what you use**: You're charged only when your code runs
- **Automatic scaling**: Lambda handles thousands of requests automatically
- **High availability**: Your code runs across multiple data centers

### Before You Begin - Checklist

Make sure you have completed these steps:

- [ ] ✅ Built the `bootstrap` binary (from "Building the Lambda Function" section)
- [ ] ✅ Created `function.zip` containing the bootstrap binary
- [ ] ✅ Created the IAM role `bizbuch-presigned-url-lambda-role` (from "IAM Role Setup" section)
- [ ] ✅ Have your AWS Account ID ready (12-digit number like `123456789012`)
- [ ] ✅ Know your JWT secret from Django settings

### Understanding the Deployment Options

| Option | Best For | Difficulty |
|--------|----------|------------|
| **AWS Console** | Beginners, visual learners | ⭐ Easy |
| **AWS CLI** | Automation, scripting | ⭐⭐ Medium |
| **AWS SAM** | Infrastructure as Code, CI/CD | ⭐⭐⭐ Advanced |

---

### Option 1: Using AWS Console (Recommended for Beginners)

This method uses the visual AWS website interface.

#### Step 1: Open AWS Lambda Console

1. Open your browser and go to: https://console.aws.amazon.com/lambda
2. Sign in to your AWS account
3. Make sure you're in the correct region (check top-right corner)
   - For India: Select **Asia Pacific (Mumbai) ap-south-1**
   - Click on the region name to change it if needed

#### Step 2: Create a New Function

1. Click the orange **"Create function"** button

2. On the "Create function" page, select **"Author from scratch"** (should be selected by default)

3. Fill in the **Basic information**:

   | Field | Value | Explanation |
   |-------|-------|-------------|
   | **Function name** | `bizbuch-presigned-url` | A unique name for your function |
   | **Runtime** | Select **"Provide your own bootstrap on Amazon Linux 2023"** | For Go compiled binaries |
   | **Architecture** | Select **x86_64** | Or arm64 if you built for ARM |

4. Expand **"Change default execution role"** section:
   
   - Select **"Use an existing role"**
   - In the dropdown **"Existing role"**, search for and select: `bizbuch-presigned-url-lambda-role`
   
   > ⚠️ If you don't see the role, go back and complete the "IAM Role Setup" section first!

5. Click **"Create function"** button

6. ✅ Wait for the success message: "Successfully created the function bizbuch-presigned-url"

#### Step 3: Upload Your Code

1. You should now be on the function's detail page

2. Scroll down to the **"Code source"** section

3. Click **"Upload from"** dropdown button (on the right side)

4. Select **".zip file"**

5. Click **"Upload"** and browse to your `function.zip` file:
   ```
   /home/ujjwal/Desktop/BizBuch/BizBuch-Backend/lambda/pre-signed-url/function.zip
   ```

6. Click **"Save"** button

7. ✅ Wait for the upload to complete. You'll see "Successfully updated the function bizbuch-presigned-url"

#### Step 4: Configure Runtime Settings

1. In the **"Code source"** section, scroll down to find **"Runtime settings"**

2. Click **"Edit"** button

3. Set the following:
   
   | Field | Value |
   |-------|-------|
   | **Runtime** | Amazon Linux 2023 |
   | **Handler** | `bootstrap` |
   | **Architecture** | x86_64 (or arm64 if you built for ARM) |

4. Click **"Save"**

#### Step 5: Configure Environment Variables

Environment variables are settings your Lambda function reads at runtime.

1. Click on the **"Configuration"** tab (near the top of the page)

2. In the left sidebar, click **"Environment variables"**

3. Click **"Edit"** button

4. Click **"Add environment variable"** and add these three variables:

   **Variable 1:**
   | Key | Value |
   |-----|-------|
   | `AWS_REGION` | `ap-south-1` |

   **Variable 2:**
   | Key | Value |
   |-----|-------|
   | `AWS_S3_BUCKET` | `bizbuch-media` |
   
   > Replace `bizbuch-media` with your actual S3 bucket name

   **Variable 3:**
   | Key | Value |
   |-----|-------|
   | `JWT_SECRET` | `your-django-secret-key-here` |
   
   > ⚠️ **Important**: This must match your Django `SECRET_KEY` or SimpleJWT signing key exactly!

5. Click **"Save"**

#### Step 6: Configure General Settings (Timeout & Memory)

1. Still in the **"Configuration"** tab, click **"General configuration"** in the left sidebar

2. Click **"Edit"**

3. Set the following:

   | Setting | Value | Explanation |
   |---------|-------|-------------|
   | **Memory** | `128` MB | Sufficient for this function |
   | **Timeout** | `10` sec | Max time for function to complete |

4. Click **"Save"**

#### Step 7: Test Your Lambda Function (Optional but Recommended)

Let's verify the function is working:

##### How to Get a Test JWT Token

The Lambda function validates JWT tokens issued by your Django backend. You need to get a valid token from your Django application first.

**Method 1: Using Django Admin or API (Recommended)**

If your Django server is running locally or on a server:

```bash
# Make sure your Django server is running
# Then get a token by logging in via the API

curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com", "password": "your-password"}'
```

The response will include an `access` token:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM3MjAwMDAwLCJ1c2VyX2lkIjoxfQ.xxxxx",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Copy the `access` token value - this is your JWT token.

**Method 2: Using Django Shell**

```bash
# Activate your virtual environment
cd /home/ujjwal/Desktop/BizBuch/BizBuch-Backend
source venv/bin/activate

# Open Django shell
python manage.py shell
```

Then in the Python shell:
```python
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User

# Get an existing user (replace with a valid user ID or email)
user = User.objects.get(id=1)  # or User.objects.get(email='your@email.com')

# Generate tokens
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)

print("Access Token:", access_token)
```

Copy the printed access token.

**Method 3: Using Browser Developer Tools (This method will not be applicable now until our website will be ready)**

If you have a frontend application that's already logged in:
1. Open your web app and log in
2. Open Browser Developer Tools (F12)
3. Go to **Application** → **Local Storage** or **Session Storage**
4. Look for a key like `accessToken` or `token`
5. Copy the token value

---

##### Now Test the Lambda Function

1. Click on the **"Test"** tab (near the top)

2. Click **"Create new event"**

3. Configure the test event:
   - **Event name**: `TestUploadEndpoint`
   - **Template**: Keep as "hello-world"
   - Replace the JSON with (paste your actual token):

   ```json
   {
     "httpMethod": "POST",
     "path": "/presign/upload",
     "headers": {
       "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.YOUR_ACTUAL_TOKEN_HERE",
       "Content-Type": "application/json"
     },
     "body": "{\"contentType\": \"image/jpeg\"}"
   }
   ```

   > ⚠️ Replace `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.YOUR_ACTUAL_TOKEN_HERE` with the actual JWT token you obtained!

4. Click **"Save"**

5. Click **"Test"** button

6. Check the results:
   - **Green banner with 200 status** = ✅ Success! You'll see `uploadUrl` and `publicUrl` in the response
   - **Green banner with 401 status** = Token validation failed (check JWT_SECRET matches Django)
   - **Red banner** = Function error (check the error message)

#### Step 8: Note the Function ARN

1. At the top of the Lambda function page, you'll see **Function ARN**:
   ```
   arn:aws:lambda:ap-south-1:123456789012:function:bizbuch-presigned-url
   ```

2. **Copy and save this ARN** - you'll need it when setting up API Gateway!

---

### Option 2: Using AWS CLI (For Automation)

This method uses command-line tools. Good for scripting and automation.

#### Prerequisites

```bash
# Verify AWS CLI is installed and configured
aws --version
aws configure list

# Make sure you're in the lambda directory
cd /home/ujjwal/Desktop/BizBuch/BizBuch-Backend/lambda/pre-signed-url

# Verify function.zip exists
ls -la function.zip
```

#### Step 1: Get Your AWS Account ID

```bash
# Get and save your AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Your AWS Account ID is: $AWS_ACCOUNT_ID"
```

#### Step 2: Set Configuration Variables

```bash
# Set these variables (modify as needed)
FUNCTION_NAME="bizbuch-presigned-url"
REGION="ap-south-1"
ROLE_NAME="bizbuch-presigned-url-lambda-role"
S3_BUCKET="bizbuch-media"
JWT_SECRET="your-django-secret-key-here"  # Replace with your actual secret

# Construct the Role ARN
ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"
echo "Using Role ARN: $ROLE_ARN"
```

#### Step 3: Create the Lambda Function

**For x86_64 Architecture:**

```bash
aws lambda create-function \
    --function-name "$FUNCTION_NAME" \
    --runtime provided.al2023 \
    --handler bootstrap \
    --architectures x86_64 \
    --zip-file fileb://function.zip \
    --role "$ROLE_ARN" \
    --timeout 10 \
    --memory-size 128 \
    --environment "Variables={AWS_REGION=${REGION},AWS_S3_BUCKET=${S3_BUCKET},JWT_SECRET=${JWT_SECRET}}" \
    --region "$REGION"
```

**For ARM64 Architecture (Graviton2 - 20% cheaper):**

```bash
aws lambda create-function \
    --function-name "$FUNCTION_NAME" \
    --runtime provided.al2023 \
    --handler bootstrap \
    --architectures arm64 \
    --zip-file fileb://function.zip \
    --role "$ROLE_ARN" \
    --timeout 10 \
    --memory-size 128 \
    --environment "Variables={AWS_REGION=${REGION},AWS_S3_BUCKET=${S3_BUCKET},JWT_SECRET=${JWT_SECRET}}" \
    --region "$REGION"
```

**Expected Output:**

```json
{
    "FunctionName": "bizbuch-presigned-url",
    "FunctionArn": "arn:aws:lambda:ap-south-1:123456789012:function:bizbuch-presigned-url",
    "Runtime": "provided.al2023",
    "Role": "arn:aws:iam::123456789012:role/bizbuch-presigned-url-lambda-role",
    "Handler": "bootstrap",
    "CodeSize": 8945678,
    "Timeout": 10,
    "MemorySize": 128,
    "State": "Pending",
    ...
}
```

> 📝 **Save the FunctionArn** - you'll need it for API Gateway setup!

#### Step 4: Wait for Function to be Active

```bash
# Wait for the function to be ready
aws lambda wait function-active-v2 \
    --function-name "$FUNCTION_NAME" \
    --region "$REGION"

echo "✅ Lambda function is now active!"
```

#### Step 5: Verify the Deployment

```bash
# Check the function configuration
aws lambda get-function-configuration \
    --function-name "$FUNCTION_NAME" \
    --region "$REGION" \
    --query '{Name:FunctionName,State:State,Runtime:Runtime,Memory:MemorySize,Timeout:Timeout}' \
    --output table
```

**Expected Output:**

```
----------------------------------------------------------
|                GetFunctionConfiguration                |
+---------+----------+----------+-------------------+----+
| Memory  |   Name   | Runtime  |      State        |Timeout|
+---------+----------+----------+-------------------+----+
|  128    | bizbuch-presigned-url| provided.al2023| Active|  10 |
+---------+----------+----------+-------------------+----+
```

#### Step 6: Test the Function (Optional)

```bash
# Invoke the function with a test event
aws lambda invoke \
    --function-name "$FUNCTION_NAME" \
    --region "$REGION" \
    --payload '{"httpMethod":"POST","path":"/presign/upload","headers":{"Authorization":"Bearer test"},"body":"{\"contentType\":\"image/jpeg\"}"}' \
    --cli-binary-format raw-in-base64-out \
    response.json

# View the response
cat response.json
```

---

### Option 3: Using AWS SAM (For Infrastructure as Code)

AWS SAM (Serverless Application Model) is ideal for managing infrastructure as code.

#### Prerequisites

```bash
# Install AWS SAM CLI (if not installed)
# On Ubuntu/Debian:
pip install aws-sam-cli

# On macOS with Homebrew:
brew install aws-sam-cli

# Verify installation
sam --version
```

#### Step 1: Navigate to the Lambda Directory

```bash
cd /home/ujjwal/Desktop/BizBuch/BizBuch-Backend/lambda/pre-signed-url
```

#### Step 2: Review the SAM Template

The `template.yaml` file defines your Lambda function. Open it to verify:

```bash
cat template.yaml
```

#### Step 3: Build with SAM

```bash
# Build the function
sam build

# This creates a .aws-sam directory with the built artifacts
```

#### Step 4: Deploy with Guided Mode (First Time)

```bash
sam deploy --guided
```

SAM will ask you several questions:

```
Setting default arguments for 'sam deploy'
=========================================
Stack Name [sam-app]: bizbuch-presigned-url-stack
AWS Region [us-east-1]: ap-south-1
Confirm changes before deploy [y/N]: y
Allow SAM CLI IAM role creation [Y/n]: Y
Disable rollback [y/N]: N
Save arguments to configuration file [Y/n]: Y
SAM configuration file [samconfig.toml]: 
SAM configuration environment [default]: 
```

#### Step 5: Deploy (Subsequent Times)

After the first deployment, just run:

```bash
sam deploy
```

#### Step 6: Get the API Endpoint

After deployment, SAM will output the API Gateway URL:

```
CloudFormation outputs from deployed stack
------------------------------------------
Outputs
------------------------------------------
Key                 PresignedUrlApi
Description         API Gateway endpoint URL
Value               https://abc123xyz.execute-api.ap-south-1.amazonaws.com/Prod/
------------------------------------------
```

---

### Understanding Deployment Parameters

Here's what each parameter means:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `--function-name` | `bizbuch-presigned-url` | Unique identifier for your function |
| `--runtime` | `provided.al2023` | Custom runtime for compiled Go binary |
| `--handler` | `bootstrap` | Name of the executable file |
| `--architectures` | `x86_64` or `arm64` | CPU architecture (must match your build) |
| `--zip-file` | `fileb://function.zip` | Path to your deployment package |
| `--role` | `arn:aws:iam::...` | IAM role ARN for permissions |
| `--timeout` | `10` | Max execution time in seconds |
| `--memory-size` | `128` | RAM allocation in MB |
| `--environment` | `Variables={...}` | Runtime configuration |
| `--region` | `ap-south-1` | AWS region to deploy to |

---

### Troubleshooting Deployment Issues

#### Error: "Function not found"
```bash
# Check if function exists
aws lambda get-function --function-name bizbuch-presigned-url --region ap-south-1
```
**Solution**: Make sure you created the function first.

#### Error: "Role does not exist"
**Solution**: 
1. Verify the role exists: `aws iam get-role --role-name bizbuch-presigned-url-lambda-role`
2. Check you're using the correct AWS account
3. Complete the "IAM Role Setup" section first

#### Error: "Invalid zip file"
**Solution**:
```bash
# Rebuild the deployment package
cd /home/ujjwal/Desktop/BizBuch/BizBuch-Backend/lambda/pre-signed-url
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -tags lambda.norpc -o bootstrap main.go
chmod +x bootstrap
zip function.zip bootstrap
```

#### Error: "exec format error" when testing
**Cause**: Architecture mismatch between build and Lambda setting.
**Solution**: Ensure you built for the same architecture as configured in Lambda:
- If Lambda is set to `x86_64`, build with `GOARCH=amd64`
- If Lambda is set to `arm64`, build with `GOARCH=arm64`

#### Function times out
**Solution**: Increase the timeout:
```bash
aws lambda update-function-configuration \
    --function-name bizbuch-presigned-url \
    --timeout 30 \
    --region ap-south-1
```

---

### Quick Reference Commands

```bash
# View function details
aws lambda get-function --function-name bizbuch-presigned-url --region ap-south-1

# View function configuration only
aws lambda get-function-configuration --function-name bizbuch-presigned-url --region ap-south-1

# Update function code
aws lambda update-function-code \
    --function-name bizbuch-presigned-url \
    --zip-file fileb://function.zip \
    --region ap-south-1

# Update environment variables
aws lambda update-function-configuration \
    --function-name bizbuch-presigned-url \
    --environment "Variables={AWS_REGION=ap-south-1,AWS_S3_BUCKET=bizbuch-media,JWT_SECRET=new-secret}" \
    --region ap-south-1

# Delete function (if needed to start over)
aws lambda delete-function --function-name bizbuch-presigned-url --region ap-south-1
```

---

## API Gateway Configuration

### What is API Gateway and Why Do We Need It?

**Amazon API Gateway** is a service that acts as a "front door" for your Lambda function. Think of it like a receptionist:

- **Without API Gateway**: Your Lambda function exists, but no one from the internet can reach it
- **With API Gateway**: Users can call your Lambda function via HTTP URLs like `https://abc123.execute-api.ap-south-1.amazonaws.com/presign/upload`

**How it works:**

```
User/Frontend App                API Gateway                    Lambda Function
      |                              |                                |
      |  POST /presign/upload        |                                |
      |----------------------------->|                                |
      |                              |  Invoke Lambda                 |
      |                              |------------------------------->|
      |                              |                                |
      |                              |         Response               |
      |                              |<-------------------------------|
      |        JSON Response         |                                |
      |<-----------------------------|                                |
```

### API Gateway Types

AWS offers two types of API Gateway:

| Type | Best For | Cost | Features |
|------|----------|------|----------|
| **HTTP API** | Simple REST APIs, Lambda integrations | Cheaper (up to 70% less) | Basic features, faster |
| **REST API** | Complex APIs, advanced features | More expensive | More control, API keys, usage plans |

**For this project, we'll use HTTP API** because it's simpler and cheaper.

### Before You Begin - Checklist

Make sure you have:

- [ ] ✅ Created and deployed the Lambda function `bizbuch-presigned-url`
- [ ] ✅ Tested the Lambda function successfully
- [ ] ✅ Have your AWS Account ID ready
- [ ] ✅ Have your Lambda Function ARN (from the previous section)

---

### Option 1: Using AWS Console (Recommended for Beginners)

This method uses the visual AWS website interface.

#### Step 1: Open API Gateway Console

1. Open your browser and go to: https://console.aws.amazon.com/apigateway
2. Sign in to your AWS account
3. Make sure you're in the correct region (check top-right corner)
   - For India: Select **Asia Pacific (Mumbai) ap-south-1**

#### Step 2: Create a New API

1. On the API Gateway dashboard, you'll see different API types

2. Find the **"HTTP API"** card and click **"Build"**

   > 💡 **Why HTTP API?** It's simpler, cheaper, and perfect for Lambda integrations. REST API has more features but is more complex and expensive.

#### Step 3: Add Integrations (Connect to Lambda FIRST)

On the "Create an API" page, you'll see **"Add integration"** section. You must add the Lambda integration **before** you can add routes.

1. Click **"Add integration"**

2. Configure the integration:
   
   | Field | Value |
   |-------|-------|
   | **Integration type** | Select **Lambda** from the dropdown |
   | **AWS Region** | `ap-south-1` (or your region) |
   | **Lambda function** | Start typing `bizbuch-presigned-url` and select it from the dropdown |

   > ⚠️ If you don't see your Lambda function in the dropdown:
   > - Make sure you're in the correct AWS region
   > - Verify the Lambda function was created successfully
   > - Try refreshing the page

3. You should see the integration added showing:
   - **Lambda** - `bizbuch-presigned-url`

4. **API name**: Enter `bizbuch-presigned-url-api` in the "API name" field (if not already filled)

#### Step 4: Configure Routes

Now that you have an integration, the **"Add route"** button will be enabled!

1. Click **"Add route"** (it should now be clickable)

2. Configure the first route:
   
   | Field | Value |
   |-------|-------|
   | **Method** | Select `POST` from dropdown |
   | **Resource path** | Type `/presign/upload` |
   | **Integration target** | Select the Lambda integration you just created |

3. Click **"Add route"** again for the second route:
   
   | Field | Value |
   |-------|-------|
   | **Method** | `POST` |
   | **Resource path** | `/presign/view` |
   | **Integration target** | Select the same Lambda integration |

4. You should now see 2 routes listed:
   - `POST /presign/upload` → Lambda: bizbuch-presigned-url
   - `POST /presign/view` → Lambda: bizbuch-presigned-url

5. Click **"Next"** button

#### Step 5: Configure Stage

Stages are like deployment environments (e.g., dev, staging, production).

1. **Stage name**: Keep the default `$default`
   
   > 💡 The `$default` stage means requests go directly to your API without a stage prefix in the URL.

2. **Auto-deploy**: Make sure this is **enabled** (checked)
   
   > This means any changes you make are automatically deployed.

3. Click **"Next"** button

#### Step 6: Review and Create

1. Review your configuration:
   - **API name**: `bizbuch-presigned-url-api`
   - **Routes**: `POST /presign/upload`, `POST /presign/view`
   - **Integrations**: Both connected to `bizbuch-presigned-url` Lambda
   - **Stage**: `$default` with auto-deploy

2. Click **"Create"** button

3. ✅ You'll see a success message and be taken to the API details page

#### Step 7: Get Your API Endpoint URL

1. On the API details page, look for **"Invoke URL"** in the **"$default Stage"** section

2. Your API URL will look like:
   ```
   https://abc123xyz.execute-api.ap-south-1.amazonaws.com
   ```

3. **Copy and save this URL!** This is your API endpoint.

Your full endpoints will be:
- **Upload**: `https://abc123xyz.execute-api.ap-south-1.amazonaws.com/presign/upload`
- **View**: `https://abc123xyz.execute-api.ap-south-1.amazonaws.com/presign/view`

#### Step 8: Configure CORS (Cross-Origin Resource Sharing)

CORS allows your frontend (running on a different domain) to call your API.

1. In the left sidebar, click on **"CORS"**

2. Click **"Configure"**

3. Set the following:

   | Field | Value |
   |-------|-------|
   | **Access-Control-Allow-Origin** | `*` (or specific domains like `http://localhost:3000, https://yourdomain.com`) |
   | **Access-Control-Allow-Headers** | `Content-Type, Authorization` |
   | **Access-Control-Allow-Methods** | `POST, OPTIONS` |

4. Click **"Save"**

> ⚠️ **Production Note**: In production, replace `*` with your actual frontend domain(s) for security.

#### Step 9: Test Your API

Now let's test the API from the command line:

```bash
# Set your API URL (replace with your actual URL)
API_URL="https://abc123xyz.execute-api.ap-south-1.amazonaws.com"

# Get a JWT token from Django (use the method from earlier)
TOKEN="your-jwt-token-here"

# Test the upload endpoint
curl -X POST "${API_URL}/presign/upload" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"contentType": "image/jpeg"}'
```

**Expected successful response:**
```json
{
  "uploadUrl": "https://bizbuch-media.s3.ap-south-1.amazonaws.com/posts/1/uuid.jpg?X-Amz-Algorithm=...",
  "publicUrl": "posts/1/uuid.jpg"
}
```

---

### Option 2: Using AWS CLI (For Automation)

This method uses command-line tools. Good for scripting and CI/CD pipelines.

#### Step 1: Set Configuration Variables

```bash
# Set your variables
API_NAME="bizbuch-presigned-url-api"
REGION="ap-south-1"
FUNCTION_NAME="bizbuch-presigned-url"

# Get your AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $AWS_ACCOUNT_ID"
```

#### Step 2: Create the HTTP API

```bash
# Create the API and capture the output
API_RESULT=$(aws apigatewayv2 create-api \
    --name "$API_NAME" \
    --protocol-type HTTP \
    --region "$REGION")

# Extract the API ID
API_ID=$(echo $API_RESULT | jq -r '.ApiId')
echo "Created API with ID: $API_ID"

# Extract the API Endpoint
API_ENDPOINT=$(echo $API_RESULT | jq -r '.ApiEndpoint')
echo "API Endpoint: $API_ENDPOINT"
```

**Expected output:**
```json
{
    "ApiEndpoint": "https://abc123xyz.execute-api.ap-south-1.amazonaws.com",
    "ApiId": "abc123xyz",
    "Name": "bizbuch-presigned-url-api",
    "ProtocolType": "HTTP",
    ...
}
```

#### Step 3: Create Lambda Integration

```bash
# Create integration with Lambda
INTEGRATION_RESULT=$(aws apigatewayv2 create-integration \
    --api-id "$API_ID" \
    --integration-type AWS_PROXY \
    --integration-uri "arn:aws:lambda:${REGION}:${AWS_ACCOUNT_ID}:function:${FUNCTION_NAME}" \
    --payload-format-version "2.0" \
    --region "$REGION")

# Extract Integration ID
INTEGRATION_ID=$(echo $INTEGRATION_RESULT | jq -r '.IntegrationId')
echo "Created Integration with ID: $INTEGRATION_ID"
```

#### Step 4: Create Routes

```bash
# Create POST /presign/upload route
aws apigatewayv2 create-route \
    --api-id "$API_ID" \
    --route-key "POST /presign/upload" \
    --target "integrations/$INTEGRATION_ID" \
    --region "$REGION"

# Create POST /presign/view route
aws apigatewayv2 create-route \
    --api-id "$API_ID" \
    --route-key "POST /presign/view" \
    --target "integrations/$INTEGRATION_ID" \
    --region "$REGION"

# Create OPTIONS routes for CORS preflight requests
aws apigatewayv2 create-route \
    --api-id "$API_ID" \
    --route-key "OPTIONS /presign/upload" \
    --target "integrations/$INTEGRATION_ID" \
    --region "$REGION"

aws apigatewayv2 create-route \
    --api-id "$API_ID" \
    --route-key "OPTIONS /presign/view" \
    --target "integrations/$INTEGRATION_ID" \
    --region "$REGION"

echo "✅ Routes created successfully!"
```

#### Step 5: Create Default Stage with Auto-Deploy

```bash
aws apigatewayv2 create-stage \
    --api-id "$API_ID" \
    --stage-name '$default' \
    --auto-deploy \
    --region "$REGION"

echo "✅ Stage created with auto-deploy!"
```

#### Step 6: Grant API Gateway Permission to Invoke Lambda

This is **critical** - without this, API Gateway cannot call your Lambda function!

```bash
aws lambda add-permission \
    --function-name "$FUNCTION_NAME" \
    --statement-id "apigateway-invoke-${API_ID}" \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:${REGION}:${AWS_ACCOUNT_ID}:${API_ID}/*" \
    --region "$REGION"

echo "✅ Lambda permission granted to API Gateway!"
```

#### Step 7: Configure CORS

```bash
aws apigatewayv2 update-api \
    --api-id "$API_ID" \
    --cors-configuration '{
        "AllowOrigins": ["*"],
        "AllowMethods": ["POST", "OPTIONS"],
        "AllowHeaders": ["Content-Type", "Authorization"],
        "MaxAge": 86400
    }' \
    --region "$REGION"

echo "✅ CORS configured!"
```

#### Step 8: Verify and Get API URL

```bash
# Get API details
aws apigatewayv2 get-api \
    --api-id "$API_ID" \
    --region "$REGION"

# Print the final API URL
echo ""
echo "=========================================="
echo "🎉 API Gateway Setup Complete!"
echo "=========================================="
echo "API ID: $API_ID"
echo "API Endpoint: $API_ENDPOINT"
echo ""
echo "Your endpoints are:"
echo "  POST ${API_ENDPOINT}/presign/upload"
echo "  POST ${API_ENDPOINT}/presign/view"
echo "=========================================="
```

---

### Complete CLI Script

Here's a complete script you can save and run:

```bash
#!/bin/bash
set -e

# Configuration
API_NAME="bizbuch-presigned-url-api"
REGION="ap-south-1"
FUNCTION_NAME="bizbuch-presigned-url"

echo "🚀 Starting API Gateway setup..."

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $AWS_ACCOUNT_ID"

# Step 1: Create HTTP API
echo "Creating HTTP API..."
API_RESULT=$(aws apigatewayv2 create-api \
    --name "$API_NAME" \
    --protocol-type HTTP \
    --region "$REGION")

API_ID=$(echo $API_RESULT | jq -r '.ApiId')
API_ENDPOINT=$(echo $API_RESULT | jq -r '.ApiEndpoint')
echo "✅ API created: $API_ID"

# Step 2: Create Lambda Integration
echo "Creating Lambda integration..."
INTEGRATION_RESULT=$(aws apigatewayv2 create-integration \
    --api-id "$API_ID" \
    --integration-type AWS_PROXY \
    --integration-uri "arn:aws:lambda:${REGION}:${AWS_ACCOUNT_ID}:function:${FUNCTION_NAME}" \
    --payload-format-version "2.0" \
    --region "$REGION")

INTEGRATION_ID=$(echo $INTEGRATION_RESULT | jq -r '.IntegrationId')
echo "✅ Integration created: $INTEGRATION_ID"

# Step 3: Create Routes
echo "Creating routes..."
aws apigatewayv2 create-route --api-id "$API_ID" --route-key "POST /presign/upload" --target "integrations/$INTEGRATION_ID" --region "$REGION" > /dev/null
aws apigatewayv2 create-route --api-id "$API_ID" --route-key "POST /presign/view" --target "integrations/$INTEGRATION_ID" --region "$REGION" > /dev/null
aws apigatewayv2 create-route --api-id "$API_ID" --route-key "OPTIONS /presign/upload" --target "integrations/$INTEGRATION_ID" --region "$REGION" > /dev/null
aws apigatewayv2 create-route --api-id "$API_ID" --route-key "OPTIONS /presign/view" --target "integrations/$INTEGRATION_ID" --region "$REGION" > /dev/null
echo "✅ Routes created"

# Step 4: Create Stage
echo "Creating stage..."
aws apigatewayv2 create-stage \
    --api-id "$API_ID" \
    --stage-name '$default' \
    --auto-deploy \
    --region "$REGION" > /dev/null
echo "✅ Stage created"

# Step 5: Grant Lambda Permission
echo "Granting Lambda permission..."
aws lambda add-permission \
    --function-name "$FUNCTION_NAME" \
    --statement-id "apigateway-invoke-${API_ID}" \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:${REGION}:${AWS_ACCOUNT_ID}:${API_ID}/*" \
    --region "$REGION" > /dev/null 2>&1 || echo "Permission may already exist"
echo "✅ Lambda permission granted"

# Step 6: Configure CORS
echo "Configuring CORS..."
aws apigatewayv2 update-api \
    --api-id "$API_ID" \
    --cors-configuration '{
        "AllowOrigins": ["*"],
        "AllowMethods": ["POST", "OPTIONS"],
        "AllowHeaders": ["Content-Type", "Authorization"],
        "MaxAge": 86400
    }' \
    --region "$REGION" > /dev/null
echo "✅ CORS configured"

# Done!
echo ""
echo "=========================================="
echo "🎉 API Gateway Setup Complete!"
echo "=========================================="
echo "API ID: $API_ID"
echo "API Endpoint: $API_ENDPOINT"
echo ""
echo "Your endpoints are:"
echo "  POST ${API_ENDPOINT}/presign/upload"
echo "  POST ${API_ENDPOINT}/presign/view"
echo "=========================================="
```

Save this as `setup-api-gateway.sh` and run:
```bash
chmod +x setup-api-gateway.sh
./setup-api-gateway.sh
```

---

### Understanding the Components

| Component | What It Does |
|-----------|--------------|
| **API** | The container for all your routes and configurations |
| **Route** | Maps a URL path + HTTP method to an integration (e.g., `POST /presign/upload`) |
| **Integration** | Connects a route to a backend (Lambda function in our case) |
| **Stage** | A deployment snapshot of your API (like dev, staging, prod) |
| **CORS** | Allows browsers to call your API from different domains |

---

### Quick Reference: API Gateway URLs

After setup, your API will have these endpoints:

| Endpoint | URL | Purpose |
|----------|-----|---------|
| Upload | `https://{api-id}.execute-api.{region}.amazonaws.com/presign/upload` | Get presigned URL for uploading |
| View | `https://{api-id}.execute-api.{region}.amazonaws.com/presign/view` | Get presigned URL for viewing |

---

### Troubleshooting API Gateway Issues

#### Error: "Internal Server Error" (500)
**Possible causes:**
1. Lambda function has an error
2. API Gateway doesn't have permission to invoke Lambda

**Solution:**
```bash
# Check if permission exists
aws lambda get-policy --function-name bizbuch-presigned-url --region ap-south-1

# Add permission if missing
aws lambda add-permission \
    --function-name bizbuch-presigned-url \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:ap-south-1:ACCOUNT_ID:API_ID/*" \
    --region ap-south-1
```

#### Error: "Missing Authentication Token"
**Cause:** You're calling a route that doesn't exist.
**Solution:** Double-check the URL path. Make sure it's exactly `/presign/upload` or `/presign/view`.

#### Error: "CORS error" in browser
**Cause:** CORS is not configured or misconfigured.
**Solution:**
1. Check CORS settings in API Gateway Console
2. Make sure `Access-Control-Allow-Origin` includes your frontend domain
3. Verify OPTIONS routes exist for preflight requests

#### Error: "Forbidden" (403)
**Cause:** API Gateway's resource policy is blocking the request.
**Solution:** Check if there are any resource policies attached to the API that might be blocking requests.

#### How to Delete and Recreate API Gateway

If you need to start over:

```bash
# List all APIs to find the ID
aws apigatewayv2 get-apis --region ap-south-1

# Delete the API (this also deletes all routes and stages)
aws apigatewayv2 delete-api --api-id YOUR_API_ID --region ap-south-1

# Remove Lambda permission
aws lambda remove-permission \
    --function-name bizbuch-presigned-url \
    --statement-id apigateway-invoke \
    --region ap-south-1
```

---

### Quick Reference Commands

```bash
# List all HTTP APIs
aws apigatewayv2 get-apis --region ap-south-1

# Get details of a specific API
aws apigatewayv2 get-api --api-id YOUR_API_ID --region ap-south-1

# List routes for an API
aws apigatewayv2 get-routes --api-id YOUR_API_ID --region ap-south-1

# List integrations for an API
aws apigatewayv2 get-integrations --api-id YOUR_API_ID --region ap-south-1

# Get stages
aws apigatewayv2 get-stages --api-id YOUR_API_ID --region ap-south-1

# Update CORS
aws apigatewayv2 update-api \
    --api-id YOUR_API_ID \
    --cors-configuration '{"AllowOrigins":["https://yourdomain.com"],"AllowMethods":["POST","OPTIONS"],"AllowHeaders":["Content-Type","Authorization"]}' \
    --region ap-south-1

# Delete an API
aws apigatewayv2 delete-api --api-id YOUR_API_ID --region ap-south-1
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
