#!/usr/bin/env python3
"""Re-authenticate with full permissions and delete spam"""

import asyncio
import sys
from gmail_mcp.auth import GmailAuth
from gmail_mcp.gmail_client import GmailClient


def main():
    print("🔐 Re-authenticating with full Gmail permissions...")
    print("=" * 50)
    print("⚠️  A browser window will open for authentication.")
    print("Please grant ALL requested permissions to enable deletion.")
    print("=" * 50)
    
    try:
        # This will trigger re-authentication with new scopes
        auth = GmailAuth()
        client = GmailClient(auth)
        
        print("\n✅ Authentication successful!")
        
        # Test by getting profile
        profile = client.get_profile()
        print(f"📧 Authenticated as: {profile.get('emailAddress')}")
        
        # Now let's count spam
        print("\n🔍 Checking spam folder...")
        result = client.list_messages(
            label_ids=['SPAM'],
            max_results=1,
            include_spam_trash=True
        )
        
        total_spam = result.get('resultSizeEstimate', 0)
        print(f"📊 Estimated spam messages: {total_spam}")
        
        if total_spam > 0:
            print("\n✅ You now have permission to delete spam!")
            print("Run 'python delete_spam_auto.py' to delete all spam messages.")
        else:
            print("\n✅ No spam messages found!")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()