#!/usr/bin/env python3
"""
Script to delete all QuickSight users created by the CDK stack.
This script will delete users but preserve the admin account.
"""

import boto3
import sys
import time
from botocore.exceptions import ClientError

# Configuration
AWS_ACCOUNT_ID = "442091038412"
REGION = "us-east-1"
NAMESPACE = "default"
PROFILE = "442091038412"

# Users to delete (federated users created by CDK)
USERS_TO_DELETE = [
    "quicksight-fed-us-users/JoyceKemp@oktank.com",
    "quicksight-fed-us-users/JohnKing@oktank.com",
    "quicksight-fed-us-users/TeresitaRedd@oktank.com",
    "quicksight-fed-us-users/GretchenJoyce@oktank.com",
    "quicksight-fed-us-users/AlbertPowers@oktank.com",
    "quicksight-fed-us-users/KevinGunn@oktank.com",
    "quicksight-fed-us-users/MichaelBrown@oktank.com",
    "quicksight-fed-us-users/TimothyMcgloin@oktank.com",
    "quicksight-fed-us-users/WayneMaxwell@oktank.com",
    "quicksight-fed-us-users/ThomasYang@oktank.com",
    "quicksight-fed-us-users/TrinhHartmann@oktank.com",
    "quicksight-fed-us-users/StephenMoretz@oktank.com",
    "quicksight-fed-us-users/CatherineCimino@oktank.com",
    "quicksight-fed-us-users/StevenLudwick@oktank.com",
    "quicksight-fed-us-users/MarshallBanks@oktank.com",
    "quicksight-fed-us-users/BettyRamirez@oktank.com"
]

# Admin user to preserve (optional - set to None to delete all)
PRESERVE_ADMIN = "442091038412"


def create_quicksight_client():
    """Create QuickSight client with specified profile."""
    try:
        session = boto3.Session(profile_name=PROFILE, region_name=REGION)
        client = session.client('quicksight')
        print(f"✓ Connected to QuickSight in region {REGION}")
        return client
    except Exception as e:
        print(f"✗ Error connecting to QuickSight: {e}")
        sys.exit(1)


def list_all_users(client):
    """List all QuickSight users in the account."""
    try:
        response = client.list_users(
            AwsAccountId=AWS_ACCOUNT_ID,
            Namespace=NAMESPACE
        )
        return response.get('UserList', [])
    except ClientError as e:
        print(f"✗ Error listing users: {e}")
        return []


def delete_user(client, user_name):
    """Delete a single QuickSight user."""
    try:
        client.delete_user(
            AwsAccountId=AWS_ACCOUNT_ID,
            Namespace=NAMESPACE,
            UserName=user_name
        )
        return True, None
    except ClientError as e:
        return False, str(e)


def main():
    """Main function to delete QuickSight users."""
    print("=" * 70)
    print("QuickSight User Deletion Script")
    print("=" * 70)
    print(f"AWS Account: {AWS_ACCOUNT_ID}")
    print(f"Region: {REGION}")
    print(f"Namespace: {NAMESPACE}")
    print("=" * 70)
    print()

    # Create QuickSight client
    qs_client = create_quicksight_client()
    
    # List current users
    print("📋 Listing current QuickSight users...")
    all_users = list_all_users(qs_client)
    print(f"   Found {len(all_users)} total users in the account")
    print()

    # Determine which users to delete
    if USERS_TO_DELETE:
        users_to_process = USERS_TO_DELETE
        print(f"🎯 Targeting {len(users_to_process)} specific users for deletion")
    else:
        # Delete all users except admin
        users_to_process = [
            user['UserName'] for user in all_users 
            if user['UserName'] != PRESERVE_ADMIN
        ]
        print(f"🎯 Targeting all users except admin: {len(users_to_process)} users")
    
    if PRESERVE_ADMIN:
        print(f"   Preserving admin user: {PRESERVE_ADMIN}")
    print()

    # Confirm deletion
    print("⚠️  WARNING: This will permanently delete the following users:")
    for i, user in enumerate(users_to_process, 1):
        print(f"   {i}. {user}")
    print()
    
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Deletion cancelled by user")
        sys.exit(0)
    
    print()
    print("🗑️  Starting user deletion...")
    print("-" * 70)

    # Delete users
    success_count = 0
    fail_count = 0
    errors = []

    for i, user_name in enumerate(users_to_process, 1):
        print(f"[{i}/{len(users_to_process)}] Deleting: {user_name}")
        
        success, error = delete_user(qs_client, user_name)
        
        if success:
            print(f"   ✓ Successfully deleted")
            success_count += 1
        else:
            print(f"   ✗ Failed: {error}")
            fail_count += 1
            errors.append((user_name, error))
        
        # Brief pause to avoid rate limiting
        if i < len(users_to_process):
            time.sleep(0.5)

    # Print summary
    print()
    print("=" * 70)
    print("📊 Deletion Summary")
    print("=" * 70)
    print(f"✅ Successfully deleted: {success_count} users")
    print(f"❌ Failed to delete: {fail_count} users")
    print(f"📈 Total processed: {len(users_to_process)} users")
    
    if errors:
        print()
        print("Failed deletions:")
        for user_name, error in errors:
            print(f"  - {user_name}: {error}")
    
    print("=" * 70)
    
    # Verify remaining users
    print()
    print("🔍 Verifying remaining users...")
    remaining_users = list_all_users(qs_client)
    print(f"   {len(remaining_users)} users remaining in the account:")
    for user in remaining_users:
        role = user.get('Role', 'N/A')
        print(f"   - {user['UserName']} ({role})")
    
    print()
    print("✅ Script completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
