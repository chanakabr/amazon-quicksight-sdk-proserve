# Deployment Log - Granular Access CDK Stack

## Date: December 14, 2025

### Issue Encountered
Initial deployment failed due to deprecated Python runtime for Lambda functions.

**Error:**
```
The runtime parameter of python3.7 is no longer supported for creating or updating AWS Lambda functions.
```

### Resolution
Updated all Lambda function runtimes from Python 3.7/3.8 to Python 3.9.

### Changes Made

#### Updated Lambda Functions:
1. **user_init** - Changed from Python 3.7 → Python 3.9
2. **check_team_members** - Changed from Python 3.7 → Python 3.9
3. **downgrade_user** - Changed from Python 3.8 → Python 3.9
4. **granular_user_govenance** - Changed from Python 3.7 → Python 3.9
5. **granular_access_assets_govenance** - Changed from Python 3.7 → Python 3.9

#### File Modified:
- `granular_access/granular_access_stack.py`

### Deployment Steps Taken

1. **Deleted Failed Stack:**
   ```powershell
   aws cloudformation delete-stack --stack-name granular-access --region us-east-1
   ```

2. **Updated Lambda Runtimes:**
   - Modified all Lambda functions to use `_lambda.Runtime.PYTHON_3_9`

3. **Redeployed Stack:**
   ```powershell
   cdk deploy granular-access --require-approval never
   ```

### Stack Resources Being Deployed

- **SSM Parameters:** 4 parameters for QuickSight configuration
- **S3 Bucket:** qs-granular-access-demo-442091038412
- **Lambda Functions:** 5 functions with Python 3.9 runtime
- **IAM Roles:** Lambda execution role and QuickSight federated role
- **EventBridge Rules:** 2 rules for automation
- **Custom Resources:** S3 auto-delete and bucket deployment

### Current Status
✅ **DEPLOYMENT SUCCESSFUL**
✅ All 27 resources created successfully
✅ Stack completed in 127.52 seconds

### Stack ARN
```
arn:aws:cloudformation:us-east-1:442091038412:stack/granular-access/338168c0-d88e-11f0-ad1a-0e5d9c0c88f5
```

### AWS Account Details
- **Account ID:** 442091038412
- **Region:** us-east-1
- **Stack Name:** granular-access

### Next Steps After Successful Deployment
1. Verify all Lambda functions are created successfully
2. Check EventBridge rules are enabled
3. Confirm S3 bucket is created with membership data
4. Test QuickSight user governance functionality

### Notes
- Python 3.9 is a stable and widely supported runtime by AWS Lambda
- All Lambda functions should work without code changes (Python 3.7/3.8 → 3.9 is backward compatible)
- If any Lambda-specific issues arise, check CloudWatch Logs for detailed error messages
