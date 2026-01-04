# AWS S3 Setup for Access Keys

- Document Title: AWS S3 Setup for Access Keys (Beginner Guide)
- Version: 1.0.0
- Created On: 2026-01-01
- Created By: Ujjwal Kar
- Purpose: This document provides a step-by-step guide to configure AWS S3 access keys securely for backend applications (e.g. Django) using best practices.

---

This document explains **step by step** how to set up **AWS S3 with access keys** for a backend application (e.g. Django) so that:

- The backend can generate pre‑signed URLs
- The mobile app can upload files directly to S3
- No AWS credentials are exposed to the client

This guide assumes **no prior AWS knowledge**.

---

## 1. Create an AWS Account

1. Go to https://aws.amazon.com
2. Click **Create an AWS Account**
3. Complete signup (email, password, billing)
4. Choose **Basic Support (Free)**

Once complete, log in to the **AWS Management Console**.

---

## 2. Select AWS Region

In the AWS Console (top‑right corner):

- Select region closest to you
- Example for India:
  ```
  Asia Pacific (Mumbai) – ap-south-1
  ```

⚠️ Always use the **same region** consistently.

---

## 3. Create an S3 Bucket

### 3.1 Open S3

- Services → Search **S3** → Open S3

### 3.2 Create Bucket

- Click **Create bucket**
- Bucket name:
  ```
  bizbuch-media
  ```
  (Must be globally unique)
- Region:
  ```
  ap-south-1
  ```

### 3.3 Block Public Access

Keep **Block all public access ENABLED** (default).

This prevents accidental public exposure.

### 3.4 Create

Click **Create bucket**.

---

## 4. Configure Object Ownership & ACLs

1. Open your bucket
2. Go to **Permissions** tab
3. Find **Object Ownership**
4. Set to:
   ```
   Bucket owner enforced
   ```
5. Save changes

Result:
- ACLs are disabled
- Bucket owner owns all objects
- Permissions are controlled only via IAM

---

## 5. Configure CORS (Required for Mobile Uploads)

1. Bucket → **Permissions**
2. Scroll to **CORS configuration**
3. Click **Edit** and paste:

```json
[
  {
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["PUT", "GET"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag"]
  }
]
```

4. Save changes

This allows uploads via pre‑signed URLs.

---

## 6. Create IAM User (Backend Only)

### 6.1 Open IAM

- Services → Search **IAM** → Open IAM

### 6.2 Create User

- Users → **Create user**
- User name:
  ```
  django-s3-user
  ```
- Click **Next**

---

## 7. Create IAM Policy (Least Privilege)

### 7.1 Create Policy

- Attach policies directly → **Create policy**
- Choose **JSON** tab
- Paste:

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
    }
  ]
}
```

### 7.2 Save Policy

- Policy name:
  ```
  DjangoS3UploadPolicy
  ```
- Create policy

---

## 8. Attach Policy to IAM User

- Return to user creation
- Select **DjangoS3UploadPolicy**
- Click **Create user**

---

## 9. Create Access Keys (IMPORTANT)

AWS no longer auto‑creates access keys.

### 9.1 Create Key

1. IAM → Users → `django-s3-user`
2. Open **Security credentials** tab
3. Scroll to **Access keys**
4. Click **Create access key**

### 9.2 Select Use Case

Choose:
```
Application running outside AWS
```

### 9.3 Save Credentials

You will see:
- Access key ID
- Secret access key

⚠️ This is the **ONLY time** the secret is shown.

Save them securely.

---

## 10. Configure Backend Environment Variables

Set these **ONLY in your backend environment**:

```env
AWS_ACCESS_KEY_ID=AKIAxxxxxxxx
AWS_SECRET_ACCESS_KEY=xxxxxxxx
AWS_REGION=ap-south-1
AWS_S3_BUCKET=bizbuch-media
```

🚫 Never expose these in mobile or frontend code.

---

## 11. Validate Setup (Optional Test)

Run in Django shell:

```python
import boto3
s3 = boto3.client("s3")
print(s3.list_buckets())
```

If buckets print successfully → setup is correct.

---

## 12. Final Recommended Settings Summary

| Setting | Value |
|------|------|
| Bucket region | ap-south-1 |
| Object ownership | Bucket owner enforced |
| ACLs | Disabled |
| Block public access | Enabled |
| Versioning | Enabled (with lifecycle rules) |
| IAM scope | Least privilege |

---

## 13. Security Rules to Remember

- AWS credentials belong **only on backend**
- Mobile apps upload using **pre‑signed URLs**
- JSON APIs carry **only file URLs**
- Never upload files through Django

---

## End of Document

This setup is **secure, scalable, and production‑ready**.

