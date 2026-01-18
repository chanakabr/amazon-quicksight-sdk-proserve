# CDK Setup Guide for granular_access

## 1. Cleanup Previous CDK Setup

```bash
# Navigate to root directory
cd ~/OneDrive/repos/amazon-quicksight-sdk-proserve

# Remove CDK output directory
rm -rf cdk.out

# Remove any CDK context file
rm -f cdk.context.json

# Deactivate and remove the old virtual environment
deactivate
rm -rf .venv

# Remove any CDK config files at root level (if they exist)
rm -f cdk.json
```

## 2. Setup CDK Inside granular_access Directory

```bash
# Navigate to granular_access directory
cd ~/OneDrive/repos/amazon-quicksight-sdk-proserve/granular_access

# Create new virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/Scripts/activate

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install aws-cdk-lib constructs boto3 awscli

# Verify installations
pip list | grep aws-cdk
python --version
```

## 3. Create cdk.json in granular_access directory

Create a file named `cdk.json` with the following content:

```json
{
  "app": "python app.py",
  "context": {
    "@aws-cdk/core:newStyleStackSynthesis": true
  }
}
```

## 4. Verify your file structure

```bash
# You should have:
# granular_access/
# ├── .venv/
# ├── app.py
# ├── cdk.json (newly created)
# ├── granular_access/
# │   └── granular_access_stack.py
# ├── lambda_functions/
# └── requirements.txt
```

## 5. Set environment variables and bootstrap CDK

```bash
# Make sure you're in granular_access directory
cd ~/OneDrive/repos/amazon-quicksight-sdk-proserve/granular_access

# Add npm to PATH (for cdk command)
export PATH=$PATH:/c/Users/cratnaya/AppData/Roaming/npm

# Set AWS profile
export AWS_PROFILE=442091038412

# Verify cdk works
cdk --version

# Bootstrap CDK (only needed once per account/region)
cdk bootstrap aws://442091038412/us-east-1 --profile 442091038412

# Synthesize to verify everything works
cdk synth --profile 442091038412

# Deploy
cdk deploy granular-access --profile 442091038412
```

## 6. Update requirements.txt for future use

Update `granular_access/requirements.txt`:

```
aws-cdk-lib>=2.0.0
constructs>=10.0.0
boto3>=1.26.0
```

## Summary of key changes

- Virtual environment is now inside `granular_access` directory
- `cdk.json` is in `granular_access` directory
- All CDK commands should be run from `granular_access` directory
- No need to specify `--app` parameter anymore (it's in cdk.json)

## Troubleshooting

### If cdk command not found
```bash
export PATH=$PATH:/c/Users/cratnaya/AppData/Roaming/npm
```

### To make PATH permanent
```bash
echo 'export PATH=$PATH:/c/Users/cratnaya/AppData/Roaming/npm' >> ~/.bashrc
source ~/.bashrc
```

### If AWS credentials issues
```bash
aws configure
# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## Common CDK Commands

```bash
# List all stacks
cdk list

# Synthesize CloudFormation template
cdk synth

# Show differences between deployed stack and current state
cdk diff

# Deploy stack
cdk deploy granular-access --profile 442091038412

# Destroy stack
cdk destroy granular-access --profile 442091038412
```
