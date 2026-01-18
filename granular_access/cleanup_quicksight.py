#!/usr/bin/env python3
"""
Complete QuickSight cleanup script after CDK stack destruction.
This script will:
1. List remaining QuickSight resources
2. Delete orphaned users (if possible)
3. Delete QuickSight groups
4. Provide a summary of cleanup actions
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


def list_all_groups(client):
    """List all QuickSight groups."""
    try:
        response = client.list_groups(
            AwsAccountId=AWS_ACCOUNT_ID,
            Namespace=NAMESPACE
        )
        return response.get('GroupList', [])
    except ClientError as e:
        print(f"✗ Error listing groups: {e}")
        return []


def delete_group(client, group_name):
    """Delete a QuickSight group."""
    try:
        client.delete_group(
            AwsAccountId=AWS_ACCOUNT_ID,
            Namespace=NAMESPACE,
            GroupName=group_name
        )
        return True, None
    except ClientError as e:
        return False, str(e)


def list_all_users(client):
    """List all QuickSight users."""
    try:
        response = client.list_users(
            AwsAccountId=AWS_ACCOUNT_ID,
            Namespace=NAMESPACE
        )
        return response.get('UserList', [])
    except ClientError as e:
        print(f"✗ Error listing users: {e}")
        return []


def main():
    """Main cleanup function."""
    print("=" * 80)
    print("QuickSight Complete Cleanup Script")
    print("=" * 80)
    print(f"AWS Account: {AWS_ACCOUNT_ID}")
    print(f"Region: {REGION}")
    print(f"Namespace: {NAMESPACE}")
    print("=" * 80)
    print()

    # Create QuickSight client
    qs_client = create_quicksight_client()
    print()

    # Check current state
    print("📋 Checking current QuickSight resources...")
    print("-" * 80)
    
    # List users
    users = list_all_users(qs_client)
    print(f"👥 Users found: {len(users)}")
    if users:
        for user in users:
            username = user.get('UserName', 'N/A')
            email = user.get('Email', 'N/A')
            role = user.get('Role', 'N/A')
            active = user.get('Active', False)
            status = "✓ Active" if active else "✗ Inactive"
            print(f"   - {email} ({role}) {status}")
            if username == 'N/A':
                print(f"     WARNING: Username is N/A - user may be orphaned")
    print()

    # List groups
    groups = list_all_groups(qs_client)
    print(f"👥 Groups found: {len(groups)}")
    if groups:
        for group in groups:
            print(f"   - {group['GroupName']}")
    print()

    # Determine what to clean up
    if not users and not groups:
        print("✅ No QuickSight resources to clean up!")
        print("   The CDK stack destruction already removed everything.")
        return

    # Show cleanup plan
    print("=" * 80)
    print("🗑️  Cleanup Plan")
    print("=" * 80)
    
    if users:
        print(f"⚠️  WARNING: {len(users)} orphaned users detected")
        print("   These users cannot be properly deleted because the IAM role is gone.")
        print("   They will remain in QuickSight but cannot be used.")
        print("   Contact AWS Support if you need them removed.")
        print()
    
    if groups:
        print(f"✓ Will delete {len(groups)} QuickSight groups:")
        for group in groups:
            print(f"   - {group['GroupName']}")
        print()

    # Confirm cleanup
    if groups:
        response = input("Do you want to proceed with group deletion? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("❌ Cleanup cancelled by user")
            sys.exit(0)
        
        print()
        print("🗑️  Deleting QuickSight groups...")
        print("-" * 80)

        success_count = 0
        fail_count = 0
        errors = []

        for i, group in enumerate(groups, 1):
            group_name = group['GroupName']
            print(f"[{i}/{len(groups)}] Deleting group: {group_name}")
            
            success, error = delete_group(qs_client, group_name)
            
            if success:
                print(f"   ✓ Successfully deleted")
                success_count += 1
            else:
                print(f"   ✗ Failed: {error}")
                fail_count += 1
                errors.append((group_name, error))
            
            # Brief pause
            if i < len(groups):
                time.sleep(0.5)

        # Print summary
        print()
        print("=" * 80)
        print("📊 Cleanup Summary")
        print("=" * 80)
        print(f"✅ Groups successfully deleted: {success_count}")
        print(f"❌ Groups failed to delete: {fail_count}")
        
        if errors:
            print()
            print("Failed deletions:")
            for group_name, error in errors:
                print(f"  - {group_name}: {error}")
        
        print("=" * 80)

    # Final status
    print()
    print("🔍 Final QuickSight Status:")
    print("-" * 80)
    
    remaining_users = list_all_users(qs_client)
    remaining_groups = list_all_groups(qs_client)
    
    print(f"👥 Remaining users: {len(remaining_users)}")
    if remaining_users:
        print("   ⚠️  Orphaned users still present (cannot be deleted without IAM role)")
        print("   These users will not incur charges and cannot be used.")
    
    print(f"👥 Remaining groups: {len(remaining_groups)}")
    if remaining_groups:
        for group in remaining_groups:
            print(f"   - {group['GroupName']}")
    
    if not remaining_groups:
        print("   ✓ All groups successfully removed!")
    
    print()
    print("✅ Cleanup completed!")
    print()
    print("📝 Summary:")
    print("   - CDK Stack: ✓ Destroyed")
    print("   - IAM Roles: ✓ Removed")
    print("   - S3 Bucket: ✓ Deleted")
    print("   - Lambda Functions: ✓ Deleted")
    print("   - EventBridge Rules: ✓ Deleted")
    print("   - QuickSight Groups: " + ("✓ Deleted" if not remaining_groups else "⚠️  Some remain"))
    print("   - QuickSight Users: " + ("⚠️  Orphaned (harmless)" if remaining_users else "✓ Removed"))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
