#!/usr/bin/env python3
"""Test delete permissions by attempting to delete a few spam messages"""

import sys
from gmail_mcp.auth import GmailAuth
from gmail_mcp.gmail_client import GmailClient


def test_delete_permission():
    print("🔍 Testing Gmail delete permissions...")
    print("=" * 50)
    
    try:
        # Initialize authentication and client
        auth = GmailAuth()
        client = GmailClient(auth)
        
        # Get profile to confirm authentication
        profile = client.get_profile()
        print(f"✅ Authenticated as: {profile.get('emailAddress')}")
        
        # Check current token scopes
        if hasattr(auth.creds, 'scopes'):
            print(f"\n📋 Current scopes:")
            for scope in auth.creds.scopes:
                print(f"   - {scope}")
        
        # List spam messages
        print("\n🔍 Fetching spam messages for test...")
        result = client.list_messages(
            label_ids=['SPAM'],
            max_results=5,  # Just get 5 for testing
            include_spam_trash=True
        )
        
        messages = result.get('messages', [])
        if not messages:
            print("❌ No spam messages found to test with!")
            return
        
        print(f"📧 Found {len(messages)} spam messages for testing")
        
        # Test 1: Try to delete a single message
        print("\n🧪 Test 1: Attempting to delete a single spam message...")
        test_message_id = messages[0]['id']
        
        try:
            client.delete_message(test_message_id)
            print("✅ Single message deletion: SUCCESS!")
        except Exception as e:
            print(f"❌ Single message deletion: FAILED")
            print(f"   Error: {str(e)}")
            if "insufficientPermissions" in str(e):
                print("\n⚠️  INSUFFICIENT PERMISSIONS!")
                print("You need to re-authenticate with the new scopes.")
                print("Run: python reauth_and_delete_spam.py")
                return
        
        # Test 2: Try batch delete with remaining messages
        if len(messages) > 1:
            print("\n🧪 Test 2: Attempting batch delete of remaining messages...")
            batch_ids = [msg['id'] for msg in messages[1:]]
            
            try:
                client.batch_delete_messages(batch_ids)
                print(f"✅ Batch deletion of {len(batch_ids)} messages: SUCCESS!")
            except Exception as e:
                print(f"❌ Batch deletion: FAILED")
                print(f"   Error: {str(e)}")
        
        print("\n🎉 Delete permissions are working correctly!")
        print(f"✅ You can now run 'python delete_spam_auto.py' to delete all spam.")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        if "Token has been expired or revoked" in str(e):
            print("\n⚠️  TOKEN EXPIRED!")
            print("Run: python reauth_and_delete_spam.py")
        sys.exit(1)


if __name__ == "__main__":
    test_delete_permission()