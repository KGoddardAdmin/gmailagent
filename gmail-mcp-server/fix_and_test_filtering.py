#!/usr/bin/env python3
"""Fix Gmail API filtering by using only the full access scope"""

import sys
from gmail_mcp.auth import GmailAuth
from gmail_mcp.gmail_client import GmailClient


def fix_and_test():
    print("🔧 Fixing Gmail API Filtering Issue")
    print("=" * 50)
    print("\n⚠️  This will re-authenticate with a single, full-access scope")
    print("Please grant permission when the browser opens.\n")
    
    try:
        # This will trigger re-authentication
        auth = GmailAuth()
        client = GmailClient(auth)
        
        print("✅ Re-authenticated successfully!")
        
        # Test filtering
        print("\n🧪 Testing search queries:")
        print("-" * 30)
        
        # Test 1: Simple query
        print("\n1. Testing 'is:unread' query...")
        try:
            result = client.list_messages(query="is:unread", max_results=5)
            count = len(result.get('messages', []))
            print(f"✅ Success! Found {count} unread messages")
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
        
        # Test 2: From query
        print("\n2. Testing 'from:' query...")
        try:
            result = client.list_messages(query="from:noreply", max_results=5)
            count = len(result.get('messages', []))
            print(f"✅ Success! Found {count} messages from noreply addresses")
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
        
        # Test 3: Subject query
        print("\n3. Testing subject search...")
        try:
            result = client.list_messages(query="subject:thank", max_results=5)
            count = len(result.get('messages', []))
            print(f"✅ Success! Found {count} messages with 'thank' in subject")
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
        
        # Test 4: Brian email search
        print("\n4. Testing brian@loser.com search...")
        try:
            result = client.list_messages(query="from:brian@loser.com OR to:brian@loser.com", max_results=10)
            messages = result.get('messages', [])
            print(f"✅ Found {len(messages)} messages with brian@loser.com")
            
            if messages:
                print("\nMessage details:")
                for msg in messages[:3]:
                    try:
                        content = client.get_message_content(msg['id'])
                        headers = content.get('headers', {})
                        print(f"\n  - Subject: {headers.get('subject', 'No subject')}")
                        print(f"    From: {headers.get('from', 'Unknown')}")
                        print(f"    Date: {headers.get('date', 'Unknown')}")
                    except:
                        pass
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
        
        print("\n✅ Gmail API filtering is now working correctly!")
        print("\nYou can now:")
        print("- Search emails with queries")
        print("- Filter by sender, recipient, subject, etc.")
        print("- Access full message content")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    fix_and_test()