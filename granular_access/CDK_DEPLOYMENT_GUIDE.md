# CDK Deployment Guide - QuickSight Granular Access Control

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [AWS Resources Created](#aws-resources-created)
5. [Deployment Steps](#deployment-steps)
6. [Issues Fixed During Deployment](#issues-fixed-during-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Post-Deployment Verification](#post-deployment-verification)
9. [Resource Cleanup](#resource-cleanup)

---

## Overview

This CDK stack deploys a comprehensive QuickSight granular access control solution that enables:
- Automated user provisioning and governance
- Role-based access control (RBAC)
- Group-based dashboard and report access
- Multi-namespace support for tenant isolation
- Automated asset permission management

**Stack Name:** `granular-access`  
**AWS Account:** 442091038412  
**Region:** us-east-1  
**Deployment Date:** December 14, 2025

---

## Prerequisites

### Required Software
- **Python 3.9+** (Python 3.14.2 used in this deployment)
- **Node.js 18+** (v24.11.1 used)
- **npm 8+** (v11.6.2 used)
- **AWS CLI** configured with valid credentials
- **AWS CDK CLI** (v2.1034.0 or later)

### Required AWS Permissions
- CloudFormation full access
- Lambda full access
- IAM role creation and management
- S3 bucket creation and management
- SSM parameter creation
- EventBridge rules management
- QuickSight administrative access

### Required Files
- `membership.zip` - Contains user-group mapping CSV files
- Lambda function source code in `lambda_functions/` directory

---

## Environment Setup

### 1. Virtual Environment Setup

```powershell
# Navigate to project directory
cd ~/OneDrive/repos/amazon-quicksight-sdk-proserve/granular_access

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install aws-cdk-lib constructs boto3 awscli
```

### 2. Install AWS CDK CLI

```powershell
npm install -g aws-cdk
```

### 3. Set Environment Variables

```powershell
$env:PATH += ";C:\Users\cratnaya\AppData\Roaming\npm"
$env:CDK_DEFAULT_REGION="us-east-1"
$env:CDK_DEFAULT_ACCOUNT="442091038412"
$env:AWS_PROFILE="442091038412"
```

### 4. Bootstrap CDK (One-time per account/region)

```powershell
cdk bootstrap aws://442091038412/us-east-1
```

---

## AWS Resources Created

### 1. SSM Parameters (4 total)
Configuration stored in AWS Systems Manager Parameter Store:

| Parameter Name | Purpose | Example Value |
|----------------|---------|---------------|
| `/qs/config/access` | Group-to-report access mapping | JSON with group permissions |
| `/qs/config/groups` | S3 bucket name for user-group mapping | `{"bucket-name": "qs-granular-access-demo-442091038412"}` |
| `/qs/config/roles` | Group-to-QuickSight role mapping | `{"default_bi-developer": "AUTHOR", ...}` |
| `/qs/config/ns` | Namespace configuration | `{"ns": ["default", "3rd-party"]}` |

### 2. S3 Bucket
**Bucket Name:** `qs-granular-access-demo-442091038412`

**Features:**
- Versioning enabled
- Auto-delete objects on stack deletion
- Contains membership data for user-group mappings
- Stores CSV files with user permissions

**Content:**
- `membership/` prefix with user-group mapping files

### 3. Lambda Functions (5 total)

| Function Name | Runtime | Memory | Timeout | Purpose |
|--------------|---------|--------|---------|---------|
| `user_init` | Python 3.9 | 512 MB | 15 min | Initialize new QuickSight users |
| `check_team_members` | Python 3.9 | 512 MB | 15 min | Validate team membership |
| `downgrade_user` | Python 3.9 | 2048 MB | 15 min | Downgrade user permissions |
| `granular_user_govenance` | Python 3.9 | 2048 MB | 15 min | Manage user governance policies |
| `granular_access_assets_govenance` | Python 3.9 | 2048 MB | 15 min | Manage asset-level permissions |

**Lambda Execution Role:** `us-east-1-role-quicksight-lambda`

**Permissions:**
- QuickSight full access
- S3 read/write access
- SSM parameter read access
- CloudWatch Logs write access
- KMS decrypt access
- Directory Services access

### 4. IAM Roles (2 total)

#### a) Lambda Execution Role
**Role Name:** `us-east-1-role-quicksight-lambda`

**Key Permissions:**
```json
{
  "Actions": [
    "quicksight:*",
    "s3:GetObject", "s3:PutObject", "s3:ListBucket",
    "ssm:GetParameter", "ssm:GetParametersByPath",
    "logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents",
    "lambda:InvokeFunction",
    "kms:Decrypt",
    "ds:DescribeDirectories",
    "cloudwatch:PutMetricData",
    "sts:GetCallerIdentity"
  ]
}
```

**Denies:**
```json
{
  "Actions": ["quicksight:Unsubscribe"]
}
```

#### b) QuickSight Federated Users Role
**Role Name:** `quicksight-fed-us-users`

**Purpose:** SAML-based federated access for QuickSight users

**Trust Policy:**
- Federated principal: `arn:aws:iam::442091038412:saml-provider/saml`
- Condition: SAML audience must match AWS sign-in URL

### 5. EventBridge Rules (2 total)

#### a) User Creation Rule
**Rule Name:** `qs-gc-user-creation`

**Event Pattern:**
```json
{
  "source": ["aws.quicksight"],
  "detail-type": ["AWS Service Event via CloudTrail"],
  "detail": {
    "eventSource": ["quicksight.amazonaws.com"],
    "eventName": ["CreateUser"]
  }
}
```

**Target:** `user_init` Lambda function

**Purpose:** Automatically initialize new QuickSight users with appropriate permissions

#### b) Hourly Governance Rule
**Rule Name:** `qs-gc-every-hour`

**Schedule:** Cron expression: `cron(0 * * * ? *)` (Every hour at :00)

**Target:** `granular_user_govenance` Lambda function

**Purpose:** Periodic synchronization of user permissions and governance policies

### 6. Custom Resources (2 total)

#### a) S3 Auto-Delete Objects
- Automatically deletes S3 objects when stack is destroyed
- Lambda-backed custom resource
- Ensures clean stack deletion

#### b) S3 Bucket Deployment
- Deploys `membership.zip` contents to S3 bucket
- Extracts files to `membership/` prefix
- Lambda-backed custom resource with AWS CLI layer

---

## Deployment Steps

### Step 1: Prepare Environment

```powershell
# Navigate to project directory
cd ~/OneDrive/repos/amazon-quicksight-sdk-proserve/granular_access

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Set required environment variables
$env:PATH += ";C:\Users\cratnaya\AppData\Roaming\npm"
$env:CDK_DEFAULT_REGION="us-east-1"
$env:CDK_DEFAULT_ACCOUNT="442091038412"
$env:AWS_PROFILE="442091038412"
```

### Step 2: Verify AWS Credentials

```powershell
aws sts get-caller-identity
```

**Expected Output:**
```json
{
  "UserId": "AIDAWN3VN43GIYSJEYH7Z",
  "Account": "442091038412",
  "Arn": "arn:aws:iam::442091038412:user/chanakabr-admin"
}
```

### Step 3: Synthesize CloudFormation Template

```powershell
cdk synth
```

**Purpose:** Generate and validate CloudFormation template before deployment

### Step 4: Review Changes (Optional)

```powershell
cdk diff
```

**Purpose:** See what resources will be created/modified

### Step 5: Deploy Stack

```powershell
cdk deploy granular-access --require-approval never
```

**Deployment Time:** Approximately 5-10 minutes

**Progress Indicators:**
- Asset building and uploading
- CloudFormation stack creation
- Resource provisioning (Lambda, IAM, S3, etc.)
- Custom resource execution
- Stack completion

### Step 6: Verify Deployment

```powershell
# Check stack status
aws cloudformation describe-stacks --stack-name granular-access --region us-east-1

# List stack resources
aws cloudformation list-stack-resources --stack-name granular-access --region us-east-1
```

---

## Issues Fixed During Deployment

### Issue 1: Python Runtime Deprecation

**Problem:**
```
The runtime parameter of python3.7 is no longer supported for creating or updating AWS Lambda functions.
```

**Root Cause:**
- Original code used Python 3.7 and 3.8 runtimes
- Python 3.7 reached end-of-life and was deprecated by AWS Lambda
- CloudFormation rejected Lambda function creation

**Solution:**
Updated all Lambda functions to Python 3.9 in `granular_access_stack.py`:

```python
# Before
runtime=_lambda.Runtime.PYTHON_3_7

# After
runtime=_lambda.Runtime.PYTHON_3_9
```

**Functions Updated:**
1. `user_init` (3.7 → 3.9)
2. `check_team_members` (3.7 → 3.9)
3. `downgrade_user` (3.8 → 3.9)
4. `granular_user_govenance` (3.7 → 3.9)
5. `granular_access_assets_govenance` (3.7 → 3.9)

**Stack Rollback:**
First deployment failed with `ROLLBACK_COMPLETE` status. Stack had to be manually deleted before redeployment:

```powershell
aws cloudformation delete-stack --stack-name granular-access --region us-east-1
aws cloudformation wait stack-delete-complete --stack-name granular-access --region us-east-1
```

### Issue 2: CDK v1 Feature Flags

**Problem:**
```
Unsupported feature flag '@aws-cdk/core:enableStackNameDuplicates'. This flag existed on CDKv1 but has been removed in CDKv2.
```

**Root Cause:**
- `cdk.json` contained CDK v1 feature flags incompatible with CDK v2

**Solution:**
Updated `cdk.json` to remove deprecated flags:

```json
// Before
{
  "app": "python3 app.py",
  "context": {
    "@aws-cdk/core:enableStackNameDuplicates": "true",
    "aws-cdk:enableDiffNoFail": "true",
    "@aws-cdk/core:stackRelativeExports": "true"
  }
}

// After
{
  "app": "python app.py",
  "context": {
    "@aws-cdk/core:newStyleStackSynthesis": true,
    "aws-cdk:enableDiffNoFail": "true"
  }
}
```

### Issue 3: Python Command Mismatch

**Problem:**
CDK was trying to use `python3` command, but virtual environment only had `python` available.

**Solution:**
Changed `cdk.json` app command from `python3 app.py` to `python app.py`

---

## Troubleshooting

### Common Issues and Solutions

#### 1. CDK Command Not Found

**Symptom:**
```
cdk: command not found
```

**Solution:**
```powershell
# Add npm global bin to PATH
$env:PATH += ";C:\Users\cratnaya\AppData\Roaming\npm"

# Verify
cdk --version
```

**Permanent Fix:**
```powershell
# Add to PowerShell profile
Add-Content $PROFILE "`n# AWS CDK PATH`n`$env:PATH += ';C:\Users\cratnaya\AppData\Roaming\npm'"
```

#### 2. AWS Credentials Not Found

**Symptom:**
```
Need to perform AWS calls for account 442091038412, but no credentials have been configured
```

**Solution:**
```powershell
# Configure AWS CLI
aws configure

# Or set environment variables
$env:AWS_ACCESS_KEY_ID="your_key"
$env:AWS_SECRET_ACCESS_KEY="your_secret"
$env:AWS_DEFAULT_REGION="us-east-1"
```

#### 3. Module Not Found Error

**Symptom:**
```
ModuleNotFoundError: No module named 'aws_cdk'
```

**Solution:**
```powershell
# Ensure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install aws-cdk-lib constructs boto3
```

#### 4. CDK_DEFAULT_REGION Not Set

**Symptom:**
```
KeyError: 'CDK_DEFAULT_REGION'
```

**Solution:**
```powershell
$env:CDK_DEFAULT_REGION="us-east-1"
$env:CDK_DEFAULT_ACCOUNT="442091038412"
```

#### 5. Stack Already Exists (Failed State)

**Symptom:**
```
Stack already exists in ROLLBACK_COMPLETE state
```

**Solution:**
```powershell
# Delete the failed stack
aws cloudformation delete-stack --stack-name granular-access --region us-east-1

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete --stack-name granular-access --region us-east-1

# Redeploy
cdk deploy granular-access
```

#### 6. Lambda Runtime Errors

**Symptom:**
Lambda functions fail at runtime with import errors

**Solution:**
- Verify Lambda function code is compatible with Python 3.9
- Check that all required packages are included in Lambda deployment package
- Review CloudWatch Logs for detailed error messages:

```powershell
aws logs tail /aws/lambda/user_init --follow --region us-east-1
```

#### 7. Permission Denied Errors

**Symptom:**
IAM permission errors during deployment

**Solution:**
- Ensure deploying user has required permissions (CloudFormation, IAM, Lambda, S3, etc.)
- Check IAM policy attachments
- Review CloudTrail logs for specific denied actions

#### 8. S3 Bucket Already Exists

**Symptom:**
```
Bucket already exists and is owned by another account
```

**Solution:**
- S3 bucket names are globally unique
- Either delete the existing bucket or change the bucket name in the stack
- Update `account_id` variable to ensure unique bucket name

---

## Post-Deployment Verification

### 1. Verify CloudFormation Stack

```powershell
# Check stack status
aws cloudformation describe-stacks `
  --stack-name granular-access `
  --region us-east-1 `
  --query "Stacks[0].StackStatus"
```

**Expected Output:** `"CREATE_COMPLETE"`

### 2. Verify Lambda Functions

```powershell
# List Lambda functions
aws lambda list-functions `
  --region us-east-1 `
  --query "Functions[?starts_with(FunctionName, 'user_') || starts_with(FunctionName, 'check_') || starts_with(FunctionName, 'downgrade_') || starts_with(FunctionName, 'granular_')].{Name:FunctionName, Runtime:Runtime, Status:State}"
```

**Expected Output:**
```json
[
  {"Name": "user_init", "Runtime": "python3.9", "Status": "Active"},
  {"Name": "check_team_members", "Runtime": "python3.9", "Status": "Active"},
  {"Name": "downgrade_user", "Runtime": "python3.9", "Status": "Active"},
  {"Name": "granular_user_govenance", "Runtime": "python3.9", "Status": "Active"},
  {"Name": "granular_access_assets_govenance", "Runtime": "python3.9", "Status": "Active"}
]
```

### 3. Verify S3 Bucket and Contents

```powershell
# Check bucket exists
aws s3 ls s3://qs-granular-access-demo-442091038412

# List membership files
aws s3 ls s3://qs-granular-access-demo-442091038412/membership/
```

### 4. Verify SSM Parameters

```powershell
# List parameters
aws ssm get-parameters-by-path `
  --path "/qs/config" `
  --region us-east-1 `
  --query "Parameters[].Name"
```

**Expected Output:**
```json
[
  "/qs/config/access",
  "/qs/config/groups",
  "/qs/config/ns",
  "/qs/config/roles"
]
```

### 5. Verify EventBridge Rules

```powershell
# List rules
aws events list-rules `
  --region us-east-1 `
  --query "Rules[?starts_with(Name, 'qs-gc')].{Name:Name, State:State}"
```

**Expected Output:**
```json
[
  {"Name": "qs-gc-user-creation", "State": "ENABLED"},
  {"Name": "qs-gc-every-hour", "State": "ENABLED"}
]
```

### 6. Verify IAM Roles

```powershell
# Check Lambda execution role
aws iam get-role `
  --role-name us-east-1-role-quicksight-lambda `
  --query "Role.RoleName"

# Check QuickSight federated role
aws iam get-role `
  --role-name quicksight-fed-us-users `
  --query "Role.RoleName"
```

### 7. Test Lambda Function (Optional)

```powershell
# Test user_init function
aws lambda invoke `
  --function-name user_init `
  --payload '{}' `
  --region us-east-1 `
  response.json

# View response
Get-Content response.json
```

---

## Resource Cleanup

### Delete the Stack

```powershell
# Delete stack (will remove all resources)
cdk destroy granular-access

# Or use CloudFormation directly
aws cloudformation delete-stack --stack-name granular-access --region us-east-1

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name granular-access --region us-east-1
```

### What Gets Deleted Automatically

- ✅ Lambda functions
- ✅ IAM roles and policies
- ✅ EventBridge rules
- ✅ SSM parameters
- ✅ S3 bucket (including all objects, due to `auto_delete_objects=True`)
- ✅ CloudWatch Log Groups (after retention period)

### Manual Cleanup (If Needed)

If stack deletion fails, manually delete:

1. **S3 Bucket:**
```powershell
aws s3 rb s3://qs-granular-access-demo-442091038412 --force
```

2. **Lambda Functions:**
```powershell
aws lambda delete-function --function-name user_init
aws lambda delete-function --function-name check_team_members
aws lambda delete-function --function-name downgrade_user
aws lambda delete-function --function-name granular_user_govenance
aws lambda delete-function --function-name granular_access_assets_govenance
```

3. **IAM Roles:**
```powershell
aws iam delete-role --role-name us-east-1-role-quicksight-lambda
aws iam delete-role --role-name quicksight-fed-us-users
```

---

## Best Practices

### 1. Version Control
- Keep `cdk.json`, `app.py`, and stack files in version control
- Document all changes in deployment logs
- Use feature branches for testing changes

### 2. Environment Management
- Use separate AWS accounts/regions for dev/test/prod
- Parameterize account IDs and regions
- Use CDK context for environment-specific values

### 3. Security
- Follow principle of least privilege for IAM roles
- Enable CloudTrail for audit logging
- Use KMS encryption for sensitive data in S3
- Regularly rotate credentials

### 4. Monitoring
- Set up CloudWatch alarms for Lambda errors
- Monitor Lambda duration and memory usage
- Track QuickSight user creation events
- Review EventBridge rule executions

### 5. Cost Optimization
- Review Lambda memory allocation (2048 MB may be excessive)
- Use S3 lifecycle policies for old membership data
- Clean up unused CloudWatch Log Groups
- Monitor S3 storage costs

### 6. Disaster Recovery
- Regular backups of S3 bucket contents
- Export SSM parameters periodically
- Document manual configuration steps
- Test stack recreation in separate account

---

## Additional Resources

### AWS Documentation
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
- [AWS Lambda Python Runtime](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [Amazon QuickSight API Reference](https://docs.aws.amazon.com/quicksight/latest/APIReference/)
- [AWS CloudFormation User Guide](https://docs.aws.amazon.com/cloudformation/)

### Project Files
- `CDK_SETUP_GUIDE.md` - Initial setup instructions
- `DEPLOYMENT_LOG.md` - Detailed deployment history
- `README.md` - Project overview

### Support
For issues or questions:
1. Check CloudWatch Logs for Lambda function errors
2. Review CloudTrail for API call failures
3. Check AWS Service Health Dashboard
4. Contact AWS Support if needed

---

## Appendix

### A. Complete Environment Variables

```powershell
$env:PATH += ";C:\Users\cratnaya\AppData\Roaming\npm"
$env:CDK_DEFAULT_REGION="us-east-1"
$env:CDK_DEFAULT_ACCOUNT="442091038412"
$env:AWS_PROFILE="442091038412"
$env:AWS_DEFAULT_REGION="us-east-1"
```

### B. Complete Deployment Command Sequence

```powershell
# 1. Setup
cd ~/OneDrive/repos/amazon-quicksight-sdk-proserve/granular_access
.\.venv\Scripts\Activate.ps1
$env:PATH += ";C:\Users\cratnaya\AppData\Roaming\npm"
$env:CDK_DEFAULT_REGION="us-east-1"
$env:CDK_DEFAULT_ACCOUNT="442091038412"
$env:AWS_PROFILE="442091038412"

# 2. Verify
aws sts get-caller-identity
cdk --version

# 3. Deploy
cdk synth
cdk deploy granular-access --require-approval never

# 4. Verify
aws cloudformation describe-stacks --stack-name granular-access --region us-east-1
```

### C. Stack Outputs

After successful deployment, the stack provides no explicit outputs, but creates resources with predictable names:

| Resource Type | Name Pattern | Example |
|--------------|-------------|---------|
| S3 Bucket | `qs-granular-access-demo-{account-id}` | `qs-granular-access-demo-442091038412` |
| Lambda Functions | Function name | `user_init`, `check_team_members`, etc. |
| IAM Role | `{region}-role-quicksight-lambda` | `us-east-1-role-quicksight-lambda` |
| EventBridge Rules | `qs-gc-*` | `qs-gc-user-creation`, `qs-gc-every-hour` |

### D. Estimated Costs

**Monthly AWS costs (estimated):**
- Lambda: ~$5-20 (depending on usage)
- S3: ~$1-5 (depending on data size)
- CloudWatch Logs: ~$1-3
- EventBridge: Minimal (first 1M events free)
- SSM Parameters: Free (standard parameters)

**Total estimated: $10-30/month**

---

**Document Version:** 1.0  
**Last Updated:** December 14, 2025  
**Author:** CDK Deployment Team  
**Status:** Production Ready
